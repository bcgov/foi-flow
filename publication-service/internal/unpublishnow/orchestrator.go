package unpublishnow

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"time"

	"github.com/google/uuid"

	"publication-service/internal/events"
	pubunpub "publication-service/internal/publication/unpublish"
	pub "publication-service/internal/publish"
	shared "publication-service/internal/unpublish"
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
	Status                 string `json:"status"`
	PublicationType        string `json:"publication_type"`
	PublicationID          string `json:"publication_id"`
	PublicURL              string `json:"public_url"`
	PublicRepositoryBucket string `json:"public_repository_bucket"`
	PublicRepositoryPrefix string `json:"public_repository_prefix"`
	ObjectsDeleted         int    `json:"objects_deleted"`
	SitemapIndexKey        string `json:"sitemap_index_key"`
	SitemapPageKey         string `json:"sitemap_page_key,omitempty"`
	SitemapResult          string `json:"sitemap_result"`
}

type Service interface {
	Handle(context.Context, shared.Request) (shared.Result, error)
}

type claimer interface {
	Claim(context.Context, pub.ClaimRequest) (pub.ClaimResult, error)
}

type Orchestrator struct {
	service Service
	claimer claimer
	now     func() time.Time
}

func New(service Service) *Orchestrator {
	return &Orchestrator{service: service, now: func() time.Time { return time.Now().UTC() }}
}

func (o *Orchestrator) WithClaimer(claimer claimer) *Orchestrator {
	o.claimer = claimer
	return o
}

func (o *Orchestrator) Unpublish(ctx context.Context, body []byte) (Response, error) {
	var req Request
	if err := json.Unmarshal(body, &req); err != nil {
		return Response{}, clientError{err: fmt.Errorf("malformed JSON: %w", err)}
	}
	if len(req.Payload) == 0 || string(req.Payload) == "null" {
		return Response{}, clientError{err: errors.New("payload is required")}
	}

	switch req.PublicationType {
	case PublicationTypeOpenInfo, PublicationTypeProactiveDisclosure:
		return o.unpublish(ctx, string(req.PublicationType), req.Payload)
	default:
		return Response{}, clientError{err: fmt.Errorf("unsupported publication_type %q", req.PublicationType)}
	}
}

func (o *Orchestrator) unpublish(ctx context.Context, pubType string, payload json.RawMessage) (Response, error) {
	env := newEnvelope(events.TypePublicationUnpublishRequested, payload, o.now())
	validator, err := pubunpub.NewValidator([]string{restSource})
	if err != nil {
		return Response{}, err
	}
	if err := validator.Validate(env); err != nil {
		return Response{}, clientError{err: err}
	}
	req, err := pubunpub.Normalize(env)
	if err != nil {
		return Response{}, clientError{err: err}
	}
	if err := o.claim(ctx, env, req); err != nil {
		return Response{}, err
	}
	result, err := o.service.Handle(ctx, req)
	if err != nil {
		return Response{}, err
	}
	return response(pubType, result), nil
}

func (o *Orchestrator) claim(ctx context.Context, env *events.Envelope, req shared.Request) error {
	if o.claimer == nil {
		return nil
	}
	claim, err := o.claimer.Claim(ctx, pub.ClaimRequest{
		EventID:       req.SourceEventID,
		EventType:     env.EventType,
		TenantID:      req.TenantID,
		CorrelationID: req.CorrelationID,
		SchemaVersion: env.SchemaVersion,
		Payload:       env.Payload,
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
		return fmt.Errorf("unpublish request %s was already claimed", req.SourceEventID)
	}
	return nil
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

func response(publicationType string, result shared.Result) Response {
	return Response{
		Status:                 "completed",
		PublicationType:        publicationType,
		PublicationID:          result.PublicationID,
		PublicURL:              result.PublicURL,
		PublicRepositoryBucket: result.PublicRepositoryBucket,
		PublicRepositoryPrefix: result.PublicRepositoryPrefix,
		ObjectsDeleted:         result.ObjectsDeleted,
		SitemapIndexKey:        result.SitemapIndexKey,
		SitemapPageKey:         result.SitemapPageKey,
		SitemapResult:          result.SitemapResult,
	}
}

type clientError struct {
	err error
}

func (e clientError) Error() string {
	return e.err.Error()
}

func IsClientError(err error) bool {
	var target clientError
	return errors.As(err, &target)
}
