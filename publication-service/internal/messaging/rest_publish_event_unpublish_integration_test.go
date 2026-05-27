//go:build integration

package messaging_test

import (
	"bytes"
	"context"
	"encoding/json"
	"io"
	"log/slog"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/aws/aws-sdk-go-v2/aws"
	s3sdk "github.com/aws/aws-sdk-go-v2/service/s3"

	"publication-service/internal/events"
	"publication-service/internal/http/handlers"
	"publication-service/internal/messaging"
	pubpub "publication-service/internal/publication/publish"
	pubunpub "publication-service/internal/publication/unpublish"
	pub "publication-service/internal/publish"
	"publication-service/internal/publishnow"
	"publication-service/internal/sitemapping"
	sharedunpublish "publication-service/internal/unpublish"
)

func TestRestPublishEventUnpublishRestRepublishCopiesFilesAndUpdatesSitemap(t *testing.T) {
	h := setupSitemapHarness(t)
	ctx := h.ctx

	createBucket(t, ctx, h.rawS3, "raw")
	putObject(t, ctx, h.rawS3, "raw", "src/a/response letter.pdf", "letter")
	putObject(t, ctx, h.rawS3, "raw", "src/a/package.json", `{"ok":true}`)

	publishHandler := newRESTPublishHandler(t, h)

	first := postPublication(t, publishHandler, restPublishBody())
	assertS3ObjectContains(t, ctx, h.rawS3, "published", "dst/a/response_letter.pdf", "letter")
	assertS3ObjectContains(t, ctx, h.rawS3, "published", "dst/a/package.json", `{"ok":true}`)
	assertS3ObjectContains(t, ctx, h.rawS3, "published", "dst/a/HTH-2025-52023.html", "HTH-2025-52023")
	assertObjectContains(t, h, "published", "openinfopub/sitemap/sitemap_pages_1.xml", first.PublicURL)

	unpublishConsumer := newUnpublishConsumer(t, h)
	publishUnpublishEnvelope(t, h, first.PublicURL)
	waitForCompletedWorkflowKind(t, h, unpublishConsumer, pub.KindOpenInfoUnpublish)
	assertObjectDoesNotExist(t, ctx, h.rawS3, "published", "dst/a/HTH-2025-52023.html")
	assertS3ObjectMissingText(t, ctx, h.rawS3, "published", "openinfopub/sitemap/sitemap_pages_1.xml", first.PublicURL)

	second := postPublication(t, publishHandler, restPublishBody())
	if second.PublicURL != first.PublicURL {
		t.Fatalf("republished public URL = %q, want %q", second.PublicURL, first.PublicURL)
	}
	assertS3ObjectContains(t, ctx, h.rawS3, "published", "dst/a/response_letter.pdf", "letter")
	assertS3ObjectContains(t, ctx, h.rawS3, "published", "dst/a/package.json", `{"ok":true}`)
	assertS3ObjectContains(t, ctx, h.rawS3, "published", "dst/a/HTH-2025-52023.html", "HTH-2025-52023")
	assertObjectContains(t, h, "published", "openinfopub/sitemap/sitemap_pages_1.xml", second.PublicURL)
}

func newRESTPublishHandler(t *testing.T, h sitemapHarness) http.Handler {
	t.Helper()
	logger := slog.New(slog.NewTextHandler(io.Discard, nil))
	pubService, err := pubpub.NewService(
		h.s3Client,
		h.s3Client,
		"https://objects.example",
		logger,
		pubpub.WithFileCopier(h.s3Client),
		pubpub.WithDeleter(h.s3Client),
	)
	if err != nil {
		t.Fatalf("publish service: %v", err)
	}
	orchestrator := publishnow.New(pubService, publishCycleSitemapWriter(h)).
		WithSitemapClaimer(pub.NewRepo(h.pool))
	return handlers.Publications(orchestrator)
}

