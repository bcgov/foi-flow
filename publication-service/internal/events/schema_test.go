package events

import "testing"

func TestSchemaFor_Requested(t *testing.T) {
	s, err := SchemaFor(TypePublicationPublishRequested, SchemaVersionV1)
	if err != nil {
		t.Fatalf("SchemaFor: %v", err)
	}

	valid := map[string]any{
		"tenant_id":       "a7d9b2f1-4c3e-4e8b-9a21-1c2e8f7b9d10",
		"axis_request_id": "HTH-2025-52023",
		"kind":            "openinfo",
		"source": map[string]any{
			"bucket": "foi-raw",
			"prefix": "incoming/a7d9b2f1/",
		},
		"destination": map[string]any{
			"bucket": "foi-published",
			"prefix": "out/a7d9b2f1/",
		},
	}
	if err := s.Validate(valid); err != nil {
		t.Fatalf("Validate good: %v", err)
	}

	missingSource := map[string]any{
		"tenant_id":   "a7d9b2f1-4c3e-4e8b-9a21-1c2e8f7b9d10",
		"kind":        "openinfo",
		"destination": map[string]any{"bucket": "foi-pub", "prefix": "p/"},
	}
	if err := s.Validate(missingSource); err == nil {
		t.Fatal("expected error: missing source")
	}

	badBucket := map[string]any{
		"tenant_id":   "a7d9b2f1-4c3e-4e8b-9a21-1c2e8f7b9d10",
		"kind":        "openinfo",
		"source":      map[string]any{"bucket": "BadBucket", "prefix": ""},
		"destination": map[string]any{"bucket": "foi-pub", "prefix": "p/"},
	}
	if err := s.Validate(badBucket); err == nil {
		t.Fatal("expected error: uppercase bucket")
	}

	extraField := map[string]any{
		"tenant_id":       "a7d9b2f1-4c3e-4e8b-9a21-1c2e8f7b9d10",
		"kind":            "openinfo",
		"axis_request_id": "HTH-2025-52023",
		"source":          map[string]any{"bucket": "foi-raw", "prefix": "p/"},
		"destination":     map[string]any{"bucket": "foi-pub", "prefix": "q/"},
		"extra":           "nope",
	}
	if err := s.Validate(extraField); err == nil {
		t.Fatal("expected error: additionalProperties:false rejects extras")
	}

	missingTenant := map[string]any{
		"kind":        "openinfo",
		"source":      map[string]any{"bucket": "foi-raw", "prefix": "src/"},
		"destination": map[string]any{"bucket": "foi-pub", "prefix": "dst/"},
	}
	if err := s.Validate(missingTenant); err == nil {
		t.Fatal("expected error: missing tenant_id")
	}
}

func TestSchemaFor_UnknownType(t *testing.T) {
	if _, err := SchemaFor("bogus.type", SchemaVersionV1); err == nil {
		t.Fatal("expected unknown-type error")
	}
}

func TestSchemaFor_PublishCompletedAcceptsEnrichedPayload(t *testing.T) {
	cases := []struct {
		name     string
		required map[string]any
	}{
		{
			name: "openinfo",
			required: map[string]any{
				"tenant_id":        "a7d9b2f1-4c3e-4e8b-9a21-1c2e8f7b9d10",
				"request_event_id": "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d90",
				"correlation_id":   "corr-123",
			},
		},
		{
			name: "pd",
			required: map[string]any{
				"tenant_id":        "a7d9b2f1-4c3e-4e8b-9a21-1c2e8f7b9d10",
				"request_event_id": "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d91",
				"correlation_id":   "corr-456",
			},
		},
	}

	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			s, err := SchemaFor(TypePublicationPublishCompleted, SchemaVersionV1)
			if err != nil {
				t.Fatalf("SchemaFor: %v", err)
			}
			valid := map[string]any{
				"publication_id":        tc.name + "-pub-1",
				"public_url":            "https://example.gov.bc.ca/" + tc.name + "/record.html",
				"html_key":              tc.name + "/record.html",
				"sitemap_index_key":     tc.name + "/sitemap/sitemap_index.xml",
				"sitemap_page_key":      tc.name + "/sitemap/sitemap_pages_1.xml",
				"sitemap_page_url":      "https://example.gov.bc.ca/" + tc.name + "/sitemap_pages_1.xml",
				"sitemap_result":        "written",
				"sitemap_index_updated": true,
			}
			for k, v := range tc.required {
				valid[k] = v
			}
			if err := s.Validate(valid); err != nil {
				t.Fatalf("Validate enriched payload: %v", err)
			}

			invalid := make(map[string]any, len(valid))
			for k, v := range valid {
				invalid[k] = v
			}
			invalid["sitemap_index_updated"] = "true"
			if err := s.Validate(invalid); err == nil {
				t.Fatal("expected error: sitemap_index_updated must be boolean")
			}
		})
	}
}

