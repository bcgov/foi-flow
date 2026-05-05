package unpublish

import (
	"context"
	"encoding/json"
	"time"

	"github.com/google/uuid"

	"publication-service/internal/events"
	"publication-service/internal/messaging"
	pub "publication-service/internal/publish"
	shared "publication-service/internal/unpublish"
)

type Service interface {
	Handle(context.Context, shared.Request) (shared.Result, error)
}

type NormalizerAdapter struct {
	service Service
}

func NewNormalizerAdapter(service Service) *NormalizerAdapter {
	return &NormalizerAdapter{service: service}
}

func (a *NormalizerAdapter) Normalize(env *events.Envelope) (
	messaging.ClaimInfo, messaging.HandlerFunc, messaging.CompletionBuilder, error,
) {
	req, err := Normalize(env)
	if err != nil {
		return messaging.ClaimInfo{}, nil, nil, err
	}
	info := messaging.ClaimInfo{
		EventID:       req.SourceEventID,
		TenantID:      req.TenantID,
		CorrelationID: req.CorrelationID,
		Kind:          req.Kind,
	}
	var result shared.Result
	handler := messaging.HandlerFunc(func(ctx context.Context) error {
		got, err := a.service.Handle(ctx, req)
		if err != nil {
			return err
		}
		result = got
		return nil
	})
	completion := messaging.CompletionBuilder(func() (string, []byte, error) {
		payload, err := json.Marshal(completionPayload(req, result))
		if err != nil {
			return "", nil, err
		}
		completionEventID := uuid.NewString()
		out := events.Envelope{
			EventID:       completionEventID,
			EventType:     events.TypePublicationUnpublishCompleted,
			Timestamp:     time.Now().UTC(),
			SchemaVersion: events.SchemaVersionV1,
			CorrelationID: req.CorrelationID,
			Source:        "publication.unpublish.service",
			Payload:       payload,
			Meta:          events.Meta{FirstSeenAt: time.Now().UTC()},
		}
		b, err := json.Marshal(out)
		if err != nil {
			return "", nil, err
		}
		return completionEventID, b, nil
	})
	return info, handler, completion, nil
}

func completionPayload(req shared.Request, result shared.Result) map[string]any {
	m := map[string]any{
		"tenant_id":                result.TenantID,
		"publication_id":           result.PublicationID,
		"request_event_id":         req.SourceEventID,
		"status":                   "completed",
		"public_repository_bucket": result.PublicRepositoryBucket,
		"public_repository_prefix": result.PublicRepositoryPrefix,
		"objects_deleted":          result.ObjectsDeleted,
		"sitemap_index_key":        result.SitemapIndexKey,
		"sitemap_page_key":         result.SitemapPageKey,
		"sitemap_result":           result.SitemapResult,
		"kind":                     kindToPayloadKind(req.Kind),
	}
	if req.FOIMinistryRequestID != nil {
		m["foiministryrequest_id"] = *req.FOIMinistryRequestID
	}
	if req.FOIRequestID != nil {
		m["foirequest_id"] = *req.FOIRequestID
	}
	return m
}

func kindToPayloadKind(k pub.Kind) string {
	switch k {
	case pub.KindProactiveDisclosureUnpublish:
		return "proactivedisclosure"
	default:
		return "openinfo"
	}
}