func publishCycleSitemapWriter(h sitemapHarness) *sitemapping.Writer {
	target := sitemapping.Target{
		Bucket:          "published",
		Prefix:          "openinfopub/sitemap/",
		PublicBaseURL:   "https://example.gov.bc.ca/openinfopub/sitemap/",
		IndexFileName:   "sitemap_index.xml",
		PageFilePattern: "sitemap_pages_%d.xml",
		PageLimit:       50000,
	}
	return sitemapping.NewWriter(h.s3Client, sitemapping.NewRequestRepo(h.pool), map[pub.Kind]sitemapping.Target{
		pub.KindOpenInfoSitemap:              target,
		pub.KindProactiveDisclosureSitemap:   target,
		pub.KindOpenInfoUnpublish:            target,
		pub.KindProactiveDisclosureUnpublish: target,
	})
}

func postPublication(t *testing.T, handler http.Handler, body []byte) publishnow.Response {
	t.Helper()
	rec := httptest.NewRecorder()
	req := httptest.NewRequest(http.MethodPost, "/publications", bytes.NewReader(body))
	handler.ServeHTTP(rec, req)
	if rec.Code != http.StatusOK {
		t.Fatalf("POST /publications status = %d, want %d; body=%s", rec.Code, http.StatusOK, rec.Body.String())
	}
	var resp publishnow.Response
	if err := json.Unmarshal(rec.Body.Bytes(), &resp); err != nil {
		t.Fatalf("decode publication response: %v", err)
	}
	return resp
}

func restPublishBody() []byte {
	payload := map[string]any{
		"tenant_id":       "a7d9b2f1-4c3e-4e8b-9a21-1c2e8f7b9d10",
		"kind":            "openinfo",
		"axis_request_id": "HTH-2025-52023",
		"description":     "A briefing note",
		"published_date":  "2026-02-03",
		"contributor":     "Ministry of Health",
		"fees":            0,
		"applicant_type":  "Interest Group",
		"source":          map[string]any{"bucket": "raw", "prefix": "src/a/"},
		"destination":     map[string]any{"bucket": "published", "prefix": "dst/a/"},
	}
	body, err := json.Marshal(map[string]any{
		"publication_type": "openinfo",
		"payload":          payload,
	})
	if err != nil {
		panic(err)
	}
	return body
}

func newUnpublishConsumer(t *testing.T, h sitemapHarness) *messaging.Consumer {
	t.Helper()
	if err := h.broker.EnsureGroup(h.ctx, events.TypePublicationUnpublishRequested, "unpublish-g"); err != nil {
		t.Fatalf("ensure unpublish group: %v", err)
	}
	unpublishService := sharedunpublish.NewService(
		h.s3Client,
		publishCycleSitemapWriter(h),
		sharedunpublish.NewRequestRepo(h.pool),
	)
	validator, err := pubunpub.NewValidator([]string{"openinfo.workflow.service"})
	if err != nil {
		t.Fatalf("unpublish validator: %v", err)
	}
	return messaging.NewConsumer(messaging.ConsumerConfig{
		Stream:                events.TypePublicationUnpublishRequested,
		CompletedStream:       events.TypePublicationUnpublishCompleted,
		CompletedEventType:    events.TypePublicationUnpublishCompleted,
		Kind:                  pub.KindOpenInfoUnpublish,
		Group:                 "unpublish-g",
		Consumer:              "unpublish-c1",
		ReadTimeout:           500 * time.Millisecond,
		HandlerTimeout:        5 * time.Second,
		MaxRetries:            5,
		PoisonRepeatThreshold: 3,
	}, h.broker, pub.NewRepo(h.pool), messaging.NewOutboxRepo(h.pool), pubunpub.NewNormalizerAdapter(unpublishService), validator)
}

