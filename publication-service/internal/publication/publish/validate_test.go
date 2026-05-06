package publish

import (
	"encoding/json"
	"testing"

	"publication-service/internal/events"
	pub "publication-service/internal/publish"
)

func TestValidator_AcceptsValidOpenInfoEnvelope(t *testing.T) {
	v, err := NewValidator(events.TypePublicationPublishRequested, []string{"test"})
	if err != nil {
		t.Fatalf("NewValidator: %v", err)
	}
	env := goodEnvelope()
	if err := v.Validate(env); err != nil {
		t.Fatalf("Validate: %v", err)
	}
}

func TestValidator_AcceptsValidPDEnvelope(t *testing.T) {
	v, err := NewValidator(events.TypePublicationPublishRequested, []string{"test"})
	if err != nil {
		t.Fatalf("NewValidator: %v", err)
	}
	env := goodEnvelope()
	env.Payload = goodPDPayload()
	if err := v.Validate(env); err != nil {
		t.Fatalf("Validate: %v", err)
	}
}

func TestValidator_RejectsWrongEventType(t *testing.T) {
	v, err := NewValidator(events.TypePublicationPublishRequested, []string{"test"})
	if err != nil {
		t.Fatalf("NewValidator: %v", err)
	}
	env := goodEnvelope()
	env.EventType = "wrong.type"
	if err := v.Validate(env); err == nil {
		t.Fatal("expected error for wrong event_type")
	} else if _, ok := err.(*pub.PermanentError); !ok {
		t.Fatalf("expected *PermanentError, got %T", err)
	}
}

func TestValidator_RejectsUnknownSource(t *testing.T) {
	v, err := NewValidator(events.TypePublicationPublishRequested, []string{"allowed"})
	if err != nil {
		t.Fatalf("NewValidator: %v", err)
	}
	env := goodEnvelope()
	env.Source = "not-allowed"
	if err := v.Validate(env); err == nil {
		t.Fatal("expected error for unknown source")
	} else if _, ok := err.(*pub.PermanentError); !ok {
		t.Fatalf("expected *PermanentError, got %T", err)
	}
}

func TestValidator_RejectsInvalidPayload(t *testing.T) {
	v, err := NewValidator(events.TypePublicationPublishRequested, []string{"test"})
	if err != nil {
		t.Fatalf("NewValidator: %v", err)
	}
	env := goodEnvelope()
	env.Payload = json.RawMessage(`{"tenant_id": 123}`) // wrong type for tenant_id
	if err := v.Validate(env); err == nil {
		t.Fatal("expected schema violation")
	}
}
