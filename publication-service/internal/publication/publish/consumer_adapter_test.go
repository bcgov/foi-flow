package publish

import (
	"context"
	"encoding/json"
	"errors"
	"testing"

	"publication-service/internal/events"
	pub "publication-service/internal/publish"
	"publication-service/internal/sitemapping"
)

type fakePublisher struct {
	result pub.PublishResult
	err    error
}

func (f *fakePublisher) Handle(_ context.Context, _ *Domain) (pub.PublishResult, error) {
	return f.result, f.err
}

type fakeSitemapWriter struct {
	result sitemapping.Result
	err    error
}

func (f *fakeSitemapWriter) Handle(_ context.Context, _ sitemapping.Request) (sitemapping.Result, error) {
	return f.result, f.err
}

func TestConsumerAdapter_OpenInfoCompletionEventType(t *testing.T) {
	adapter := NewCompletionAdapter(
		&fakePublisher{result: pub.PublishResult{PublicationID: "X"}},
		&fakeSitemapWriter{},
	)
	env := goodEnvelope()
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
	if completion.EventType != events.TypePublicationPublishCompleted {
		t.Errorf("EventType = %q", completion.EventType)
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
}

func TestConsumerAdapter_HandlerPropagatesError(t *testing.T) {
	adapter := NewCompletionAdapter(
		&fakePublisher{err: errors.New("boom")},
		nil,
	)
	env := goodEnvelope()
	_, handler, _, err := adapter.Normalize(env)
	if err != nil {
		t.Fatalf("Normalize: %v", err)
	}
	if err := handler(context.Background()); err == nil {
		t.Fatal("expected error")
	}
}

func TestConsumerAdapter_KindInClaimInfo(t *testing.T) {
	adapter := NewCompletionAdapter(
		&fakePublisher{result: pub.PublishResult{PublicationID: "X"}},
		&fakeSitemapWriter{},
	)
	env := goodEnvelope()
	info, _, _, err := adapter.Normalize(env)
	if err != nil {
		t.Fatalf("Normalize: %v", err)
	}
	if info.Kind != pub.KindOpenInfo {
		t.Errorf("ClaimInfo.Kind = %q, want %q", info.Kind, pub.KindOpenInfo)
	}

	env.Payload = goodPDPayload()
	info, _, _, err = adapter.Normalize(env)
	if err != nil {
		t.Fatalf("Normalize PD: %v", err)
	}
	if info.Kind != pub.KindProactiveDisclosure {
		t.Errorf("ClaimInfo.Kind = %q, want %q", info.Kind, pub.KindProactiveDisclosure)
	}
}

func TestConsumerAdapter_FOIIDsInCompletionPayload(t *testing.T) {
	adapter := NewCompletionAdapter(
		&fakePublisher{result: pub.PublishResult{PublicationID: "X"}},
		&fakeSitemapWriter{},
	)
	env := goodEnvelope()
	env.Payload = json.RawMessage(`{
		"tenant_id":       "a7d9b2f1-4c3e-4e8b-9a21-1c2e8f7b9d10",
		"source":          {"bucket": "foi-raw",       "prefix": "incoming/a7d9b2f1/"},
		"destination":     {"bucket": "foi-published", "prefix": "out/a7d9b2f1/"},
		"axis_request_id": "HTH-2025-52023",
		"kind":            "openinfo",
		"published_date":  "2025-04-01",
		"foiministryrequest_id": 22318,
		"foirequest_id": 22319
	}`)

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
	var payload map[string]any
	if err := json.Unmarshal(completion.Payload, &payload); err != nil {
		t.Fatalf("unmarshal payload: %v", err)
	}
	if v, ok := payload["foiministryrequest_id"]; !ok {
		t.Error("missing foiministryrequest_id in completion payload")
	} else if int(v.(float64)) != 22318 {
		t.Errorf("foiministryrequest_id = %v, want 22318", v)
	}
	if v, ok := payload["foirequest_id"]; !ok {
		t.Error("missing foirequest_id in completion payload")
	} else if int(v.(float64)) != 22319 {
		t.Errorf("foirequest_id = %v, want 22319", v)
	}
}
