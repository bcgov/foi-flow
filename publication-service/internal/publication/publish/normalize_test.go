package publish

import (
	"encoding/json"
	"testing"

	"publication-service/internal/events"
	pub "publication-service/internal/publish"
)

func goodOpenInfoPayload() json.RawMessage {
	return json.RawMessage(`{
		"tenant_id":       "a7d9b2f1-4c3e-4e8b-9a21-1c2e8f7b9d10",
		"source":          {"bucket": "foi-raw",       "prefix": "incoming/a7d9b2f1/"},
		"destination":     {"bucket": "foi-published", "prefix": "out/a7d9b2f1/"},
		"axis_request_id": "HTH-2025-52023",
		"kind":            "openinfo",
		"description":     "Test request",
		"published_date":  "2025-04-01",
		"contributor":     "Ministry of Test",
		"fees":            150,
		"applicant_type":  "Business"
	}`)
}

func goodPDPayload() json.RawMessage {
	return json.RawMessage(`{
		"tenant_id":                    "a7d9b2f1-4c3e-4e8b-9a21-1c2e8f7b9d10",
		"source":                       {"bucket": "foi-raw",       "prefix": "incoming/pd/"},
		"destination":                  {"bucket": "foi-published", "prefix": "out/pd/"},
		"axis_request_id":              "PD-2025-001",
		"kind":                         "proactivedisclosure",
		"description":                  "PD test",
		"published_date":               "2025-04-01",
		"contributor":                   "Ministry of PD",
		"fees":                          0,
		"applicant_type":               null,
		"proactivedisclosure_category": "Travel",
		"report_period":                "2025-Q1"
	}`)
}

func goodEnvelope() *events.Envelope {
	return &events.Envelope{
		EventID:       "evt-001",
		EventType:     events.TypePublicationPublishRequested,
		SchemaVersion: events.SchemaVersionV1,
		CorrelationID: "corr-001",
		Source:        "test",
		Payload:       goodOpenInfoPayload(),
	}
}

func TestNormalize_OpenInfoPayload(t *testing.T) {
	env := goodEnvelope()
	d, err := Normalize(env)
	if err != nil {
		t.Fatalf("Normalize: %v", err)
	}
	if d.Kind != pub.KindOpenInfo {
		t.Errorf("Kind = %q, want %q", d.Kind, pub.KindOpenInfo)
	}
	if d.TenantID != "a7d9b2f1-4c3e-4e8b-9a21-1c2e8f7b9d10" {
		t.Errorf("TenantID = %q", d.TenantID)
	}
	if d.RequestID != "HTH-2025-52023" {
		t.Errorf("RequestID = %q", d.RequestID)
	}
	if d.ApplicantType != "Business" {
		t.Errorf("ApplicantType = %q", d.ApplicantType)
	}
	if d.Category != "" {
		t.Errorf("Category = %q, want empty for openinfo", d.Category)
	}
}

func TestNormalize_FOIIDs_PresentWhenProvided(t *testing.T) {
	env := goodEnvelope()
	env.Payload = json.RawMessage(`{
		"tenant_id":       "a7d9b2f1-4c3e-4e8b-9a21-1c2e8f7b9d10",
		"source":          {"bucket": "foi-raw",       "prefix": "incoming/a7d9b2f1/"},
		"destination":     {"bucket": "foi-published", "prefix": "out/a7d9b2f1/"},
		"axis_request_id": "HTH-2025-52023",
		"kind":            "openinfo",
		"foiministryrequest_id": 22318,
		"foirequest_id": 22319
	}`)
	d, err := Normalize(env)
	if err != nil {
		t.Fatalf("Normalize: %v", err)
	}
	if d.FOIMinistryRequestID == nil || *d.FOIMinistryRequestID != 22318 {
		t.Errorf("FOIMinistryRequestID = %v, want 22318", d.FOIMinistryRequestID)
	}
	if d.FOIRequestID == nil || *d.FOIRequestID != 22319 {
		t.Errorf("FOIRequestID = %v, want 22319", d.FOIRequestID)
	}
}

func TestNormalize_FOIIDs_NilWhenAbsent(t *testing.T) {
	env := goodEnvelope()
	d, err := Normalize(env)
	if err != nil {
		t.Fatalf("Normalize: %v", err)
	}
	if d.FOIMinistryRequestID != nil {
		t.Errorf("FOIMinistryRequestID = %v, want nil", d.FOIMinistryRequestID)
	}
	if d.FOIRequestID != nil {
		t.Errorf("FOIRequestID = %v, want nil", d.FOIRequestID)
	}
}

