package sitemapping

import (
	"context"
	"encoding/json"
	"errors"
	"testing"

	"publication-service/internal/events"
	pub "publication-service/internal/publish"
	"publication-service/internal/sitemapping"
)

type fakeWriter struct {
	result sitemapping.Result
	err    error
}

func (f *fakeWriter) Handle(_ context.Context, _ sitemapping.Request) (sitemapping.Result, error) {
	return f.result, f.err
}

func TestConsumerAdapter_CompletionEventType(t *testing.T) {
	adapter := NewNormalizerAdapter(&fakeWriter{
		result: sitemapping.Result{TenantID: "t1", PublicationID: "P1", Kind: pub.KindOpenInfoSitemap},
	})
	env := goodSitemapEnvelope("openinfo")
	env.CorrelationID = "corr-123"

	_, handler, buildCompletion, err := adapter.Normalize(env)
	if err != nil {
		t.Fatalf("Normalize: %v", err)
	}
	if err := handler(context.Background()); err != nil {
		t.Fatalf("handler: %v", err)
	}

	_, completionBytes, err := buildCompletion()
	if err != nil {
		t.Fatalf("buildCompletion: %v", err)
	}
	var completion events.Envelope
	if err := json.Unmarshal(completionBytes, &completion); err != nil {
		t.Fatalf("unmarshal: %v", err)
	}
	if completion.EventType != events.TypePublicationSitemappingCompleted {
		t.Errorf("EventType = %q, want %q", completion.EventType, events.TypePublicationSitemappingCompleted)
	}
	if completion.Source != "publication.sitemapping.service" {
		t.Errorf("Source = %q, want %q", completion.Source, "publication.sitemapping.service")
	}
	if completion.CorrelationID != "corr-123" {
		t.Errorf("CorrelationID = %q", completion.CorrelationID)
	}
	var payload map[string]any
	if err := json.Unmarshal(completion.Payload, &payload); err != nil {
		t.Fatalf("unmarshal payload: %v", err)
	}
	if payload["kind"] != "openinfo" {
		t.Errorf("kind = %v, want openinfo", payload["kind"])
	}
	if _, ok := payload["foiministryrequest_id"]; ok {
		t.Error("foiministryrequest_id should be absent when not provided")
	}
	if _, ok := payload["foirequest_id"]; ok {
		t.Error("foirequest_id should be absent when not provided")
	}
}

func TestConsumerAdapter_KindInClaimInfo(t *testing.T) {
	adapter := NewNormalizerAdapter(&fakeWriter{})

	env := goodSitemapEnvelope("openinfo")
	info, _, _, err := adapter.Normalize(env)
	if err != nil {
		t.Fatalf("Normalize OI: %v", err)
	}
	if info.Kind != pub.KindOpenInfoSitemap {
		t.Errorf("ClaimInfo.Kind = %q, want %q", info.Kind, pub.KindOpenInfoSitemap)
	}

	env = goodSitemapEnvelope("proactivedisclosure")
	info, _, _, err = adapter.Normalize(env)
	if err != nil {
		t.Fatalf("Normalize PD: %v", err)
	}
	if info.Kind != pub.KindProactiveDisclosureSitemap {
		t.Errorf("ClaimInfo.Kind = %q, want %q", info.Kind, pub.KindProactiveDisclosureSitemap)
	}
}

func TestConsumerAdapter_HandlerPropagatesError(t *testing.T) {
	adapter := NewNormalizerAdapter(&fakeWriter{err: errors.New("boom")})
	env := goodSitemapEnvelope("openinfo")
	_, handler, _, err := adapter.Normalize(env)
	if err != nil {
		t.Fatalf("Normalize: %v", err)
	}
	if err := handler(context.Background()); err == nil {
		t.Fatal("expected error")
	}
}

func TestConsumerAdapter_FOIIDsInCompletionPayload(t *testing.T) {
	adapter := NewNormalizerAdapter(&fakeWriter{
		result: sitemapping.Result{TenantID: "t1", PublicationID: "P1", Kind: pub.KindOpenInfoSitemap},
	})
	payload, _ := json.Marshal(map[string]any{
		"tenant_id":              "a7d9b2f1-4c3e-4e8b-9a21-1c2e8f7b9d10",
		"publication_id":         "HTH-001",
		"public_url":             "https://public.example/foi-published/out/a7d9b2f1/HTH-001.html",
		"last_modified":          "2025-04-01",
		"publication_result_ref": "ref-123",
		"kind":                   "openinfo",
		"foiministryrequest_id":  22318,
		"foirequest_id":          22319,
	})
	env := &events.Envelope{
		EventID:       "evt-sm-001",
		EventType:     events.TypePublicationSitemappingRequested,
		SchemaVersion: events.SchemaVersionV1,
		CorrelationID: "corr-sm-001",
		Source:        "test",
		Payload:       payload,
	}

	_, handler, buildCompletion, err := adapter.Normalize(env)
	if err != nil {
		t.Fatalf("Normalize: %v", err)
	}
	if err := handler(context.Background()); err != nil {
		t.Fatalf("handler: %v", err)
	}

	_, completionBytes, err := buildCompletion()
	if err != nil {
		t.Fatalf("buildCompletion: %v", err)
	}
	var completion events.Envelope
	if err := json.Unmarshal(completionBytes, &completion); err != nil {
		t.Fatalf("unmarshal: %v", err)
	}
	var completionPayload map[string]any
	if err := json.Unmarshal(completion.Payload, &completionPayload); err != nil {
		t.Fatalf("unmarshal payload: %v", err)
	}
	if v, ok := completionPayload["foiministryrequest_id"]; !ok {
		t.Error("missing foiministryrequest_id")
	} else if int(v.(float64)) != 22318 {
		t.Errorf("foiministryrequest_id = %v, want 22318", v)
	}
	if v, ok := completionPayload["foirequest_id"]; !ok {
		t.Error("missing foirequest_id")
	} else if int(v.(float64)) != 22319 {
		t.Errorf("foirequest_id = %v, want 22319", v)
	}
}
