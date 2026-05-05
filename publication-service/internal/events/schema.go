package events

import (
	"bytes"
	"embed"
	"fmt"

	"github.com/santhosh-tekuri/jsonschema/v5"
)

//go:embed schema/*.json
var schemaFS embed.FS

// SchemaFor returns the compiled JSON Schema for an (event_type, version) pair.
func SchemaFor(eventType, version string) (*jsonschema.Schema, error) {
	if version != SchemaVersionV1 {
		return nil, fmt.Errorf("events: unsupported schema_version %q", version)
	}
	name, ok := schemaFileFor(eventType)
	if !ok {
		return nil, fmt.Errorf("events: unknown event_type %q", eventType)
	}
	raw, err := schemaFS.ReadFile("schema/" + name)
	if err != nil {
		return nil, fmt.Errorf("events: read schema: %w", err)
	}
	c := jsonschema.NewCompiler()
	if err := c.AddResource(name, bytes.NewReader(raw)); err != nil {
		return nil, fmt.Errorf("events: add resource: %w", err)
	}
	return c.Compile(name)
}

func schemaFileFor(eventType string) (string, bool) {
	switch eventType {
	case TypePublicationPublishRequested:
		return "publication.publish.requested.v1.json", true
	case TypePublicationPublishCompleted:
		return "publication.publish.completed.v1.json", true
	case TypePublicationSitemappingRequested:
		return "publication.sitemapping.requested.v1.json", true
	case TypePublicationSitemappingCompleted:
		return "publication.sitemapping.completed.v1.json", true
	case TypePublicationUnpublishRequested:
		return "publication.unpublish.requested.v1.json", true
	case TypePublicationUnpublishCompleted:
		return "publication.unpublish.completed.v1.json", true
	}
	return "", false
}
