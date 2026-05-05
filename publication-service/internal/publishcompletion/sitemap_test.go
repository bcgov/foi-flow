package publishcompletion

import (
	"testing"

	pub "publication-service/internal/publish"
)

func TestSitemapRequest(t *testing.T) {
	tests := []struct {
		name string
		kind pub.Kind
	}{
		{
			name: "openinfo sitemap",
			kind: pub.KindOpenInfoSitemap,
		},
		{
			name: "proactive disclosure sitemap",
			kind: pub.KindProactiveDisclosureSitemap,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := pub.PublishResult{
				PublicationID: "pub-123",
				HTMLKey:       "publications/pub-123/index.html",
				PublicURL:     "https://example.test/pub-123/",
			}

			req, err := SitemapRequest(tt.kind, "tenant-1", "corr-1", "event-1", result, "2026-04-28")
			if err != nil {
				t.Fatalf("SitemapRequest returned error: %v", err)
			}

			if req.Kind != tt.kind {
				t.Fatalf("Kind = %q, want %q", req.Kind, tt.kind)
			}
			if req.TenantID != "tenant-1" {
				t.Fatalf("TenantID = %q, want tenant-1", req.TenantID)
			}
			if req.PublicationID != result.PublicationID {
				t.Fatalf("PublicationID = %q, want %q", req.PublicationID, result.PublicationID)
			}
			if req.PublicURL != result.PublicURL {
				t.Fatalf("PublicURL = %q, want %q", req.PublicURL, result.PublicURL)
			}
			if req.PublicationResultRef != result.HTMLKey {
				t.Fatalf("PublicationResultRef = %q, want %q", req.PublicationResultRef, result.HTMLKey)
			}
			if req.SourceEventID != "event-1" {
				t.Fatalf("SourceEventID = %q, want event-1", req.SourceEventID)
			}
			if req.CorrelationID != "corr-1" {
				t.Fatalf("CorrelationID = %q, want corr-1", req.CorrelationID)
			}
			if got := req.LastModified.Format("2006-01-02"); got != "2026-04-28" {
				t.Fatalf("LastModified = %q, want 2026-04-28", got)
			}
		})
	}
}

func TestSitemapRequestInvalidPublishedDate(t *testing.T) {
	_, err := SitemapRequest(pub.KindOpenInfoSitemap, "tenant-1", "corr-1", "event-1", pub.PublishResult{}, "04/28/2026")
	if err == nil {
		t.Fatal("SitemapRequest returned nil error for invalid date")
	}
}
