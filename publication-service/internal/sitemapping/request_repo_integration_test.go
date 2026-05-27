//go:build integration

package sitemapping

import (
	"encoding/json"
	"testing"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"

	"publication-service/internal/events"
	pub "publication-service/internal/publish"
	"publication-service/internal/workflowtest"
)

const testTenantID = "a7d9b2f1-4c3e-4e8b-9a21-1c2e8f7b9d10"

func TestRequestRepo(t *testing.T) {
	workflowtest.RunRequestRepoSuite(t, workflowtest.RequestRepoSuite[Result]{
		NewRepo:      func(pool *pgxpool.Pool) workflowtest.RequestRepo[Result] { return NewRequestRepo(pool) },
		ClaimRequest: claimSitemapRequest,
		SampleResult: sampleSitemapResult,
		Kind:         pub.KindOpenInfoSitemap,
		OtherKind:    pub.KindProactiveDisclosureSitemap,
		TenantID:     testTenantID,
	})
}

func claimSitemapRequest(eventID string, correlationID string) pub.ClaimRequest {
	return pub.ClaimRequest{
		EventID:       eventID,
		EventType:     events.TypePublicationSitemappingRequested,
		TenantID:      testTenantID,
		CorrelationID: correlationID,
		SchemaVersion: events.SchemaVersionV1,
		Payload: json.RawMessage(`{
			"tenant_id":"a7d9b2f1-4c3e-4e8b-9a21-1c2e8f7b9d10",
			"publication_id":"HTH-2025-52023:v1",
			"public_url":"https://example.gov.bc.ca/openinfopub/packages/HTH-2025-52023/openinfo/HTH-2025-52023.html",
			"last_modified":"2026-04-01",
			"publication_result_ref":"018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d90"
		}`),
		Kind: pub.KindOpenInfoSitemap,
	}
}

func sampleSitemapResult() Result {
	return Result{
		Kind:                 pub.KindOpenInfoSitemap,
		TenantID:             testTenantID,
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