func TestSchemaFor_CompletedRequiresCorrelationID(t *testing.T) {
	s, err := SchemaFor(TypePublicationPublishCompleted, SchemaVersionV1)
	if err != nil {
		t.Fatalf("SchemaFor: %v", err)
	}

	valid := map[string]any{
		"tenant_id":        "a7d9b2f1-4c3e-4e8b-9a21-1c2e8f7b9d10",
		"request_event_id": "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d90",
		"correlation_id":   "corr-123",
	}
	if err := s.Validate(valid); err != nil {
		t.Fatalf("Validate good: %v", err)
	}

	missingCorrelationID := map[string]any{
		"tenant_id":        "a7d9b2f1-4c3e-4e8b-9a21-1c2e8f7b9d10",
		"request_event_id": "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d90",
	}
	if err := s.Validate(missingCorrelationID); err == nil {
		t.Fatal("expected error: missing correlation_id")
	}
}

func TestSchemaFor_SitemappingRequested(t *testing.T) {
	cases := []struct {
		name    string
		kind    string
		pubID   string
		baseURL string
		ref     string
	}{
		{"openinfo", "openinfo", "HTH-2025-52023:v1", "https://example.gov.bc.ca/openinfopub/packages/HTH-2025-52023/openinfo/HTH-2025-52023.html", "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d90"},
		{"pd", "proactivedisclosure", "PD-2026-001:v1", "https://example.gov.bc.ca/proactivedisclosurepub/packages/PD-2026-001/openinfo/PD-2026-001.html", "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d91"},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			s, err := SchemaFor(TypePublicationSitemappingRequested, SchemaVersionV1)
			if err != nil {
				t.Fatalf("SchemaFor: %v", err)
			}
			valid := map[string]any{
				"tenant_id":              "a7d9b2f1-4c3e-4e8b-9a21-1c2e8f7b9d10",
				"publication_id":         tc.pubID,
				"public_url":             tc.baseURL,
				"last_modified":          "2026-04-01",
				"publication_result_ref": tc.ref,
				"kind":                   tc.kind,
			}
			if err := s.Validate(valid); err != nil {
				t.Fatalf("Validate good: %v", err)
			}
		})
	}
}

func TestSchemaFor_SitemappingCompleted(t *testing.T) {
	cases := []struct {
		name    string
		pageKey string
	}{
		{"openinfo", "openinfopub/sitemap/sitemap_pages_1.xml"},
		{"pd", "proactivedisclosurepub/sitemap/sitemap_pages_1.xml"},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			s, err := SchemaFor(TypePublicationSitemappingCompleted, SchemaVersionV1)
			if err != nil {
				t.Fatalf("SchemaFor: %v", err)
			}
			valid := map[string]any{
				"tenant_id":              "a7d9b2f1-4c3e-4e8b-9a21-1c2e8f7b9d10",
				"publication_id":         tc.name + ":v1",
				"public_url":             "https://example.gov.bc.ca/" + tc.name + "/record.html",
				"last_modified":          "2026-04-01",
				"sitemap_index_key":      tc.name + "/sitemap/sitemap_index.xml",
				"sitemap_page_key":       tc.pageKey,
				"sitemap_page_url":       "https://example.gov.bc.ca/" + tc.pageKey,
				"result":                 "written",
				"index_updated":          false,
				"publication_result_ref": "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d91",
				"kind":                   "openinfo",
			}
			if err := s.Validate(valid); err != nil {
				t.Fatalf("Validate good: %v", err)
			}
		})
	}
}
