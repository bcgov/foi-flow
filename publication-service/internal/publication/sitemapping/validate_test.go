package sitemapping

import (
	"testing"

	pub "publication-service/internal/publish"
)

func TestValidator_AcceptsValidSitemappingEnvelope(t *testing.T) {
	v, err := NewValidator([]string{"test"})
	if err != nil {
		t.Fatalf("NewValidator: %v", err)
	}
	env := goodSitemapEnvelope("openinfo")
	if err := v.Validate(env); err != nil {
		t.Fatalf("Validate: %v", err)
	}
}

func TestValidator_RejectsWrongEventType(t *testing.T) {
	v, err := NewValidator([]string{"test"})
	if err != nil {
		t.Fatalf("NewValidator: %v", err)
	}
	env := goodSitemapEnvelope("openinfo")
	env.EventType = "wrong.type"
	if err := v.Validate(env); err == nil {
		t.Fatal("expected error for wrong event_type")
	} else if _, ok := err.(*pub.PermanentError); !ok {
		t.Fatalf("expected *PermanentError, got %T", err)
	}
}

func TestValidator_RejectsUnknownSource(t *testing.T) {
	v, err := NewValidator([]string{"allowed"})
	if err != nil {
		t.Fatalf("NewValidator: %v", err)
	}
	env := goodSitemapEnvelope("openinfo")
	env.Source = "not-allowed"
	if err := v.Validate(env); err == nil {
		t.Fatal("expected error for unknown source")
	} else if _, ok := err.(*pub.PermanentError); !ok {
		t.Fatalf("expected *PermanentError, got %T", err)
	}
}