func publishUnpublishEnvelope(t *testing.T, h sitemapHarness, publicURL string) {
	t.Helper()
	payload, err := json.Marshal(map[string]any{
		"tenant_id":      "a7d9b2f1-4c3e-4e8b-9a21-1c2e8f7b9d10",
		"publication_id": "HTH-2025-52023",
		"public_url":     publicURL,
		"public_repository": map[string]string{
			"bucket": "published",
			"prefix": "dst/a/",
		},
		"last_modified": "2026-02-03",
		"kind":          "openinfo",
	})
	if err != nil {
		t.Fatalf("unpublish payload: %v", err)
	}
	env := events.Envelope{
		EventID:       "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d95",
		EventType:     events.TypePublicationUnpublishRequested,
		Timestamp:     time.Now().UTC(),
		SchemaVersion: events.SchemaVersionV1,
		CorrelationID: "rest-publish-event-unpublish",
		Source:        "openinfo.workflow.service",
		Payload:       payload,
		Meta:          events.Meta{FirstSeenAt: time.Now().UTC()},
	}
	b, err := json.Marshal(env)
	if err != nil {
		t.Fatalf("unpublish envelope: %v", err)
	}
	if _, err := h.broker.Publish(h.ctx, events.TypePublicationUnpublishRequested, b, 1000); err != nil {
		t.Fatalf("publish unpublish event: %v", err)
	}
}

func waitForCompletedWorkflowKind(t *testing.T, h sitemapHarness, consumer *messaging.Consumer, kind pub.Kind) {
	t.Helper()
	for i := 0; i < 100; i++ {
		if err := consumer.Step(h.ctx); err != nil {
			t.Fatalf("unpublish Step: %v", err)
		}
		var completedCount int
		if err := h.pool.QueryRow(h.ctx,
			`SELECT count(*) FROM workflow_request WHERE state='completed' AND kind=$1`,
			string(kind),
		).Scan(&completedCount); err != nil {
			t.Fatalf("count completed %s workflows: %v", kind, err)
		}
		if completedCount == 1 {
			return
		}
		time.Sleep(20 * time.Millisecond)
	}
	t.Fatalf("workflow_request kind %s never reached completed", kind)
}

func createBucket(t *testing.T, ctx context.Context, client *s3sdk.Client, bucket string) {
	t.Helper()
	if _, err := client.CreateBucket(ctx, &s3sdk.CreateBucketInput{Bucket: aws.String(bucket)}); err != nil {
		t.Fatalf("create bucket %q: %v", bucket, err)
	}
}

func putObject(t *testing.T, ctx context.Context, client *s3sdk.Client, bucket, key, body string) {
	t.Helper()
	if _, err := client.PutObject(ctx, &s3sdk.PutObjectInput{
		Bucket: aws.String(bucket),
		Key:    aws.String(key),
		Body:   bytes.NewReader([]byte(body)),
	}); err != nil {
		t.Fatalf("put %s/%s: %v", bucket, key, err)
	}
}

func assertObjectDoesNotExist(t *testing.T, ctx context.Context, client *s3sdk.Client, bucket, key string) {
	t.Helper()
	_, err := client.GetObject(ctx, &s3sdk.GetObjectInput{
		Bucket: aws.String(bucket),
		Key:    aws.String(key),
	})
	if err == nil {
		t.Fatalf("%s/%s exists, want deleted", bucket, key)
	}
}

func assertS3ObjectMissingText(t *testing.T, ctx context.Context, client *s3sdk.Client, bucket, key, text string) {
	t.Helper()
	got, err := client.GetObject(ctx, &s3sdk.GetObjectInput{
		Bucket: aws.String(bucket),
		Key:    aws.String(key),
	})
	if err != nil {
		return
	}
	body, err := io.ReadAll(got.Body)
	_ = got.Body.Close()
	if err != nil {
		t.Fatalf("read %s/%s: %v", bucket, key, err)
	}
	if bytes.Contains(body, []byte(text)) {
		t.Fatalf("%s/%s contains %q, want removed:\n%s", bucket, key, text, body)
	}
}
