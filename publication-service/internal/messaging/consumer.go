package messaging

import (
	"context"
	"fmt"
	"log/slog"
	"math"
	"math/rand"
	"time"

	"publication-service/internal/events"
	"publication-service/internal/observability"
	pub "publication-service/internal/publish"
)

// EnvelopeNormalizer turns an envelope into a domain view for this consumer's pipeline.
type EnvelopeNormalizer interface {
	// Normalize returns a minimal ClaimInfo (used to claim the DB row),
	// a handler closure that performs the domain work, and a completion-event
	// payload builder for the outbox.
	Normalize(env *events.Envelope) (ClaimInfo, HandlerFunc, CompletionBuilder, error)
}

// ClaimInfo is the minimal view the consumer needs to Claim a row.
type ClaimInfo struct {
	EventID       string
	TenantID      string
	CorrelationID string
	Kind          pub.Kind
}

// HandlerFunc performs the domain work (S3 copy, HTML render, upload).
type HandlerFunc func(ctx context.Context) error

// CompletionBuilder returns the completion envelope for the outbox.
type CompletionBuilder func() (eventID string, envelope []byte, err error)

// Validator is the consumer's validation interface.
type Validator interface {
	Validate(env *events.Envelope) error
}

// PublishRepo is the consumer's view of the publish_request table.
type PublishRepo interface {
	Claim(ctx context.Context, req pub.ClaimRequest) (pub.ClaimResult, error)
	MarkCompleted(ctx context.Context, eventID string, now time.Time) error
	MarkRetry(ctx context.Context, eventID, msg, hash string, nextAt time.Time) error
	MarkDead(ctx context.Context, eventID, msg string, class pub.Class) error
}

// OutboxInserter inserts an outbound row.
type OutboxInserter interface {
	Insert(ctx context.Context, row OutboxRow) error
}

// ConsumerConfig groups stream and timing configuration.
type ConsumerConfig struct {
	Stream                string
	CompletedStream       string
	CompletedEventType    string   // e.g. events.TypePublicationPublishCompleted
	Kind                  pub.Kind // used when claiming rows + tagging outbox
	Group                 string
	Consumer              string
	ReadTimeout           time.Duration
	HandlerTimeout        time.Duration
	ErrorBackoffMin       time.Duration
	ErrorBackoffMax       time.Duration
	MaxRetries            int
	PoisonRepeatThreshold int
}

// Consumer wires a Broker to validation, normalization, the repo, and the outbox.
type Consumer struct {
	cfg        ConsumerConfig
	broker     Broker
	repo       PublishRepo
	outbox     OutboxInserter
	normalizer EnvelopeNormalizer
	validator  Validator
	logger     *slog.Logger
	metrics    *observability.EventMetrics
}

// NewConsumer constructs a Consumer.
func NewConsumer(cfg ConsumerConfig, broker Broker, repo PublishRepo, outbox OutboxInserter, normalizer EnvelopeNormalizer, validator Validator) *Consumer {
	return &Consumer{cfg: cfg, broker: broker, repo: repo, outbox: outbox, normalizer: normalizer, validator: validator, logger: slog.Default()}
}

// WithLogger overrides the logger.
func (c *Consumer) WithLogger(l *slog.Logger) *Consumer { c.logger = l; return c }

// WithMetrics attaches event metrics to the consumer.
func (c *Consumer) WithMetrics(m *observability.EventMetrics) *Consumer { c.metrics = m; return c }

// Run loops Step until ctx is done.
func (c *Consumer) Run(ctx context.Context) error {
	errorBackoff := c.cfg.errorBackoffMin()
	for {
		if err := c.broker.EnsureGroup(ctx, c.cfg.Stream, c.cfg.Group); err != nil {
			if ctx.Err() != nil {
				return ctx.Err()
			}
			c.logger.Error("consumer ensure group failed", slog.Any("err", fmt.Errorf("consumer.Run: ensure group: %w", err)))
			if !sleepContext(ctx, errorBackoff) {
				return ctx.Err()
			}
			errorBackoff = nextErrorBackoff(errorBackoff, c.cfg.errorBackoffMax())
			continue
		}
		break
	}
	errorBackoff = c.cfg.errorBackoffMin()
	for {
		if err := c.Step(ctx); err != nil {
			if ctx.Err() != nil {
				return ctx.Err()
			}
			c.logger.Error("consumer step failed", slog.Any("err", err))
			if !sleepContext(ctx, errorBackoff) {
				return ctx.Err()
			}
			errorBackoff = nextErrorBackoff(errorBackoff, c.cfg.errorBackoffMax())
			continue
		}
		errorBackoff = c.cfg.errorBackoffMin()
		if ctx.Err() != nil {
			return ctx.Err()
		}
	}
}

