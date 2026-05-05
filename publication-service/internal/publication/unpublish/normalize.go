package unpublish

import (
	"encoding/json"
	"fmt"
	"time"

	"publication-service/internal/events"
	pub "publication-service/internal/publish"
	shared "publication-service/internal/unpublish"
)

type requestedPayloadV1 struct {
	TenantID         string `json:"tenant_id"`
	PublicationID    string `json:"publication_id"`
	PublicURL        string `json:"public_url"`
	PublicRepository struct {
		Bucket string `json:"bucket"`
		Prefix string `json:"prefix"`
	} `json:"public_repository"`
	LastModified         string `json:"last_modified"`
	Kind                 string `json:"kind"`
	FOIMinistryRequestID *int   `json:"foiministryrequest_id"`
	FOIRequestID         *int   `json:"foirequest_id"`
}

func Normalize(env *events.Envelope) (shared.Request, error) {
	if env.SchemaVersion != events.SchemaVersionV1 {
		return shared.Request{}, pub.NewPermanent(fmt.Sprintf("publication.unpublish: unsupported schema_version %q", env.SchemaVersion))
	}
	var p requestedPayloadV1
	if err := json.Unmarshal(env.Payload, &p); err != nil {
		return shared.Request{}, fmt.Errorf("publication.unpublish: payload: %w", err)
	}
	lastModified, err := time.Parse("2006-01-02", p.LastModified)
	if err != nil {
		return shared.Request{}, pub.NewPermanent("publication.unpublish: last_modified must be YYYY-MM-DD")
	}
	kind, err := parseUnpublishKind(p.Kind)
	if err != nil {
		return shared.Request{}, err
	}
	return shared.NormalizeRequest(shared.Request{
		Kind:          kind,
		TenantID:      p.TenantID,
		PublicationID: p.PublicationID,
		PublicURL:     p.PublicURL,
		PublicRepository: shared.PublicRepositoryLocation{
			Bucket: p.PublicRepository.Bucket,
			Prefix: p.PublicRepository.Prefix,
		},
		LastModified:         lastModified,
		SourceEventID:        env.EventID,
		CorrelationID:        env.CorrelationID,
		FOIMinistryRequestID: p.FOIMinistryRequestID,
		FOIRequestID:         p.FOIRequestID,
	})
}

func parseUnpublishKind(raw string) (pub.Kind, error) {
	switch raw {
	case "openinfo":
		return pub.KindOpenInfoUnpublish, nil
	case "proactivedisclosure":
		return pub.KindProactiveDisclosureUnpublish, nil
	default:
		return pub.KindUnknown, pub.NewPermanent(fmt.Sprintf("publication.unpublish: unknown kind %q", raw))
	}
}
