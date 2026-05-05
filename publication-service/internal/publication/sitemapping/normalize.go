package sitemapping

import (
	"encoding/json"
	"fmt"
	"time"

	"publication-service/internal/events"
	pub "publication-service/internal/publish"
	shared "publication-service/internal/sitemapping"
)

type requestedPayloadV1 struct {
	TenantID             string `json:"tenant_id"`
	PublicationID        string `json:"publication_id"`
	PublicURL            string `json:"public_url"`
	LastModified         string `json:"last_modified"`
	PublicationResultRef string `json:"publication_result_ref"`
	Kind                 string `json:"kind"`
	FOIMinistryRequestID *int   `json:"foiministryrequest_id"`
	FOIRequestID         *int   `json:"foirequest_id"`
}

func Normalize(env *events.Envelope) (shared.Request, error) {
	if env.SchemaVersion != events.SchemaVersionV1 {
		return shared.Request{}, pub.NewPermanent(fmt.Sprintf("publication.sitemapping: unsupported schema_version %q", env.SchemaVersion))
	}
	var p requestedPayloadV1
	if err := json.Unmarshal(env.Payload, &p); err != nil {
		return shared.Request{}, fmt.Errorf("publication.sitemapping: payload: %w", err)
	}
	lastModified, err := time.Parse("2006-01-02", p.LastModified)
	if err != nil {
		return shared.Request{}, pub.NewPermanent("publication.sitemapping: last_modified must be YYYY-MM-DD")
	}
	kind, err := parseSitemapKind(p.Kind)
	if err != nil {
		return shared.Request{}, err
	}
	return shared.Request{
		Kind:                 kind,
		TenantID:             p.TenantID,
		PublicationID:        p.PublicationID,
		PublicURL:            p.PublicURL,
		LastModified:         lastModified,
		PublicationResultRef: p.PublicationResultRef,
		SourceEventID:        env.EventID,
		CorrelationID:        env.CorrelationID,
		FOIMinistryRequestID: p.FOIMinistryRequestID,
		FOIRequestID:         p.FOIRequestID,
	}, nil
}

func parseSitemapKind(raw string) (pub.Kind, error) {
	switch raw {
	case "openinfo":
		return pub.KindOpenInfoSitemap, nil
	case "proactivedisclosure":
		return pub.KindProactiveDisclosureSitemap, nil
	default:
		return pub.KindUnknown, pub.NewPermanent(fmt.Sprintf("publication.sitemapping: unknown kind %q", raw))
	}
}