func TestNormalize_PDPayload(t *testing.T) {
	env := goodEnvelope()
	env.Payload = goodPDPayload()
	d, err := Normalize(env)
	if err != nil {
		t.Fatalf("Normalize: %v", err)
	}
	if d.Kind != pub.KindProactiveDisclosure {
		t.Errorf("Kind = %q, want %q", d.Kind, pub.KindProactiveDisclosure)
	}
	if d.Category != "Travel" {
		t.Errorf("Category = %q, want Travel", d.Category)
	}
	if d.ReportPeriod != "2025-Q1" {
		t.Errorf("ReportPeriod = %q", d.ReportPeriod)
	}
	if d.ApplicantType != "" {
		t.Errorf("ApplicantType = %q, want empty for null", d.ApplicantType)
	}
}

func TestNormalize_RejectsUnsupportedVersion(t *testing.T) {
	env := goodEnvelope()
	env.SchemaVersion = "9.9.9"
	_, err := Normalize(env)
	if _, ok := err.(*pub.PermanentError); !ok {
		t.Fatalf("expected *PermanentError, got %T (%v)", err, err)
	}
}

func TestNormalize_CanonicalizesTrailingSlash(t *testing.T) {
	env := goodEnvelope()
	env.Payload = json.RawMessage(`{
		"tenant_id":       "a7d9b2f1-4c3e-4e8b-9a21-1c2e8f7b9d10",
		"source":          {"bucket": "foi-raw",       "prefix": "incoming/a7d9b2f1"},
		"destination":     {"bucket": "foi-published", "prefix": "out/a7d9b2f1"},
		"axis_request_id": "HTH-2025-52023",
		"kind":            "openinfo"
	}`)
	d, err := Normalize(env)
	if err != nil {
		t.Fatalf("Normalize: %v", err)
	}
	if d.Source.Prefix != "incoming/a7d9b2f1/" {
		t.Errorf("Source.Prefix = %q, want trailing slash", d.Source.Prefix)
	}
	if d.Destination.Prefix != "out/a7d9b2f1/" {
		t.Errorf("Destination.Prefix = %q, want trailing slash", d.Destination.Prefix)
	}
}

func TestNormalize_RejectsOverlappingPrefixes(t *testing.T) {
	env := goodEnvelope()
	env.Payload = json.RawMessage(`{
		"tenant_id":       "a7d9b2f1-4c3e-4e8b-9a21-1c2e8f7b9d10",
		"source":          {"bucket": "same-bucket", "prefix": "data/"},
		"destination":     {"bucket": "same-bucket", "prefix": "data/sub/"},
		"axis_request_id": "HTH-2025-52023",
		"kind":            "openinfo"
	}`)
	_, err := Normalize(env)
	if _, ok := err.(*pub.PermanentError); !ok {
		t.Fatalf("expected *PermanentError, got %T (%v)", err, err)
	}
}

func TestNormalize_RejectsEmptyBucket(t *testing.T) {
	env := goodEnvelope()
	env.Payload = json.RawMessage(`{
		"tenant_id":       "a7d9b2f1-4c3e-4e8b-9a21-1c2e8f7b9d10",
		"source":          {"bucket": "  ",            "prefix": "x/"},
		"destination":     {"bucket": "foi-published", "prefix": "y/"},
		"axis_request_id": "X",
		"kind":            "openinfo"
	}`)
	_, err := Normalize(env)
	if _, ok := err.(*pub.PermanentError); !ok {
		t.Fatalf("expected *PermanentError, got %T (%v)", err, err)
	}
}

func TestNormalize_PDRequiresCategoryAndReportPeriod(t *testing.T) {
	env := goodEnvelope()
	env.Payload = json.RawMessage(`{
		"tenant_id":       "a7d9b2f1-4c3e-4e8b-9a21-1c2e8f7b9d10",
		"source":          {"bucket": "foi-raw",       "prefix": "in/"},
		"destination":     {"bucket": "foi-published", "prefix": "out/"},
		"axis_request_id": "PD-001",
		"kind":            "proactivedisclosure"
	}`)
	_, err := Normalize(env)
	if _, ok := err.(*pub.PermanentError); !ok {
		t.Fatalf("expected *PermanentError for missing PD fields, got %T (%v)", err, err)
	}
}

