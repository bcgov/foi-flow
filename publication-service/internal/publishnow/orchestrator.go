package publishnow

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"time"

	"github.com/google/uuid"

	"publication-service/internal/events"
	pubpub "publication-service/internal/publication/publish"
	pub "publication-service/internal/publish"
	"publication-service/internal/publishcompletion"
	"publication-service/internal/sitemapping"
)

const restSource = "publication-service.rest"

type PublicationType string

const (
	PublicationTypeOpenInfo            PublicationType = "openinfo"
	PublicationTypeProactiveDisclosure PublicationType = "proactivedisclosure"
)

type Request struct {
	PublicationType PublicationType `json:"publication_type"`
	Payload         json.RawMessage `json:"payload"`
}

type Response struct {
	Status          string `json:"status"`
	PublicationType string `json:"publication_type"`
	PublicationID   string `json:"publication_id"`
	PublicURL       string `json:"public_url"`
	HTMLKey         string `json:"html_key"`
	SitemapIndexKey string `json:"sitemap_index_key"`
	SitemapPageKey  string `json:"sitemap_page_key"`
	SitemapResult   string `json:"sitemap_result"`
}

type publisher interface {
	Handle(context.Context, *pubpub.Domain) (pub.PublishResult, error)
}

type sitemapWriter interface {
	Handle(context.Context, sitemapping.Request) (sitemapping.Result, error)
}

type sitemapClaimer interface {
	Claim(context.Context, pub.ClaimRequest) (pub.ClaimResult, error)
}

type Orchestrator struct {
	publisher      publisher
	sitemap        sitemapWriter
	sitemapClaimer sitemapClaimer
	now            func() time.Time
}

func New(pub publisher, sitemap sitemapWriter) *Orchestrator {
	return &Orchestrator{
		publisher: pub,
		sitemap:   sitemap,
		now:       func() time.Time { return time.Now().UTC() },
	}
}

func (o *Orchestrator) WithSitemapClaimer(claimer sitemapClaimer) *Orchestrator {
	o.sitemapClaimer = claimer
	return o
}

func (o *Orchestrator) Publish(ctx context.Context, body []byte) (Response, error) {
	var req Request
	if err := json.Unmarshal(body, &req); err != nil {
		return Response{}, clientError{err: fmt.Errorf("malformed JSON: %w", err)}
	}
	if len(req.Payload) == 0 || string(req.Payload) == "null" {
		return Response{}, clientError{err: errors.New("payload is required")}
	}

	switch req.PublicationType {
	case PublicationTypeOpenInfo, PublicationTypeProactiveDisclosure:
		return o.publish(ctx, string(req.PublicationType), req.Payload)
	default:
		return Response{}, clientError{err: fmt.Errorf("unsupported publication_type %q", req.PublicationType)}
	}
}

func (o *Orchestrator) publish(ctx context.Context, pubType string, payload json.RawMessage) (Response, error) {
	env := newEnvelope(events.TypePublicationPublishRequested, payload, o.now())
	validator, err := pubpub.NewValidator(events.TypePublicationPublishRequested, []string{restSource})
	if err != nil {
		return Response{}, err
	}
	if err := validator.Validate(env); err != nil {
		return Response{}, clientError{err: err}
	}
	d, err := pubpub.Normalize(env)
	if err != nil {
		return Response{}, clientError{err: err}
	}
	result, err := o.publisher.Handle(ctx, d)
	if err != nil {
		return Response{}, err
	}
	sitemapKind := pub.KindOpenInfoSitemap
	if d.Kind == pub.KindProactiveDisclosure {
		sitemapKind = pub.KindProactiveDisclosureSitemap
	}
	sitemapReq, err := publishcompletion.SitemapRequest(sitemapKind, d.TenantID, d.CorrelationID, env.EventID, result, d.PublishedDate)
	if err != nil {
		return Response{}, clientError{err: err}
	}
	if err := o.claimSitemap(ctx, sitemapReq); err != nil {
		return Response{}, err
	}
	sitemapResult, err := o.sitemap.Handle(ctx, sitemapReq)
	if err != nil {
		return Response{}, err
	}
	return response(pubType, result, sitemapResult), nil
}

func (o *Orchestrator) claimSitemap(ctx context.Context, req sitemapping.Request) error {
	if o.sitemapClaimer == nil {
		return nil
	}
	payload, err := sitemapPayload(req)
	if err != nil {
		return err
	}
	claim, err := o.sitemapClaimer.Claim(ctx, pub.ClaimRequest{
		EventID:       req.SourceEventID,
		EventType:     sitemapEventType(req.Kind),
		TenantID:      req.TenantID,
		CorrelationID: req.CorrelationID,
		SchemaVersion: events.SchemaVersionV1,
		Payload:       payload,
		Now:           o.now(),
		Kind:          req.Kind,
	})
	if err != nil {
		if pub.IsDuplicate(err) {
			return nil
		}
		return err
	}
	if !claim.Won {
		return fmt.Errorf("sitemap request %s was already claimed", req.SourceEventID)
	}
	return nil
}

func sitemapPayload(req sitemapping.Request) (json.RawMessage, error) {
	payload, err := json.Marshal(map[string]string{
		"tenant_id":              req.TenantID,
		"publication_id":         req.PublicationID,
		"public_url":             req.PublicURL,
		"last_modified":          req.LastModified.Format("2006-01-02"),
		"publication_result_ref": req.PublicationResultRef,
	})
	return json.RawMessage(payload), err
}

func sitemapEventType(_ pub.Kind) string {
	return events.TypePublicationSitemappingRequested
}

func newEnvelope(eventType string, payload json.RawMessage, now time.Time) *events.Envelope {
	return &events.Envelope{
		EventID:       uuid.NewString(),
		EventType:     eventType,
		Timestamp:     now,
		SchemaVersion: events.SchemaVersionV1,
		CorrelationID: uuid.NewString(),
		Source:        restSource,
		Payload:       payload,
		Meta:          events.Meta{FirstSeenAt: now},
	}
}

func response(publicationType string, result pub.PublishResult, sitemapResult sitemapping.Result) Response {
	return Response{
		Status:          "completed",
		PublicationType: publicationType,
		PublicationID:   result.PublicationID,
		PublicURL:       result.PublicURL,
		HTMLKey:         result.HTMLKey,
		SitemapIndexKey: sitemapResult.SitemapIndexKey,
		SitemapPageKey:  sitemapResult.SitemapPageKey,
		SitemapResult:   string(sitemapResult.Status),
	}
}

type clientError struct {
	err error
}

func (e clientError) Error() string {
	return e.err.Error()
}

func (e clientError) Unwrap() error {
	return e.err
}

func IsClientError(err error) bool {
	var target clientError
	return errors.As(err, &target)
}

func NewClientError(message string) error {
	return clientError{err: errors.New(message)}
}
