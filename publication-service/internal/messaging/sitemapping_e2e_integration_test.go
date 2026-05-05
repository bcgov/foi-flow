//go:build integration

package messaging_test

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
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
	pubsm "publication-service/internal/publication/sitemapping"
	pub "publication-service/internal/publish"
	sitemapping "publication-service/internal/sitemapping"
	pgkg "publication-service/internal/storage/postgres"
	pubs3 "publication-service/internal/storage/s3"
)

type sitemapHarness struct {
	ctx      context.Context
	pool     *pgxpool.Pool
	broker   *redisstream.Broker
	rawS3    *s3sdk.Client
	s3Client *pubs3.Client
}

func setupSitemapHarness(t *testing.T) sitemapHarness {
	t.Helper()
	ctx, cancel := context.WithTimeout(context.Background(), 120*time.Second)
	t.Cleanup(cancel)

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
	dsn, err := pgC.ConnectionString(ctx, "sslmode=disable")
	if err != nil {
		t.Fatalf("postgres dsn: %v", err)
	}
	if err := pgkg.Migrate(ctx, dsn); err != nil {
		t.Fatalf("migrate: %v", err)
	}
	pool, err := pgxpool.New(ctx, dsn)
	if err != nil {
		t.Fatalf("pool: %v", err)
	}
	t.Cleanup(pool.Close)

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
	broker, err := redisstream.New(redisstream.Options{Addr: redisAddr})
	if err != nil {
		t.Fatalf("broker: %v", err)
	}
	t.Cleanup(func() { _ = broker.Close() })

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
	host, err := swC.Host(ctx)
	if err != nil {
		t.Fatalf("seaweedfs host: %v", err)
	}
	port, err := swC.MappedPort(ctx, "8333/tcp")
	if err != nil {
		t.Fatalf("seaweedfs port: %v", err)
	}
	endpoint := fmt.Sprintf("http://%s:%s", host, port.Port())
	awsCfg, err := awsconfig.LoadDefaultConfig(ctx,
		awsconfig.WithRegion("us-east-1"),
		awsconfig.WithCredentialsProvider(credentials.NewStaticCredentialsProvider("test-key", "test-secret", "")),
	)
	if err != nil {
		t.Fatalf("aws cfg: %v", err)
	}
	raw := s3sdk.NewFromConfig(awsCfg, func(o *s3sdk.Options) {
		o.BaseEndpoint = &endpoint
		o.UsePathStyle = true
	})
	for _, bucket := range []string{"published", "pd-published"} {
		if _, err := raw.CreateBucket(ctx, &s3sdk.CreateBucketInput{Bucket: aws.String(bucket)}); err != nil {
			t.Fatalf("create bucket %q: %v", bucket, err)
		}
	}
	client, err := pubs3.NewClient(config.S3Config{
		Endpoint:        endpoint,
		Region:          "us-east-1",
		AccessKeyID:     "test-key",
		SecretAccessKey: "test-secret",
		UsePathStyle:    true,
		RequestTimeout:  10 * time.Second,
	})
	if err != nil {
		t.Fatalf("s3 client: %v", err)
	}
	return sitemapHarness{ctx: ctx, pool: pool, broker: broker, rawS3: raw, s3Client: client}
}

func sitemapWriter(h sitemapHarness) *sitemapping.Writer {
	return sitemapping.NewWriter(h.s3Client, sitemapping.NewRequestRepo(h.pool), map[pub.Kind]sitemapping.Target{
		pub.KindOpenInfoSitemap: {
			Bucket:          "published",
			Prefix:          "openinfopub/sitemap/",
			PublicBaseURL:   "https://example.gov.bc.ca/openinfopub/sitemap/",
			IndexFileName:   "sitemap_index.xml",
			PageFilePattern: "sitemap_pages_%d.xml",
			PageLimit:       50000,
		},
		pub.KindProactiveDisclosureSitemap: {
			Bucket:          "pd-published",
			Prefix:          "proactivedisclosurepub/sitemap/",
			PublicBaseURL:   "https://example.gov.bc.ca/proactivedisclosurepub/sitemap/",
			IndexFileName:   "sitemap_index.xml",
			PageFilePattern: "sitemap_pages_%d.xml",
			PageLimit:       50000,
		},
	})
}

