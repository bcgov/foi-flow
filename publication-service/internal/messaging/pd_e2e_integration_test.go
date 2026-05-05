//go:build integration

package messaging_test

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"log/slog"
	"strings"
	"testing"
	"time"

	"github.com/aws/aws-sdk-go-v2/aws"
	awsconfig "github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/credentials"
	s3sdk "github.com/aws/aws-sdk-go-v2/service/s3"
	"github.com/jackc/pgx/v5/pgxpool"
	tc "github.com/testcontainers/testcontainers-go"
	tcpostgres "github.com/testcontainers/testcontainers-go/modules/postgres"
	tcredis "github.com/testcontainers/testcontainers-go/modules/redis"
	"github.com/testcontainers/testcontainers-go/wait"

	"publication-service/internal/config"
	"publication-service/internal/events"
	"publication-service/internal/messaging"
	"publication-service/internal/messaging/redisstream"
	pubpub "publication-service/internal/publication/publish"
	pub "publication-service/internal/publish"
	sitemapping "publication-service/internal/sitemapping"
	pgkg "publication-service/internal/storage/postgres"
	pubs3 "publication-service/internal/storage/s3"
)

func TestEndToEnd_PD_PublishedRequestProducesCompleted(t *testing.T) {
	ctx, cancel := context.WithTimeout(context.Background(), 120*time.Second)
	defer cancel()

	// --- Postgres ---
	pgC, err := tcpostgres.Run(ctx, "postgres:16-alpine",
		tcpostgres.WithDatabase("foi"),
		tcpostgres.WithUsername("foi"),
		tcpostgres.WithPassword("foi"),
		tcpostgres.BasicWaitStrategies(),
	)
	if err != nil {
		t.Fatalf("postgres: %v", err)
	}
	t.Cleanup(func() { _ = pgC.Terminate(context.Background()) })
	dsn, _ := pgC.ConnectionString(ctx, "sslmode=disable")
	if err := pgkg.Migrate(ctx, dsn); err != nil {
		t.Fatalf("migrate: %v", err)
	}
	pool, err := pgxpool.New(ctx, dsn)
	if err != nil {
		t.Fatalf("pool: %v", err)
	}
	t.Cleanup(pool.Close)

	// --- Redis ---
	rC, err := tcredis.Run(ctx, "redis:7-alpine")
	if err != nil {
		t.Fatalf("redis: %v", err)
	}
	t.Cleanup(func() { _ = rC.Terminate(context.Background()) })
	redisAddr, err := rC.ConnectionString(ctx)
	if err != nil {
		t.Fatalf("redis addr: %v", err)
	}
	redisAddr = strings.TrimPrefix(redisAddr, "redis://")

	// --- SeaweedFS ---
	swC, err := tc.GenericContainer(ctx, tc.GenericContainerRequest{
		ContainerRequest: tc.ContainerRequest{
			Image:        "chrislusf/seaweedfs:3.72",
			Cmd:          []string{"server", "-s3"},
			ExposedPorts: []string{"8333/tcp"},
			WaitingFor: wait.ForHTTP("/").
				WithPort("8333/tcp").
				WithStatusCodeMatcher(func(status int) bool { return status < 500 }).
				WithStartupTimeout(60 * time.Second),
		},
		Started: true,
	})
	if err != nil {
		t.Fatalf("seaweedfs: %v", err)
	}
	t.Cleanup(func() { _ = swC.Terminate(context.Background()) })
	swHost, err := swC.Host(ctx)
	if err != nil {
		t.Fatalf("seaweedfs host: %v", err)
	}
	swPort, err := swC.MappedPort(ctx, "8333/tcp")
	if err != nil {
		t.Fatalf("seaweedfs port: %v", err)
	}
	s3Endpoint := fmt.Sprintf("http://%s:%s", swHost, swPort.Port())

	// Seed source bucket and destination bucket; put 2 objects under src/.
	awsCfg, err := awsconfig.LoadDefaultConfig(ctx,
		awsconfig.WithRegion("us-east-1"),
		awsconfig.WithCredentialsProvider(credentials.NewStaticCredentialsProvider(
			"test-key", "test-secret", "")),
	)
	if err != nil {
		t.Fatalf("aws cfg: %v", err)
	}
	raw := s3sdk.NewFromConfig(awsCfg, func(o *s3sdk.Options) {
		o.BaseEndpoint = &s3Endpoint
		o.UsePathStyle = true
	})
	for _, b := range []string{"pd-raw", "pd-published"} {
		_, err := raw.CreateBucket(ctx, &s3sdk.CreateBucketInput{Bucket: aws.String(b)})
		if err != nil {
			t.Fatalf("create bucket %q: %v", b, err)
		}
	}
	seeds := map[string]string{
		"in/pd1/report.pdf": "pdf-content",
		"in/pd1/letter.txt": "letter-content",
	}
	for k, v := range seeds {
		_, err := raw.PutObject(ctx, &s3sdk.PutObjectInput{
			Bucket: aws.String("pd-raw"),
			Key:    aws.String(k),
			Body:   bytes.NewReader([]byte(v)),
		})
		if err != nil {
			t.Fatalf("put %q: %v", k, err)
		}
	}

	// --- Wire the PD consumer with the real S3 Client ---
	broker, err := redisstream.New(redisstream.Options{Addr: redisAddr})
	if err != nil {
		t.Fatalf("broker: %v", err)
	}
	t.Cleanup(func() { _ = broker.Close() })

	if err := broker.EnsureGroup(ctx, events.TypePublicationPublishRequested, "g"); err != nil {
		t.Fatalf("ensure group: %v", err)
	}

	pubRepo := pub.NewRepo(pool)
	outRepo := messaging.NewOutboxRepo(pool)

	s3Client, err := pubs3.NewClient(config.S3Config{
		Endpoint:        s3Endpoint,
		Region:          "us-east-1",
		AccessKeyID:     "test-key",
		SecretAccessKey: "test-secret",
		UsePathStyle:    true,
		RequestTimeout:  10 * time.Second,
	})
	if err != nil {
		t.Fatalf("s3 client: %v", err)
	}
	logger := slog.New(slog.NewTextHandler(io.Discard, nil))
	svc := pubpub.NewService(s3Client, s3Client, "", logger)
	sitemapWriter := sitemapping.NewWriter(s3Client, sitemapping.NewRequestRepo(pool), map[pub.Kind]sitemapping.Target{
		pub.KindProactiveDisclosureSitemap: {
			Bucket:          "pd-published",
			Prefix:          "sitemap/",
			PublicBaseURL:   "https://example.gov.bc.ca/proactivedisclosurepub/sitemap/",
			IndexFileName:   "sitemap_index.xml",
			PageFilePattern: "sitemap_pages_%d.xml",
			PageLimit:       50000,
		},
	})
	normalizer := pubpub.NewCompletionAdapter(svc, sitemapWriter)

	val, err := pubpub.NewValidator(events.TypePublicationPublishRequested,
		[]string{"proactivedisclosure.enqueue.service"})
	if err != nil {
		t.Fatalf("validator: %v", err)
	}
	consumer := messaging.NewConsumer(messaging.ConsumerConfig{
		Stream:                events.TypePublicationPublishRequested,
		CompletedStream:       events.TypePublicationPublishCompleted,
		CompletedEventType:    events.TypePublicationPublishCompleted,
		Kind:                  pub.KindProactiveDisclosure,
		Group:                 "g",
		Consumer:              "c1",
		ReadTimeout:           500 * time.Millisecond,
		HandlerTimeout:        5 * time.Second,
		MaxRetries:            5,
		PoisonRepeatThreshold: 3,
	}, broker, pubRepo, outRepo, normalizer, val)

	publisher := messaging.NewOutboxPublisher(outRepo, broker, 1000).WithInterval(100 * time.Millisecond)

	// --- Publish one inbound PD event pointing at the seeded source ---
	payload := json.RawMessage(`{
		"tenant_id":                    "a7d9b2f1-4c3e-4e8b-9a21-1c2e8f7b9d10",
		"source":                       {"bucket": "pd-raw",       "prefix": "in/pd1/"},
		"destination":                  {"bucket": "pd-published", "prefix": "out/pd1/"},
		"axis_request_id":              "PD-2026-001",
		"kind":                         "proactivedisclosure",
		"description":                  "Quarterly travel expenses",
		"published_date":               "2026-04-01",
		"contributor":                  "Ministry of Transportation",
		"fees":                         0,
		"applicant_type":               null,
		"proactivedisclosure_category": "Travel Expenses",
		"report_period":                "2026-Q1"
	}`)
	in := events.Envelope{
		EventID:       "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d95",
		EventType:     events.TypePublicationPublishRequested,
		Timestamp:     time.Now().UTC(),
		SchemaVersion: events.SchemaVersionV1,
		CorrelationID: "pd-req-e2e",
		Source:        "proactivedisclosure.enqueue.service",
		Payload:       payload,
		Meta:          events.Meta{FirstSeenAt: time.Now().UTC()},
	}
	b, _ := json.Marshal(in)
	if _, err := broker.Publish(ctx, events.TypePublicationPublishRequested, b, 1000); err != nil {
		t.Fatalf("seed publish: %v", err)
	}

	// Step the consumer until the row reaches 'completed'.
	for i := 0; i < 100; i++ {
		if err := consumer.Step(ctx); err != nil {
			t.Fatalf("Step: %v", err)
		}
		var completedCount int
		_ = pool.QueryRow(ctx,
			`SELECT count(*) FROM workflow_request WHERE state='completed'`).Scan(&completedCount)
		if completedCount == 1 {
			break
		}
		time.Sleep(20 * time.Millisecond)
	}

	var finalCount int
	_ = pool.QueryRow(ctx, `SELECT count(*) FROM workflow_request WHERE state='completed'`).Scan(&finalCount)
	if finalCount != 1 {
		t.Fatalf("workflow_request never reached completed after polling loop")
	}

	// --- Assert HTML index was uploaded with PD meta tags ---
	htmlKey := "out/pd1/PD-2026-001.html"
	got, err := raw.GetObject(ctx, &s3sdk.GetObjectInput{
		Bucket: aws.String("pd-published"),
		Key:    aws.String(htmlKey),
	})
	if err != nil {
		t.Fatalf("get HTML %q: %v", htmlKey, err)
	}
	htmlBytes, _ := io.ReadAll(got.Body)
	_ = got.Body.Close()

	if !bytes.Contains(htmlBytes, []byte(`name="proactivedisclosure.category"`)) {
		t.Errorf("HTML missing proactivedisclosure.category meta tag:\n%s", htmlBytes)
	}
	if !bytes.Contains(htmlBytes, []byte("Travel Expenses")) {
		t.Errorf("HTML missing category content 'Travel Expenses':\n%s", htmlBytes)
	}
	if !bytes.Contains(htmlBytes, []byte(`name="proactivedisclosure.report_period"`)) {
		t.Errorf("HTML missing proactivedisclosure.report_period meta tag:\n%s", htmlBytes)
	}
	if !bytes.Contains(htmlBytes, []byte("2026-Q1")) {
		t.Errorf("HTML missing report_period content '2026-Q1':\n%s", htmlBytes)
	}
	assertS3ObjectContains(t, ctx, raw, "pd-published", "sitemap/sitemap_index.xml", "sitemap_pages_1.xml")
	assertS3ObjectContains(t, ctx, raw, "pd-published", "sitemap/sitemap_pages_1.xml", "out/pd1/PD-2026-001.html")

	// --- Drain the outbox and read the completed event ---
	if err := broker.EnsureGroup(ctx, events.TypePublicationPublishCompleted, "g-out"); err != nil {
		t.Fatalf("ensure out group: %v", err)
	}
	if err := publisher.Drain(ctx); err != nil {
		t.Fatalf("Drain: %v", err)
	}
	outMsg, err := broker.Read(ctx, events.TypePublicationPublishCompleted, "g-out", "c1", 2*time.Second)
	if err != nil {
		t.Fatalf("Read out: %v", err)
	}
	if outMsg == nil {
		t.Fatal("no completed event arrived")
	}
	var outEnv events.Envelope
	if err := json.Unmarshal(outMsg.Payload, &outEnv); err != nil {
		t.Fatalf("unmarshal out: %v", err)
	}
	if outEnv.EventType != events.TypePublicationPublishCompleted {
		t.Errorf("EventType = %q, want %q", outEnv.EventType, events.TypePublicationPublishCompleted)
	}
	assertCompletedPayload(t, outEnv.Payload, map[string]any{
		"public_url":        "/pd-published/out/pd1/PD-2026-001.html",
		"html_key":          "out/pd1/PD-2026-001.html",
		"sitemap_index_key": "sitemap/sitemap_index.xml",
		"sitemap_page_key":  "sitemap/sitemap_pages_1.xml",
	})
}
