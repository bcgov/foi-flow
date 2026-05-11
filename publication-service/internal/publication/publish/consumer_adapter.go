package publish

import (
	"context"
	"encoding/json"
	"time"

	"github.com/google/uuid"

	"publication-service/internal/events"
	"publication-service/internal/messaging"
	pub "publication-service/internal/publish"
	"publication-service/internal/publishcompletion"
	"publication-service/internal/sitemapping"
)

type publishServiceIface interface {
	Handle(context.Context, *Domain) (pub.PublishResult, error)
}

type sitemapWriterIface interface {
	Handle(context.Context, sitemapping.Request) (sitemapping.Result, error)
}

// NormalizerAdapter implements messaging.EnvelopeNormalizer for the unified publication pipeline.
type NormalizerAdapter struct {
	svc     publishServiceIface
	sitemap sitemapWriterIface
}

// NewNormalizerAdapter constructs a NormalizerAdapter wrapping the given Service.
func NewNormalizerAdapter(svc *Service) *NormalizerAdapter {
	return &NormalizerAdapter{svc: svc}
}

// NewCompletionAdapter constructs a NormalizerAdapter with sitemap support.
func NewCompletionAdapter(svc publishServiceIface, sitemap sitemapWriterIface) *NormalizerAdapter {
	return &NormalizerAdapter{svc: svc, sitemap: sitemap}
}

// Normalize implements messaging.EnvelopeNormalizer.
func (a *NormalizerAdapter) Normalize(env *events.Envelope) (
	messaging.ClaimInfo, messaging.HandlerFunc, messaging.CompletionBuilder, error,
) {
	d, err := Normalize(env)
	if err != nil {
		return messaging.ClaimInfo{}, nil, nil, err
	}

	info := messaging.ClaimInfo{
		EventID:       d.EventID,
		TenantID:      d.TenantID,
		CorrelationID: d.CorrelationID,
		Kind:          d.Kind,
	}

	var publishResult pub.PublishResult
	var sitemapResult sitemapping.Result

	sitemapKind := sitemapKindFor(d.Kind)

	handler := messaging.HandlerFunc(func(ctx context.Context) error {
		result, err := a.svc.Handle(ctx, d)
		if err != nil {
			return err
		}
		publishResult = result
		if a.sitemap == nil {
			return nil
		}
		req, err := publishcompletion.SitemapRequest(sitemapKind, d.TenantID, d.CorrelationID, d.EventID, result, d.PublishedDate)
		if err != nil {
			return err
		}
		sitemapResult, err = a.sitemap.Handle(ctx, req)
		return err
	})

	completion := messaging.CompletionBuilder(func() (string, []byte, error) {
		payload, err := publishcompletion.BuildPayload(d.TenantID, d.EventID, d.CorrelationID, d.FOIMinistryRequestID, d.FOIRequestID, publishResult, sitemapResult)
		if err != nil {
			return "", nil, err
		}
		// Add kind to payload so downstream consumers can distinguish OI vs PD.
		var payloadMap map[string]any
		if err := json.Unmarshal(payload, &payloadMap); err != nil {
			return "", nil, err
		}
		payloadMap["kind"] = kindToPayloadKind(d.Kind)
		payload, err = json.Marshal(payloadMap)
		if err != nil {
			return "", nil, err
		}
		completionEventID := uuid.NewString()
		out := events.Envelope{
			EventID:       completionEventID,
			EventType:     events.TypePublicationPublishCompleted,
			Timestamp:     time.Now().UTC(),
			SchemaVersion: events.SchemaVersionV1,
			CorrelationID: d.CorrelationID,
			Source:        "publication.publish.service",
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

func sitemapKindFor(k pub.Kind) pub.Kind {
	switch k {
	case pub.KindProactiveDisclosure:
		return pub.KindProactiveDisclosureSitemap
	default:
		return pub.KindOpenInfoSitemap
	}
}

func kindToPayloadKind(k pub.Kind) string {
	switch k {
	case pub.KindProactiveDisclosure:
		return "proactivedisclosure"
	default:
		return "openinfo"
	}
}
