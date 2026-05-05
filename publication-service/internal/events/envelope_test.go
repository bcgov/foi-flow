package events

import (
	"encoding/json"
	"testing"
	"time"
)

func TestEnvelope_RoundTrip(t *testing.T) {
	raw := []byte(`{
      "event_id": "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d90",
      "event_type": "openinfo.publish.requested",
      "timestamp": "2026-04-15T14:32:15Z",
      "schema_version": "1.0.0",
      "correlation_id": "req-9f4e1c7b-3c52-4f7a",
      "source": "openinfo.enqueue.service",
      "payload": {"tenant_id": "a7d9b2f1-4c3e-4e8b-9a21-1c2e8f7b9d10"},
      "meta": {"retry_count": 0, "first_seen_at": "2026-04-15T14:32:15Z"}
    }`)

	env, err := UnmarshalEnvelope(raw)
	if err != nil {
		t.Fatalf("UnmarshalEnvelope: %v", err)
	}
	if env.EventID != "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d90" {
		t.Errorf("EventID = %q", env.EventID)
	}
	if env.EventType != "openinfo.publish.requested" {
		t.Errorf("EventType = %q", env.EventType)
	}
	if env.Source != "openinfo.enqueue.service" {
		t.Errorf("Source = %q", env.Source)
	}
	if env.Meta.RetryCount != 0 {
		t.Errorf("Meta.RetryCount = %d", env.Meta.RetryCount)
	}
	if want := time.Date(2026, 4, 15, 14, 32, 15, 0, time.UTC); !env.Timestamp.Equal(want) {
		t.Errorf("Timestamp = %v want %v", env.Timestamp, want)
	}

	out, err := json.Marshal(env)
	if err != nil {
		t.Fatalf("Marshal: %v", err)
	}
	var roundtrip Envelope
	if err := json.Unmarshal(out, &roundtrip); err != nil {
		t.Fatalf("re-Unmarshal: %v", err)
	}
	if roundtrip.EventID != env.EventID {
		t.Error("round-trip EventID mismatch")
	}
}

func TestUnmarshalEnvelope_RejectsInvalidJSON(t *testing.T) {
	if _, err := UnmarshalEnvelope([]byte("not-json")); err == nil {
		t.Fatal("expected error")
	}
}
