package publish

import (
	"encoding/json"
	"fmt"

	"github.com/santhosh-tekuri/jsonschema/v5"

	"publication-service/internal/events"
	pub "publication-service/internal/publish"
)

// Validator runs envelope-level checks: type whitelist, source allowlist,
// payload schema. All failures are PermanentError.
type Validator struct {
	expectedType string
	allowSources map[string]struct{}
	schema       *jsonschema.Schema
}

// NewValidator constructs a Validator for one event_type with a fixed source allowlist.
func NewValidator(eventType string, allowedSources []string) (*Validator, error) {
	schema, err := events.SchemaFor(eventType, events.SchemaVersionV1)
	if err != nil {
		return nil, fmt.Errorf("publish: validator schema: %w", err)
	}
	src := make(map[string]struct{}, len(allowedSources))
	for _, s := range allowedSources {
		src[s] = struct{}{}
	}
	return &Validator{
		expectedType: eventType,
		allowSources: src,
		schema:       schema,
	}, nil
}

// Validate returns a PermanentError on any rule violation.
func (v *Validator) Validate(env *events.Envelope) error {
	if env.EventType != v.expectedType {
		return pub.NewPermanent(fmt.Sprintf("event_type %q not allowed on this stream", env.EventType))
	}
	if _, ok := v.allowSources[env.Source]; !ok {
		return pub.NewPermanent(fmt.Sprintf("source %q not in allowlist", env.Source))
	}
	if env.SchemaVersion != events.SchemaVersionV1 {
		return pub.NewPermanent(fmt.Sprintf("schema_version %q unsupported", env.SchemaVersion))
	}
	var payload any
	if err := json.Unmarshal(env.Payload, &payload); err != nil {
		return pub.NewPermanent(fmt.Sprintf("payload not valid JSON: %v", err))
	}
	if err := v.schema.Validate(payload); err != nil {
		return pub.NewPermanent(fmt.Sprintf("payload schema violation: %v", err))
	}
	return nil
}