func TestSitemapping_OpenInfoE2E(t *testing.T) {
	h := setupSitemapHarness(t)
	writer := sitemapWriter(h)
	consumer := newSitemapConsumer(t, h, writer, "openinfo.workflow.service")
	outRepo := messaging.NewOutboxRepo(h.pool)
	publisher := messaging.NewOutboxPublisher(outRepo, h.broker, 1000)

	publicURL := "https://example.gov.bc.ca/openinfopub/packages/HTH-2025-52023/openinfo/HTH-2025-52023.html"
	publishSitemapEnvelope(t, h, "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d92", "oi-map-e2e", "openinfo.workflow.service", publicURL, "openinfo")
	waitForSitemapCompleted(t, h, consumer)

	assertWorkflowResult(t, h, pub.KindOpenInfoSitemap, "HTH-2025-52023:v1")
	assertObjectContains(t, h, "published", "openinfopub/sitemap/sitemap_index.xml", "sitemap_pages_1.xml")
	assertObjectContains(t, h, "published", "openinfopub/sitemap/sitemap_pages_1.xml", publicURL)
	assertCompletedEvent(t, h, publisher, events.TypePublicationSitemappingCompleted)
}

func TestSitemapping_ProactiveDisclosureE2E(t *testing.T) {
	h := setupSitemapHarness(t)
	writer := sitemapWriter(h)
	consumer := newSitemapConsumer(t, h, writer, "proactivedisclosure.workflow.service")
	outRepo := messaging.NewOutboxRepo(h.pool)
	publisher := messaging.NewOutboxPublisher(outRepo, h.broker, 1000)

	publicURL := "https://example.gov.bc.ca/proactivedisclosurepub/packages/PD-2026-001/openinfo/PD-2026-001.html"
	publishSitemapEnvelope(t, h, "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d93", "pd-map-e2e", "proactivedisclosure.workflow.service", publicURL, "proactivedisclosure")
	waitForSitemapCompleted(t, h, consumer)

	assertWorkflowResult(t, h, pub.KindProactiveDisclosureSitemap, "PD-2026-001:v1")
	assertObjectContains(t, h, "pd-published", "proactivedisclosurepub/sitemap/sitemap_index.xml", "sitemap_pages_1.xml")
	assertObjectContains(t, h, "pd-published", "proactivedisclosurepub/sitemap/sitemap_pages_1.xml", publicURL)
	assertCompletedEvent(t, h, publisher, events.TypePublicationSitemappingCompleted)
}

func TestSitemapping_IdempotentDuplicateRequest(t *testing.T) {
	h := setupSitemapHarness(t)
	writer := sitemapWriter(h)
	consumer := newSitemapConsumer(t, h, writer, "openinfo.workflow.service")
	publicURL := "https://example.gov.bc.ca/openinfopub/packages/HTH-2025-52023/openinfo/HTH-2025-52023.html"

	publishSitemapEnvelope(t, h, "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d92", "oi-map-e2e-1", "openinfo.workflow.service", publicURL, "openinfo")
	waitForSitemapCompleted(t, h, consumer)
	publishSitemapEnvelope(t, h, "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d94", "oi-map-e2e-2", "openinfo.workflow.service", publicURL, "openinfo")
	if err := consumer.Step(h.ctx); err != nil {
		t.Fatalf("second Step: %v", err)
	}

	var rows int
	if err := h.pool.QueryRow(h.ctx,
		`SELECT count(*) FROM workflow_request WHERE kind=$1 AND payload->>'publication_id'=$2`,
		string(pub.KindOpenInfoSitemap), "HTH-2025-52023:v1",
	).Scan(&rows); err != nil {
		t.Fatalf("count workflow rows: %v", err)
	}
	if rows != 1 {
		t.Fatalf("workflow rows = %d, want 1", rows)
	}
	page := readObject(t, h, "published", "openinfopub/sitemap/sitemap_pages_1.xml")
	if got := bytes.Count(page, []byte(publicURL)); got != 1 {
		t.Fatalf("public URL count = %d, want 1\n%s", got, page)
	}
}

func newSitemapConsumer(t *testing.T, h sitemapHarness, writer *sitemapping.Writer, source string) *messaging.Consumer {
	t.Helper()
	if err := h.broker.EnsureGroup(h.ctx, events.TypePublicationSitemappingRequested, "g"); err != nil {
		t.Fatalf("ensure group: %v", err)
	}
	val, err := pubsm.NewValidator([]string{source})
	if err != nil {
		t.Fatalf("validator: %v", err)
	}
	kind := pub.KindOpenInfoSitemap
	if source == "proactivedisclosure.workflow.service" {
		kind = pub.KindProactiveDisclosureSitemap
	}
	return messaging.NewConsumer(messaging.ConsumerConfig{
		Stream:                events.TypePublicationSitemappingRequested,
		CompletedStream:       events.TypePublicationSitemappingCompleted,
		CompletedEventType:    events.TypePublicationSitemappingCompleted,
		Kind:                  kind,
		Group:                 "g",
		Consumer:              "c1",
		ReadTimeout:           500 * time.Millisecond,
		HandlerTimeout:        5 * time.Second,
		MaxRetries:            5,
		PoisonRepeatThreshold: 3,
	}, h.broker, pub.NewRepo(h.pool), messaging.NewOutboxRepo(h.pool), pubsm.NewNormalizerAdapter(writer), val)
}

