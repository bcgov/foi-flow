package messaging

import (
	"context"
	"log/slog"
	"time"
)

// OutboxStore is the publisher's view of the outbox table.
type OutboxStore interface {
	ClaimBatch(ctx context.Context, limit int) ([]OutboxRow, error)
	MarkPublished(ctx context.Context, id int64, now time.Time) error
	BumpAttempts(ctx context.Context, id int64) error
}

// OutboxPublisher drains unpublished outbox rows to a Broker.
type OutboxPublisher struct {
	store    OutboxStore
	broker   Broker
	maxLen   int64
	batch    int
	logger   *slog.Logger
	interval time.Duration
}

// NewOutboxPublisher constructs a publisher with default batch=100.
func NewOutboxPublisher(store OutboxStore, broker Broker, maxLen int64) *OutboxPublisher {
	return &OutboxPublisher{
		store:    store,
		broker:   broker,
		maxLen:   maxLen,
		batch:    100,
		logger:   slog.Default(),
		interval: time.Second,
	}
}

// WithInterval overrides the tick interval.
func (p *OutboxPublisher) WithInterval(d time.Duration) *OutboxPublisher {
	p.interval = d
	return p
}

// WithLogger overrides the logger.
func (p *OutboxPublisher) WithLogger(l *slog.Logger) *OutboxPublisher {
	p.logger = l
	return p
}

// Drain publishes one batch and returns.
func (p *OutboxPublisher) Drain(ctx context.Context) error {
	rows, err := p.store.ClaimBatch(ctx, p.batch)
	if err != nil {
		return err
	}
	for _, r := range rows {
		if _, err := p.broker.Publish(ctx, r.EventType, r.Envelope, p.maxLen); err != nil {
			p.logger.Error("outbox publish failed",
				slog.String("event_id", r.EventID),
				slog.String("event_type", r.EventType),
				slog.String("kind", string(r.Kind)),
				slog.Int64("outbox_id", r.ID),
				slog.Any("err", err))
			if bumpErr := p.store.BumpAttempts(ctx, r.ID); bumpErr != nil {
				p.logger.Error("outbox bump attempts failed",
					slog.Int64("outbox_id", r.ID), slog.Any("err", bumpErr))
			}
			continue
		}
		if err := p.store.MarkPublished(ctx, r.ID, time.Now().UTC()); err != nil {
			p.logger.Error("outbox mark published failed",
				slog.Int64("outbox_id", r.ID), slog.Any("err", err))
		}
	}
	return nil
}

// Run ticks Drain on the configured interval until ctx is done.
func (p *OutboxPublisher) Run(ctx context.Context) error {
	t := time.NewTicker(p.interval)
	defer t.Stop()
	for {
		if err := p.Drain(ctx); err != nil {
			p.logger.Error("outbox drain failed", slog.Any("err", err))
		}
		select {
		case <-ctx.Done():
			return ctx.Err()
		case <-t.C:
		}
	}
}