func TestNormalize_TitlePassedThrough(t *testing.T) {
	env := goodEnvelope()
	env.Payload = json.RawMessage(`{
		"tenant_id":       "a7d9b2f1-4c3e-4e8b-9a21-1c2e8f7b9d10",
		"source":          {"bucket": "foi-raw",       "prefix": "incoming/a7d9b2f1/"},
		"destination":     {"bucket": "foi-published", "prefix": "out/a7d9b2f1/"},
		"axis_request_id": "HTH-2025-52023",
		"kind":            "openinfo",
		"title":           "Custom Title"
	}`)
	d, err := Normalize(env)
	if err != nil {
		t.Fatalf("Normalize: %v", err)
	}
	if d.Title != "Custom Title" {
		t.Errorf("Title = %q, want %q", d.Title, "Custom Title")
	}
}

func TestNormalize_TitleEmptyWhenAbsent(t *testing.T) {
	env := goodEnvelope()
	d, err := Normalize(env)
	if err != nil {
		t.Fatalf("Normalize: %v", err)
	}
	if d.Title != "" {
		t.Errorf("Title = %q, want empty", d.Title)
	}
}

func TestNormalize_EmptyPrefixPreserved(t *testing.T) {
	env := goodEnvelope()
	env.Payload = json.RawMessage(`{
		"tenant_id":       "a7d9b2f1-4c3e-4e8b-9a21-1c2e8f7b9d10",
		"source":          {"bucket": "foi-raw",       "prefix": ""},
		"destination":     {"bucket": "foi-published", "prefix": "out/"},
		"axis_request_id": "HTH-001",
		"kind":            "openinfo"
	}`)
	d, err := Normalize(env)
	if err != nil {
		t.Fatalf("Normalize: %v", err)
	}
	if d.Source.Prefix != "" {
		t.Errorf("Source.Prefix = %q, want empty", d.Source.Prefix)
	}
}

func TestNormalize_AdditionalFiles_ActiveOnly(t *testing.T) {
	env := goodEnvelope()
	env.Payload = json.RawMessage(`{
		"tenant_id":       "a7d9b2f1-4c3e-4e8b-9a21-1c2e8f7b9d10",
		"source":          {"bucket": "foi-raw",       "prefix": "incoming/"},
		"destination":     {"bucket": "foi-published", "prefix": "out/"},
		"axis_request_id": "HTH-2025-52023",
		"kind":            "openinfo",
		"additionalfiles": [
			{"additionalfileid": 67, "filename": "s.pdf", "s3uripath": "https://store.example/bucket-a/path/to/file.pdf", "isactive": true},
			{"additionalfileid": 68, "filename": "inactive.pdf", "s3uripath": "https://store.example/bucket-a/path/to/inactive.pdf", "isactive": false}
		]
	}`)
	d, err := Normalize(env)
	if err != nil {
		t.Fatalf("Normalize: %v", err)
	}
	if len(d.AdditionalFiles) != 1 {
		t.Fatalf("AdditionalFiles length = %d, want 1", len(d.AdditionalFiles))
	}
	af := d.AdditionalFiles[0]
	if af.ID != 67 {
		t.Errorf("ID = %d, want 67", af.ID)
	}
	if af.Filename != "s.pdf" {
		t.Errorf("Filename = %q, want s.pdf", af.Filename)
	}
	if af.S3URI != "https://store.example/bucket-a/path/to/file.pdf" {
		t.Errorf("S3URI = %q", af.S3URI)
	}
}

func TestNormalize_AdditionalFiles_EmptyWhenAbsent(t *testing.T) {
	env := goodEnvelope()
	d, err := Normalize(env)
	if err != nil {
		t.Fatalf("Normalize: %v", err)
	}
	if len(d.AdditionalFiles) != 0 {
		t.Errorf("AdditionalFiles length = %d, want 0", len(d.AdditionalFiles))
	}
}

func TestParseS3URI_ValidURL(t *testing.T) {
	bucket, key, err := parseS3URI("https://citz-foi-prod.objectstore.gov.bc.ca/psa-dev-e/PSA-2025-154571/openinfo/fdaef2d5.pdf")
	if err != nil {
		t.Fatalf("parseS3URI: %v", err)
	}
	if bucket != "psa-dev-e" {
		t.Errorf("bucket = %q, want psa-dev-e", bucket)
	}
	if key != "PSA-2025-154571/openinfo/fdaef2d5.pdf" {
		t.Errorf("key = %q", key)
	}
}

func TestParseS3URI_InvalidURL(t *testing.T) {
	cases := []string{
		"",
		"not-a-url",
		"https://host.example/",        // no key
		"https://host.example/bucket",  // no key after bucket
		"https://host.example/bucket/", // empty key
	}
	for _, uri := range cases {
		_, _, err := parseS3URI(uri)
		if err == nil {
			t.Errorf("parseS3URI(%q) expected error, got nil", uri)
		}
	}
}