// Step processes at most one message.
func (c *Consumer) Step(ctx context.Context) error {
	msg, err := c.broker.Read(ctx, c.cfg.Stream, c.cfg.Group, c.cfg.Consumer, c.cfg.ReadTimeout)
	if err != nil {
		return err
	}
	if msg == nil {
		return nil
	}

	env, err := events.UnmarshalEnvelope(msg.Payload)
	if err != nil {
		c.logger.Warn("envelope parse failed", slog.String("redis_id", msg.ID), slog.Any("err", err))
		return c.broker.Ack(ctx, c.cfg.Stream, c.cfg.Group, msg.ID)
	}

	log := c.logger.With(
		slog.String("event_id", env.EventID),
		slog.String("event_type", env.EventType),
		slog.String("correlation_id", env.CorrelationID),
	)

	if err := c.validator.Validate(env); err != nil {
		log.Warn("envelope validation failed", slog.Any("err", err))
		_ = c.repo.MarkDead(ctx, env.EventID, err.Error(), pub.ClassPermanent)
		if c.metrics != nil {
			c.metrics.RecordProcessed(ctx, env.EventType, "dead")
			c.metrics.RecordDeadLetter(ctx, env.EventType, "permanent")
		}
		return c.broker.Ack(ctx, c.cfg.Stream, c.cfg.Group, msg.ID)
	}

	info, handlerFn, completionFn, err := c.normalizer.Normalize(env)
	if err != nil {
		log.Warn("normalize failed", slog.Any("err", err))
		_ = c.repo.MarkDead(ctx, env.EventID, err.Error(), pub.ClassPermanent)
		if c.metrics != nil {
			c.metrics.RecordProcessed(ctx, env.EventType, "dead")
			c.metrics.RecordDeadLetter(ctx, env.EventType, "permanent")
		}
		return c.broker.Ack(ctx, c.cfg.Stream, c.cfg.Group, msg.ID)
	}

	if c.metrics != nil {
		c.metrics.RecordReceived(ctx, env.EventType, info.TenantID)
	}

	now := time.Now().UTC()
	claim, err := c.repo.Claim(ctx, pub.ClaimRequest{
		EventID:       info.EventID,
		EventType:     env.EventType,
		TenantID:      info.TenantID,
		CorrelationID: info.CorrelationID,
		SchemaVersion: env.SchemaVersion,
		Payload:       env.Payload,
		Now:           now,
		Kind:          info.Kind,
	})
	if pub.IsDuplicate(err) {
		log.Warn("duplicate (tenant_id, correlation_id) — skipping")
		return c.broker.Ack(ctx, c.cfg.Stream, c.cfg.Group, msg.ID)
	}
	if err != nil {
		return fmt.Errorf("consumer claim: %w", err)
	}
	if !claim.Won {
		log.Info("already claimed by another worker — skipping")
		return c.broker.Ack(ctx, c.cfg.Stream, c.cfg.Group, msg.ID)
	}

	// Ack now: retry clock lives in Postgres from here on.
	if err := c.broker.Ack(ctx, c.cfg.Stream, c.cfg.Group, msg.ID); err != nil {
		log.Error("ack failed", slog.Any("err", err))
	}

	hctx, cancel := context.WithTimeout(ctx, c.cfg.HandlerTimeout)
	defer cancel()
	herr := handlerFn(hctx)
	if herr == nil {
		if err := c.repo.MarkCompleted(ctx, env.EventID, time.Now().UTC()); err != nil {
			return fmt.Errorf("consumer mark completed: %w", err)
		}
		if c.metrics != nil {
			c.metrics.RecordProcessed(ctx, env.EventType, "completed")
		}
		completionEventID, completionBytes, err := completionFn()
		if err != nil {
			return fmt.Errorf("consumer build completed envelope: %w", err)
		}
		return c.outbox.Insert(ctx, OutboxRow{
			EventID:   completionEventID,
			EventType: c.cfg.CompletedEventType,
			TenantID:  info.TenantID,
			Envelope:  completionBytes,
			Kind:      info.Kind,
		})
	}

	cl := pub.Classify(herr)
	if cl.Class == pub.ClassPermanent {
		log.Warn("permanent error → dead", slog.String("err", cl.Message))
		if c.metrics != nil {
			c.metrics.RecordProcessed(ctx, env.EventType, "dead")
			c.metrics.RecordDeadLetter(ctx, env.EventType, "permanent")
		}
		return c.repo.MarkDead(ctx, env.EventID, cl.Message, pub.ClassPermanent)
	}
	hash := pub.ErrorHash(cl.Class, cl.Message)
	next := time.Now().UTC().Add(backoff(0))
	log.Warn("transient error → retry",
		slog.String("err", cl.Message),
		slog.String("error_hash", hash),
		slog.Time("next_retry_at", next))
	if c.metrics != nil {
		c.metrics.RecordProcessed(ctx, env.EventType, "retry")
	}
	return c.repo.MarkRetry(ctx, env.EventID, cl.Message, hash, next)
}

// backoff returns the wait duration for retry attempt n (0-indexed).
func backoff(n int) time.Duration {
	base := time.Second * time.Duration(math.Pow(5, float64(n)))
	if base > 10*time.Minute {
		base = 10 * time.Minute
	}
	jitter := 1 + (rand.Float64()*0.4 - 0.2)
	return time.Duration(float64(base) * jitter)
}

func (cfg ConsumerConfig) errorBackoffMin() time.Duration {
	if cfg.ErrorBackoffMin > 0 {
		return cfg.ErrorBackoffMin
	}
	return time.Second
}

func (cfg ConsumerConfig) errorBackoffMax() time.Duration {
	if cfg.ErrorBackoffMax > 0 {
		return cfg.ErrorBackoffMax
	}
	return 30 * time.Second
}

func nextErrorBackoff(current, max time.Duration) time.Duration {
	if current <= 0 {
		current = time.Second
	}
	next := current * 2
	if next > max {
		return max
	}
	return next
}

func sleepContext(ctx context.Context, d time.Duration) bool {
	t := time.NewTimer(d)
	defer t.Stop()
	select {
	case <-ctx.Done():
		return false
	case <-t.C:
		return true
	}
}
