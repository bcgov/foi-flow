//go:build integration

package unpublish

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
		ClaimRequest: claimUnpublishRequest,
		SampleResult: sampleUnpublishResult,
		Kind:         pub.KindOpenInfoUnpublish,
		OtherKind:    pub.KindProactiveDisclosureUnpublish,
		TenantID:     testTenantID,
	})
}

func claimUnpublishRequest(eventID string, correlationID string) pub.ClaimRequest {
	return pub.ClaimRequest{
		EventID:       eventID,
		EventType:     events.TypePublicationUnpublishRequested,
		TenantID:      testTenantID,
		CorrelationID: correlationID,
		SchemaVersion: events.SchemaVersionV1,
		Payload: json.RawMessage(`{
			"tenant_id":"a7d9b2f1-4c3e-4e8b-9a21-1c2e8f7b9d10",
			"publication_id":"HTH-2025-52023:v1",
			"public_url":"https://example.gov.bc.ca/openinfopub/packages/HTH-2025-52023/openinfo/HTH-2025-52023.html",
			"public_repository":{"bucket":"public","prefix":"openinfo/HTH-2025-52023"}
		}`),
		Kind: pub.KindOpenInfoUnpublish,
	}
}

func sampleUnpublishResult() Result {
	return Result{
		Kind:                   pub.KindOpenInfoUnpublish,
		TenantID:               testTenantID,
		PublicationID:          "HTH-2025-52023:v1",
		PublicURL:              "https://example.gov.bc.ca/openinfopub/packages/HTH-2025-52023/openinfo/HTH-2025-52023.html",
		PublicRepositoryBucket: "public",
		PublicRepositoryPrefix: "openinfo/HTH-2025-52023",
		ObjectsDeleted:         3,
		SitemapIndexKey:        "openinfopub/sitemap/sitemap_index.xml",
		SitemapPageKey:         "openinfopub/sitemap/sitemap_pages_1.xml",
		SitemapResult:          "removed",
		CompletedAt:            time.Date(2026, 4, 21, 12, 30, 0, 0, time.UTC),
	}
}
