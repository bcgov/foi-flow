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

func TestEndToEnd_PublishedRequestProducesCompleted(t *testing.T) {
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
	for _, b := range []string{"raw", "published"} {
		_, err := raw.CreateBucket(ctx, &s3sdk.CreateBucketInput{Bucket: aws.String(b)})
		if err != nil {
			t.Fatalf("create bucket %q: %v", b, err)
		}
	}
	seeds := map[string]string{
		"src/one.txt": "1",
		"src/two.txt": "22",
	}
	for k, v := range seeds {
		_, err := raw.PutObject(ctx, &s3sdk.PutObjectInput{
			Bucket: aws.String("raw"),
			Key:    aws.String(k),
			Body:   bytes.NewReader([]byte(v)),
		})
		if err != nil {
			t.Fatalf("put %q: %v", k, err)
		}
	}

	// --- Wire the consumer with the real S3 Client ---
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
	svc := pubpub.NewService(s3Client, s3Client, "", logger, pubpub.WithFileCopier(s3Client))
	sitemapWriter := sitemapping.NewWriter(s3Client, sitemapping.NewRequestRepo(pool), map[pub.Kind]sitemapping.Target{
		pub.KindOpenInfoSitemap: {
			Bucket:          "published",
			Prefix:          "sitemap/",
			PublicBaseURL:   "https://example.gov.bc.ca/openinfopub/sitemap/",
			IndexFileName:   "sitemap_index.xml",
			PageFilePattern: "sitemap_pages_%d.xml",
			PageLimit:       50000,
		},
	})
	normalizer := pubpub.NewCompletionAdapter(svc, sitemapWriter)

	val, err := pubpub.NewValidator(events.TypePublicationPublishRequested,
		[]string{"openinfo.enqueue.service"})
	if err != nil {
		t.Fatalf("validator: %v", err)
	}
	consumer := messaging.NewConsumer(messaging.ConsumerConfig{
		Stream:                events.TypePublicationPublishRequested,
		CompletedStream:       events.TypePublicationPublishCompleted,
		CompletedEventType:    events.TypePublicationPublishCompleted,
		Kind:                  pub.KindOpenInfo,
		Group:                 "g",
		Consumer:              "c1",
		ReadTimeout:           500 * time.Millisecond,
		HandlerTimeout:        5 * time.Second,
		MaxRetries:            5,
		PoisonRepeatThreshold: 3,
	}, broker, pubRepo, outRepo, normalizer, val)

	publisher := messaging.NewOutboxPublisher(outRepo, broker, 1000).WithInterval(100 * time.Millisecond)

	// --- Publish one inbound event pointing at the seeded source ---
	payload := json.RawMessage(`{
		"tenant_id":   "a7d9b2f1-4c3e-4e8b-9a21-1c2e8f7b9d10",
		"source":      {"bucket": "raw",       "prefix": "src/"},
		"destination": {"bucket": "published", "prefix": "dst/"},
		"axis_request_id": "HTH-2025-52023",
		"kind": "openinfo",
		"description": "A copy of briefing note",
		"published_date": "2026-02-03",
		"contributor": "Ministry of Health",
		"fees": 0,
		"applicant_type": "Interest Group"
	}`)
	in := events.Envelope{
		EventID:       "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d90",
		EventType:     events.TypePublicationPublishRequested,
		Timestamp:     time.Now().UTC(),
		SchemaVersion: events.SchemaVersionV1,
		CorrelationID: "req-e2e",
		Source:        "openinfo.enqueue.service",
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

	// Ensure the event actually reached 'completed', not just exhausted iterations.
	var finalCount int
	_ = pool.QueryRow(ctx, `SELECT count(*) FROM workflow_request WHERE state='completed'`).Scan(&finalCount)
	if finalCount != 1 {
		t.Fatalf("workflow_request never reached completed after polling loop")
	}

	// --- Assert the S3 copy actually happened ---
	for k, want := range map[string]string{
		"dst/one.txt": "1",
		"dst/two.txt": "22",
	} {
		got, err := raw.GetObject(ctx, &s3sdk.GetObjectInput{
			Bucket: aws.String("published"),
			Key:    aws.String(k),
		})
		if err != nil {
			t.Fatalf("get dst %q: %v", k, err)
		}
		body, _ := io.ReadAll(got.Body)
		_ = got.Body.Close()
		if string(body) != want {
			t.Errorf("%q = %q, want %q", k, body, want)
		}
	}
	assertS3ObjectContains(t, ctx, raw, "published", "sitemap/sitemap_index.xml", "sitemap_pages_1.xml")
	assertS3ObjectContains(t, ctx, raw, "published", "sitemap/sitemap_pages_1.xml", "dst/HTH-2025-52023.html")

	// --- Drain the outbox and read the completed event ---
	if err := broker.EnsureGroup(ctx, events.TypePublicationPublishCompleted, "g-out"); err != nil {
		t.Fatalf("ensure out group: %v", err)
	}
	if err := publisher.Drain(ctx); err != nil {
		t.Fatalf("Drain: %v", err)
	}
	got, err := broker.Read(ctx, events.TypePublicationPublishCompleted, "g-out", "c1", 2*time.Second)
	if err != nil {
		t.Fatalf("Read out: %v", err)
	}
	if got == nil {
		t.Fatal("no completed event arrived")
	}
	var outEnv events.Envelope
	if err := json.Unmarshal(got.Payload, &outEnv); err != nil {
		t.Fatalf("unmarshal out: %v", err)
	}
	if outEnv.EventType != events.TypePublicationPublishCompleted {
		t.Errorf("EventType = %q", outEnv.EventType)
	}
	assertCompletedPayload(t, outEnv.Payload, map[string]any{
		"public_url":        "/published/dst/HTH-2025-52023.html",
		"html_key":          "dst/HTH-2025-52023.html",
		"sitemap_index_key": "sitemap/sitemap_index.xml",
		"sitemap_page_key":  "sitemap/sitemap_pages_1.xml",
	})
}

func assertS3ObjectContains(t *testing.T, ctx context.Context, client *s3sdk.Client, bucket, key, want string) {
	t.Helper()
	got, err := client.GetObject(ctx, &s3sdk.GetObjectInput{
		Bucket: aws.String(bucket),
		Key:    aws.String(key),
	})
	if err != nil {
		t.Fatalf("get %s/%s: %v", bucket, key, err)
	}
	body, err := io.ReadAll(got.Body)
	_ = got.Body.Close()
	if err != nil {
		t.Fatalf("read %s/%s: %v", bucket, key, err)
	}
	if !bytes.Contains(body, []byte(want)) {
		t.Fatalf("%s/%s missing %q:\n%s", bucket, key, want, body)
	}
}

func assertCompletedPayload(t *testing.T, raw json.RawMessage, want map[string]any) {
	t.Helper()
	var payload map[string]any
	if err := json.Unmarshal(raw, &payload); err != nil {
		t.Fatalf("unmarshal completion payload: %v", err)
	}
	for key, expected := range want {
		if payload[key] != expected {
			t.Fatalf("%s = %#v, want %#v", key, payload[key], expected)
		}
	}
}
