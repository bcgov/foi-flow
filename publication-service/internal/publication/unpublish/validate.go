package unpublish

import (
	"encoding/json"
	"fmt"

	"github.com/santhosh-tekuri/jsonschema/v5"

	"publication-service/internal/events"
	pub "publication-service/internal/publish"
)

type Validator struct {
	allowSources map[string]struct{}
	schema       *jsonschema.Schema
}

func NewValidator(allowedSources []string) (*Validator, error) {
	schema, err := events.SchemaFor(events.TypePublicationUnpublishRequested, events.SchemaVersionV1)
	if err != nil {
		return nil, fmt.Errorf("publication.unpublish: validator schema: %w", err)
	}
	src := make(map[string]struct{}, len(allowedSources))
	for _, s := range allowedSources {
		src[s] = struct{}{}
	}
	return &Validator{allowSources: src, schema: schema}, nil
}

func (v *Validator) Validate(env *events.Envelope) error {
	if env.EventType != events.TypePublicationUnpublishRequested {
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
