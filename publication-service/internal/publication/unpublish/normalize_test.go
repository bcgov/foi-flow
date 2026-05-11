package unpublish

import (
	"encoding/json"
	"testing"

	"publication-service/internal/events"
	pub "publication-service/internal/publish"
)

func goodUnpublishEnvelope(kind string) *events.Envelope {
	payload, _ := json.Marshal(map[string]any{
		"tenant_id":      "tenant-1",
		"publication_id": "EDU-2024-12345",
		"public_url":     "https://example/public/EDU-2024-12345.html",
		"public_repository": map[string]string{
			"bucket": "public-bucket",
			"prefix": "openinfo/EDU-2024-12345",
		},
		"last_modified": "2026-04-27",
		"kind":          kind,
	})
	return &events.Envelope{
		EventID:       "event-1",
		EventType:     events.TypePublicationUnpublishRequested,
		SchemaVersion: events.SchemaVersionV1,
		CorrelationID: "corr-1",
		Source:        "test",
		Payload:       payload,
	}
}

func TestNormalize_OpenInfoUnpublish(t *testing.T) {
	env := goodUnpublishEnvelope("openinfo")
	req, err := Normalize(env)
	if err != nil {
		t.Fatalf("Normalize: %v", err)
	}
	if req.Kind != pub.KindOpenInfoUnpublish {
		t.Errorf("Kind = %q, want %q", req.Kind, pub.KindOpenInfoUnpublish)
	}
	if req.PublicationID != "EDU-2024-12345" {
		t.Errorf("PublicationID = %q", req.PublicationID)
	}
}

func TestNormalize_PDUnpublish(t *testing.T) {
	env := goodUnpublishEnvelope("proactivedisclosure")
	req, err := Normalize(env)
	if err != nil {
		t.Fatalf("Normalize: %v", err)
	}
	if req.Kind != pub.KindProactiveDisclosureUnpublish {
		t.Errorf("Kind = %q, want %q", req.Kind, pub.KindProactiveDisclosureUnpublish)
	}
}

func TestNormalize_RejectsBadDate(t *testing.T) {
	env := goodUnpublishEnvelope("openinfo")
	env.Payload = json.RawMessage(`{
		"tenant_id": "tenant-1",
		"publication_id": "X",
		"public_url": "https://x",
		"public_repository": {"bucket": "b", "prefix": "p"},
		"last_modified": "not-a-date",
		"kind": "openinfo"
	}`)
	_, err := Normalize(env)
	if err == nil {
		t.Fatal("expected error for bad date")
	}
}

func TestNormalize_PrefixNormalization(t *testing.T) {
	env := goodUnpublishEnvelope("openinfo")
	req, err := Normalize(env)
	if err != nil {
		t.Fatalf("Normalize: %v", err)
	}
	want := "openinfo/EDU-2024-12345/"
	if req.PublicRepository.Prefix != want {
		t.Errorf("Prefix = %q, want %q", req.PublicRepository.Prefix, want)
	}
}

func TestNormalize_FOIIDs_PresentWhenProvided(t *testing.T) {
	payload, _ := json.Marshal(map[string]any{
		"tenant_id":             "tenant-1",
		"publication_id":        "EDU-2024-12345",
		"public_url":            "https://example/public/EDU-2024-12345.html",
		"public_repository":     map[string]string{"bucket": "public-bucket", "prefix": "openinfo/EDU-2024-12345"},
		"last_modified":         "2026-04-27",
		"kind":                  "openinfo",
		"foiministryrequest_id": 22318,
		"foirequest_id":         22319,
	})
	env := &events.Envelope{
		EventID:       "event-1",
		EventType:     events.TypePublicationUnpublishRequested,
		SchemaVersion: events.SchemaVersionV1,
		CorrelationID: "corr-1",
		Source:        "test",
		Payload:       payload,
	}
	req, err := Normalize(env)
	if err != nil {
		t.Fatalf("Normalize: %v", err)
	}
	if req.FOIMinistryRequestID == nil || *req.FOIMinistryRequestID != 22318 {
		t.Errorf("FOIMinistryRequestID = %v, want 22318", req.FOIMinistryRequestID)
	}
	if req.FOIRequestID == nil || *req.FOIRequestID != 22319 {
		t.Errorf("FOIRequestID = %v, want 22319", req.FOIRequestID)
	}
}

func TestNormalize_FOIIDs_NilWhenAbsent(t *testing.T) {
	env := goodUnpublishEnvelope("openinfo")
	req, err := Normalize(env)
	if err != nil {
		t.Fatalf("Normalize: %v", err)
	}
	if req.FOIMinistryRequestID != nil {
		t.Errorf("FOIMinistryRequestID = %v, want nil", req.FOIMinistryRequestID)
	}
	if req.FOIRequestID != nil {
		t.Errorf("FOIRequestID = %v, want nil", req.FOIRequestID)
	}
}