func publishSitemapEnvelope(t *testing.T, h sitemapHarness, eventID, correlationID, source, publicURL, kind string) {
	t.Helper()
	publicationID := "HTH-2025-52023:v1"
	ref := "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d90"
	if kind == "proactivedisclosure" {
		publicationID = "PD-2026-001:v1"
		ref = "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d91"
	}
	payload, err := json.Marshal(map[string]string{
		"tenant_id":              "a7d9b2f1-4c3e-4e8b-9a21-1c2e8f7b9d10",
		"publication_id":         publicationID,
		"public_url":             publicURL,
		"last_modified":          "2026-04-01",
		"publication_result_ref": ref,
		"kind":                   kind,
	})
	if err != nil {
		t.Fatalf("payload marshal: %v", err)
	}
	env := events.Envelope{
		EventID:       eventID,
		EventType:     events.TypePublicationSitemappingRequested,
		Timestamp:     time.Now().UTC(),
		SchemaVersion: events.SchemaVersionV1,
		CorrelationID: correlationID,
		Source:        source,
		Payload:       payload,
		Meta:          events.Meta{FirstSeenAt: time.Now().UTC()},
	}
	b, err := json.Marshal(env)
	if err != nil {
		t.Fatalf("envelope marshal: %v", err)
	}
	if _, err := h.broker.Publish(h.ctx, events.TypePublicationSitemappingRequested, b, 1000); err != nil {
		t.Fatalf("publish: %v", err)
	}
}

func waitForSitemapCompleted(t *testing.T, h sitemapHarness, consumer *messaging.Consumer) {
	t.Helper()
	for i := 0; i < 100; i++ {
		if err := consumer.Step(h.ctx); err != nil {
			t.Fatalf("Step: %v", err)
		}
		var completedCount int
		if err := h.pool.QueryRow(h.ctx,
			`SELECT count(*) FROM workflow_request WHERE state='completed'`,
		).Scan(&completedCount); err != nil {
			t.Fatalf("count completed: %v", err)
		}
		if completedCount == 1 {
			return
		}
		time.Sleep(20 * time.Millisecond)
	}
	t.Fatal("workflow_request never reached completed")
}

func assertWorkflowResult(t *testing.T, h sitemapHarness, kind pub.Kind, publicationID string) {
	t.Helper()
	var raw []byte
	if err := h.pool.QueryRow(h.ctx,
		`SELECT result FROM workflow_request WHERE state='completed' AND kind=$1 AND payload->>'publication_id'=$2`,
		string(kind), publicationID,
	).Scan(&raw); err != nil {
		t.Fatalf("query workflow result: %v", err)
	}
	var result map[string]any
	if err := json.Unmarshal(raw, &result); err != nil {
		t.Fatalf("unmarshal workflow result: %v", err)
	}
	if result["result"] != "written" {
		t.Fatalf("workflow result status = %v, raw: %s", result["result"], raw)
	}
}

func assertObjectContains(t *testing.T, h sitemapHarness, bucket, key, want string) {
	t.Helper()
	body := readObject(t, h, bucket, key)
	if !bytes.Contains(body, []byte(want)) {
		t.Fatalf("%s/%s missing %q:\n%s", bucket, key, want, body)
	}
}

func readObject(t *testing.T, h sitemapHarness, bucket, key string) []byte {
	t.Helper()
	got, err := h.rawS3.GetObject(h.ctx, &s3sdk.GetObjectInput{
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
	return body
}

func assertCompletedEvent(t *testing.T, h sitemapHarness, publisher *messaging.OutboxPublisher, eventType string) {
	t.Helper()
	if err := h.broker.EnsureGroup(h.ctx, eventType, "g-out"); err != nil {
		t.Fatalf("ensure out group: %v", err)
	}
	if err := publisher.Drain(h.ctx); err != nil {
		t.Fatalf("Drain: %v", err)
	}
	got, err := h.broker.Read(h.ctx, eventType, "g-out", "c1", 2*time.Second)
	if err != nil {
		t.Fatalf("Read out: %v", err)
	}
	if got == nil {
		t.Fatal("no completed event arrived")
	}
	var out events.Envelope
	if err := json.Unmarshal(got.Payload, &out); err != nil {
		t.Fatalf("unmarshal out: %v", err)
	}
	if out.EventType != eventType {
		t.Fatalf("EventType = %q, want %q", out.EventType, eventType)
	}
}
