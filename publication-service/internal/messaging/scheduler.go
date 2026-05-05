package messaging

import (
	"context"
	"encoding/json"
	"fmt"
	"log/slog"
	"time"

	"publication-service/internal/events"
	pub "publication-service/internal/publish"
)

// SchedulerRepo is the scheduler's view of workflow_request.
type SchedulerRepo interface {
	ClaimDue(ctx context.Context, limit int, now time.Time) ([]pub.DueRow, error)
	ResetStuck(ctx context.Context, threshold time.Time) (int64, error)
}

// SchedulerConfig groups inputs.
type SchedulerConfig struct {
	PublishStream   string
	PublishSource   string
	SitemapStream   string
	SitemapSource   string
	UnpublishStream string
	UnpublishSource string
	BatchSize       int
	StreamMaxLen    int64
	Interval        time.Duration
	StuckTimeout    time.Duration
}

// Scheduler ticks: claim due rows, re-XADD, and reset stuck rows.
type Scheduler struct {
	cfg    SchedulerConfig
	repo   SchedulerRepo
	broker Broker
	logger *slog.Logger
}

// NewScheduler constructs a Scheduler.
func NewScheduler(cfg SchedulerConfig, repo SchedulerRepo, broker Broker) *Scheduler {
	return &Scheduler{cfg: cfg, repo: repo, broker: broker, logger: slog.Default()}
}

// WithLogger overrides the logger.
func (s *Scheduler) WithLogger(l *slog.Logger) *Scheduler { s.logger = l; return s }

// Tick performs one cycle of due-row re-enqueue + stuck-row recovery.
func (s *Scheduler) Tick(ctx context.Context) error {
	now := time.Now().UTC()

	due, err := s.repo.ClaimDue(ctx, s.cfg.BatchSize, now)
	if err != nil {
		return fmt.Errorf("scheduler ClaimDue: %w", err)
	}
	for _, d := range due {
		var stream, source string
		switch d.Kind {
		case pub.KindOpenInfo, pub.KindProactiveDisclosure:
			stream = s.cfg.PublishStream
			source = s.cfg.PublishSource
		case pub.KindOpenInfoSitemap, pub.KindProactiveDisclosureSitemap:
			stream = s.cfg.SitemapStream
			source = s.cfg.SitemapSource
		case pub.KindOpenInfoUnpublish, pub.KindProactiveDisclosureUnpublish:
			stream = s.cfg.UnpublishStream
			source = s.cfg.UnpublishSource
		default:
			stream = s.cfg.PublishStream
			source = s.cfg.PublishSource
		}

		env := events.Envelope{
			EventID:       d.EventID,
			EventType:     d.EventType,
			Timestamp:     now,
			SchemaVersion: d.SchemaVersion,
			CorrelationID: d.CorrelationID,
			Source:        source,
			Payload:       d.Payload,
			Meta: events.Meta{
				RetryCount:  d.RetryCount,
				FirstSeenAt: now,
			},
		}
		b, err := json.Marshal(env)
		if err != nil {
			s.logger.Error("scheduler marshal failed",
				slog.String("event_id", d.EventID), slog.Any("err", err))
			continue
		}
		if _, err := s.broker.Publish(ctx, stream, b, s.cfg.StreamMaxLen); err != nil {
			s.logger.Error("scheduler publish failed",
				slog.String("event_id", d.EventID), slog.Any("err", err))
		}
	}

	if s.cfg.StuckTimeout > 0 {
		threshold := now.Add(-s.cfg.StuckTimeout)
		n, err := s.repo.ResetStuck(ctx, threshold)
		if err != nil {
			s.logger.Error("scheduler ResetStuck failed", slog.Any("err", err))
		} else if n > 0 {
			s.logger.Warn("scheduler reset stuck rows", slog.Int64("count", n))
		}
	}
	return nil
}

// Run loops Tick on the configured interval until ctx is done.
func (s *Scheduler) Run(ctx context.Context) error {
	t := time.NewTicker(s.cfg.Interval)
	defer t.Stop()
	for {
		if err := s.Tick(ctx); err != nil {
			s.logger.Error("scheduler tick failed", slog.Any("err", err))
		}
		select {
		case <-ctx.Done():
			return ctx.Err()
		case <-t.C:
		}
	}
}
