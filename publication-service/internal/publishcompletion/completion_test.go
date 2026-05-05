package publishcompletion

import (
	"encoding/json"
	"testing"
	"time"

	pub "publication-service/internal/publish"
	"publication-service/internal/sitemapping"
)

func TestBuildPayload(t *testing.T) {
	payload, err := BuildPayload(
		"tenant-1",
		"request-event-1",
		"corr-1",
		nil, nil,
		pub.PublishResult{
			PublicationID: "pub-123",
			HTMLKey:       "publications/pub-123/index.html",
			PublicURL:     "https://example.test/pub-123/",
		},
		sitemapping.Result{
			SitemapIndexKey: "sitemaps/sitemap.xml",
			SitemapPageKey:  "sitemaps/sitemap-1.xml",
			SitemapPageURL:  "https://example.test/sitemap-1.xml",
			Status:          sitemapping.StatusWritten,
			IndexUpdated:    true,
			CompletedAt:     time.Date(2026, 4, 28, 10, 30, 0, 0, time.UTC),
		},
	)
	if err != nil {
		t.Fatalf("BuildPayload returned error: %v", err)
	}

	var got map[string]any
	if err := json.Unmarshal(payload, &got); err != nil {
		t.Fatalf("payload was not JSON: %v", err)
	}

	want := map[string]any{
		"tenant_id":             "tenant-1",
		"request_event_id":      "request-event-1",
		"correlation_id":        "corr-1",
		"publication_id":        "pub-123",
		"public_url":            "https://example.test/pub-123/",
		"html_key":              "publications/pub-123/index.html",
		"sitemap_index_key":     "sitemaps/sitemap.xml",
		"sitemap_page_key":      "sitemaps/sitemap-1.xml",
		"sitemap_page_url":      "https://example.test/sitemap-1.xml",
		"sitemap_result":        "written",
		"sitemap_index_updated": true,
	}

	for key, expected := range want {
		if got[key] != expected {
			t.Fatalf("%s = %#v, want %#v", key, got[key], expected)
		}
	}
}

func TestBuildPayload_FOIIDs(t *testing.T) {
	ministryID := 22318
	requestID := 22319
	payload, err := BuildPayload(
		"tenant-1", "req-1", "corr-1",
		&ministryID, &requestID,
		pub.PublishResult{PublicationID: "pub-1", HTMLKey: "k", PublicURL: "https://x"},
		sitemapping.Result{Status: sitemapping.StatusWritten},
	)
	if err != nil {
		t.Fatalf("BuildPayload: %v", err)
	}
	var got map[string]any
	if err := json.Unmarshal(payload, &got); err != nil {
		t.Fatalf("unmarshal: %v", err)
	}
	if v, ok := got["foiministryrequest_id"]; !ok {
		t.Error("missing foiministryrequest_id")
	} else if int(v.(float64)) != 22318 {
		t.Errorf("foiministryrequest_id = %v, want 22318", v)
	}
	if v, ok := got["foirequest_id"]; !ok {
		t.Error("missing foirequest_id")
	} else if int(v.(float64)) != 22319 {
		t.Errorf("foirequest_id = %v, want 22319", v)
	}
}

func TestBuildPayload_FOIIDs_OmittedWhenNil(t *testing.T) {
	payload, err := BuildPayload(
		"tenant-1", "req-1", "corr-1",
		nil, nil,
		pub.PublishResult{PublicationID: "pub-1", HTMLKey: "k", PublicURL: "https://x"},
		sitemapping.Result{Status: sitemapping.StatusWritten},
	)
	if err != nil {
		t.Fatalf("BuildPayload: %v", err)
	}
	var got map[string]any
	if err := json.Unmarshal(payload, &got); err != nil {
		t.Fatalf("unmarshal: %v", err)
	}
	if _, ok := got["foiministryrequest_id"]; ok {
		t.Error("foiministryrequest_id should be absent when nil")
	}
	if _, ok := got["foirequest_id"]; ok {
		t.Error("foirequest_id should be absent when nil")
	}
}
