//go:build integration

package sitemapping

import (
	"context"
	"encoding/json"
	"testing"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
	tcpostgres "github.com/testcontainers/testcontainers-go/modules/postgres"

	"publication-service/internal/events"
	pub "publication-service/internal/publish"
	pg "publication-service/internal/storage/postgres"
)

func setupRequestRepo(t *testing.T) (*RequestRepo, *pub.Repo, *pgxpool.Pool) {
	t.Helper()
	ctx, cancel := context.WithTimeout(context.Background(), 60*time.Second)
	defer cancel()
	c, err := tcpostgres.Run(ctx, "postgres:16-alpine",
		tcpostgres.WithDatabase("foi"),
		tcpostgres.WithUsername("foi"),
		tcpostgres.WithPassword("foi"),
		tcpostgres.BasicWaitStrategies(),
	)
	if err != nil {
		t.Fatalf("postgres: %v", err)
	}
	t.Cleanup(func() { _ = c.Terminate(context.Background()) })
	dsn, err := c.ConnectionString(ctx, "sslmode=disable")
	if err != nil {
		t.Fatalf("connection string: %v", err)
	}
	if err := pg.Migrate(ctx, dsn); err != nil {
		t.Fatalf("migrate: %v", err)
	}
	pool, err := pgxpool.New(ctx, dsn)
	if err != nil {
		t.Fatalf("pool: %v", err)
	}
	t.Cleanup(pool.Close)
	return NewRequestRepo(pool), pub.NewRepo(pool), pool
}

func claimSitemapRequest(t *testing.T, repo *pub.Repo, eventID string) {
	t.Helper()
	_, err := repo.Claim(context.Background(), pub.ClaimRequest{
		EventID:       eventID,
		EventType:     events.TypePublicationSitemappingRequested,
		TenantID:      "a7d9b2f1-4c3e-4e8b-9a21-1c2e8f7b9d10",
		CorrelationID: eventID,
		SchemaVersion: events.SchemaVersionV1,
		Payload: json.RawMessage(`{
			"tenant_id":"a7d9b2f1-4c3e-4e8b-9a21-1c2e8f7b9d10",
			"publication_id":"HTH-2025-52023:v1",
			"public_url":"https://example.gov.bc.ca/openinfopub/packages/HTH-2025-52023/openinfo/HTH-2025-52023.html",
			"last_modified":"2026-04-01",
			"publication_result_ref":"018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d90"
		}`),
		Now:  time.Now().UTC(),
		Kind: pub.KindOpenInfoSitemap,
	})
	if err != nil {
		t.Fatalf("Claim: %v", err)
	}
}

func sampleSitemapResult() Result {
	return Result{
		Kind:                 pub.KindOpenInfoSitemap,
		TenantID:             "a7d9b2f1-4c3e-4e8b-9a21-1c2e8f7b9d10",
		PublicationID:        "HTH-2025-52023:v1",
		PublicURL:            "https://example.gov.bc.ca/openinfopub/packages/HTH-2025-52023/openinfo/HTH-2025-52023.html",
		LastModified:         time.Date(2026, 4, 1, 0, 0, 0, 0, time.UTC),
		SitemapIndexKey:      "openinfopub/sitemap/sitemap_index.xml",
		SitemapPageKey:       "openinfopub/sitemap/sitemap_pages_1.xml",
		SitemapPageURL:       "https://example.gov.bc.ca/openinfopub/sitemap/sitemap_pages_1.xml",
		Status:               StatusWritten,
		IndexUpdated:         false,
		PublicationResultRef: "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d90",
		CompletedAt:          time.Date(2026, 4, 21, 12, 30, 0, 0, time.UTC),
	}
}

func TestRequestRepo_FindCompletedFalseBeforeSuccess(t *testing.T) {
	repo, pubRepo, _ := setupRequestRepo(t)
	claimSitemapRequest(t, pubRepo, "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d90")

	_, ok, err := repo.FindCompleted(context.Background(), pub.KindOpenInfoSitemap, "HTH-2025-52023:v1")
	if err != nil {
		t.Fatalf("FindCompleted: %v", err)
	}
	if ok {
		t.Fatal("FindCompleted returned true before success")
	}
}

func TestRequestRepo_MarkSucceededStoresFullResult(t *testing.T) {
	repo, pubRepo, pool := setupRequestRepo(t)
	eventID := "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d90"
	claimSitemapRequest(t, pubRepo, eventID)
	result := sampleSitemapResult()

	if err := repo.MarkSucceeded(context.Background(), eventID, result); err != nil {
		t.Fatalf("MarkSucceeded: %v", err)
	}

	var state string
	var raw []byte
	if err := pool.QueryRow(context.Background(),
		`SELECT state, result FROM workflow_request WHERE event_id=$1`, eventID,
	).Scan(&state, &raw); err != nil {
		t.Fatalf("query stored result: %v", err)
	}
	if state != "completed" {
		t.Fatalf("state = %q, want completed", state)
	}
	var stored Result
	if err := json.Unmarshal(raw, &stored); err != nil {
		t.Fatalf("unmarshal stored result: %v", err)
	}
	if stored != result {
		t.Fatalf("stored result mismatch:\n got: %#v\nwant: %#v", stored, result)
	}
}

func TestRequestRepo_FindCompletedReturnsStoredResultByKindAndPublicationID(t *testing.T) {
	repo, pubRepo, _ := setupRequestRepo(t)
	eventID := "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d90"
	claimSitemapRequest(t, pubRepo, eventID)
	want := sampleSitemapResult()
	if err := repo.MarkSucceeded(context.Background(), eventID, want); err != nil {
		t.Fatalf("MarkSucceeded: %v", err)
	}

	got, ok, err := repo.FindCompleted(context.Background(), pub.KindOpenInfoSitemap, "HTH-2025-52023:v1")
	if err != nil {
		t.Fatalf("FindCompleted: %v", err)
	}
	if !ok {
		t.Fatal("FindCompleted returned false after success")
	}
	if got != want {
		t.Fatalf("FindCompleted result mismatch:\n got: %#v\nwant: %#v", got, want)
	}
}
