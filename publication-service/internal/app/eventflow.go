package app

import (
	"context"
	"fmt"
	"log/slog"
	"sync"
	"time"

	"go.opentelemetry.io/otel"

	"publication-service/internal/config"
	"publication-service/internal/events"
	"publication-service/internal/messaging"
	"publication-service/internal/messaging/redisstream"
	"publication-service/internal/observability"
	pubpub "publication-service/internal/publication/publish"
	pubsm "publication-service/internal/publication/sitemapping"
	pubunpub "publication-service/internal/publication/unpublish"
	pub "publication-service/internal/publish"
	sitemapping "publication-service/internal/sitemapping"
	pg "publication-service/internal/storage/postgres"
	pubs3 "publication-service/internal/storage/s3"
	"publication-service/internal/unpublish"
)

const eventFlowWorkerCount = 5

// RunEventFlow wires and runs the consumer, scheduler, and outbox publisher.
// It blocks until ctx is cancelled, then waits for goroutines to stop.
func RunEventFlow(ctx context.Context, cfg *config.Config, logger *slog.Logger) error {
	if err := pg.Migrate(ctx, cfg.PostgresURL); err != nil {
		return fmt.Errorf("migrate: %w", err)
	}

	pool, err := pg.NewPool(ctx, cfg.PostgresURL)
	if err != nil {
		return fmt.Errorf("postgres pool: %w", err)
	}
	defer pool.Close()

	broker, err := redisstream.New(redisstream.Options{
		Addr:     cfg.RedisAddr,
		Password: cfg.RedisPassword,
		UseTLS:   cfg.RedisTLS,
	})
	if err != nil {
		return fmt.Errorf("redis: %w", err)
	}
	defer func() { _ = broker.Close() }()

	sharedRepo := pub.NewRepo(pool)
	outboxRepo := messaging.NewOutboxRepo(pool)

	s3Client, err := pubs3.NewClient(cfg.S3)
	if err != nil {
		return fmt.Errorf("s3 client: %w", err)
	}
	sitemapResultRepo := sitemapping.NewRequestRepo(pool)
	sitemapWriter := sitemapping.NewWriter(s3Client, sitemapResultRepo, SitemapTargets(cfg))
	unpublishResultRepo := unpublish.NewRequestRepo(pool)
	unpublishService := unpublish.NewService(s3Client, sitemapWriter, unpublishResultRepo)

	meter := otel.GetMeterProvider().Meter("publication-service/events")
	metrics, err := observability.NewEventMetrics(meter)
	if err != nil {
		return fmt.Errorf("metrics: %w", err)
	}

	// Unified publish consumer
	pubService := pubpub.NewService(s3Client, s3Client, cfg.S3.PublicURL, logger, pubpub.WithFileCopier(s3Client), pubpub.WithDeleter(s3Client))
	pubNormalizer := pubpub.NewCompletionAdapter(pubService, sitemapWriter)
	pubValidator, err := pubpub.NewValidator(events.TypePublicationPublishRequested, cfg.SourceAllowlist)
	if err != nil {
		return fmt.Errorf("publish validator: %w", err)
	}
	pubConsumer := messaging.NewConsumer(messaging.ConsumerConfig{
		Stream:                cfg.RedisStreamPublishRequested,
		CompletedStream:       cfg.RedisStreamPublishCompleted,
		CompletedEventType:    events.TypePublicationPublishCompleted,
		Kind:                  pub.KindOpenInfo,
		Group:                 cfg.RedisPublishConsumerGroup,
		Consumer:              cfg.RedisPublishConsumerName,
		ReadTimeout:           5 * time.Second,
		HandlerTimeout:        cfg.HandlerTimeout,
		MaxRetries:            cfg.RetryMaxAttempts,
		PoisonRepeatThreshold: cfg.PoisonRepeatThreshold,
	}, broker, sharedRepo, outboxRepo, pubNormalizer, pubValidator).WithMetrics(metrics).WithLogger(logger)

	// Unified unpublish consumer
	unpubNormalizer := pubunpub.NewNormalizerAdapter(unpublishService)
	unpubValidator, err := pubunpub.NewValidator(cfg.UnpublishSourceAllowlist)
	if err != nil {
		return fmt.Errorf("unpublish validator: %w", err)
	}
	unpubConsumer := messaging.NewConsumer(messaging.ConsumerConfig{
		Stream:                cfg.RedisStreamUnpublishRequested,
		CompletedStream:       cfg.RedisStreamUnpublishCompleted,
		CompletedEventType:    events.TypePublicationUnpublishCompleted,
		Kind:                  pub.KindOpenInfoUnpublish,
		Group:                 cfg.RedisUnpublishConsumerGroup,
		Consumer:              cfg.RedisUnpublishConsumerName,
		ReadTimeout:           5 * time.Second,
		HandlerTimeout:        cfg.HandlerTimeout,
		MaxRetries:            cfg.RetryMaxAttempts,
		PoisonRepeatThreshold: cfg.PoisonRepeatThreshold,
	}, broker, sharedRepo, outboxRepo, unpubNormalizer, unpubValidator).WithMetrics(metrics).WithLogger(logger)

	// Unified sitemapping consumer
	smNormalizer := pubsm.NewNormalizerAdapter(sitemapWriter)
	smValidator, err := pubsm.NewValidator(cfg.Sitemap.SourceAllowlist)
	if err != nil {
		return fmt.Errorf("sitemapping validator: %w", err)
	}
	smConsumer := messaging.NewConsumer(messaging.ConsumerConfig{
		Stream:                cfg.Sitemap.RequestedStream,
		CompletedStream:       cfg.Sitemap.CompletedStream,
		CompletedEventType:    events.TypePublicationSitemappingCompleted,
		Kind:                  pub.KindOpenInfoSitemap,
		Group:                 cfg.Sitemap.ConsumerGroup,
		Consumer:              cfg.Sitemap.ConsumerName,
		ReadTimeout:           5 * time.Second,
		HandlerTimeout:        cfg.HandlerTimeout,
		MaxRetries:            cfg.RetryMaxAttempts,
		PoisonRepeatThreshold: cfg.PoisonRepeatThreshold,
	}, broker, sharedRepo, outboxRepo, smNormalizer, smValidator).WithMetrics(metrics).WithLogger(logger)

	scheduler := messaging.NewScheduler(messaging.SchedulerConfig{
		PublishStream:   cfg.RedisStreamPublishRequested,
		PublishSource:   "publication.publish.service",
		SitemapStream:   cfg.Sitemap.RequestedStream,
		SitemapSource:   "publication.sitemapping.service",
		UnpublishStream: cfg.RedisStreamUnpublishRequested,
		UnpublishSource: "publication.unpublish.service",
		BatchSize:       100,
		StreamMaxLen:    cfg.StreamMaxLen,
		Interval:        cfg.SchedulerInterval,
		StuckTimeout:    cfg.StuckTimeout,
	}, sharedRepo, broker).WithLogger(logger)

	publisher := messaging.NewOutboxPublisher(outboxRepo, broker, cfg.StreamMaxLen).
		WithInterval(cfg.OutboxInterval).WithLogger(logger)

	bgCtx, cancelBg := context.WithCancel(ctx)
	defer cancelBg()

	var wg sync.WaitGroup
	wg.Add(eventFlowWorkerCount)
	go func() { defer wg.Done(); _ = pubConsumer.Run(bgCtx) }()
	go func() { defer wg.Done(); _ = unpubConsumer.Run(bgCtx) }()
	go func() { defer wg.Done(); _ = smConsumer.Run(bgCtx) }()
	go func() { defer wg.Done(); _ = scheduler.Run(bgCtx) }()
	go func() { defer wg.Done(); _ = publisher.Run(bgCtx) }()

	<-ctx.Done()
	cancelBg()

	shutdownDeadline := cfg.HandlerTimeout + 5*time.Second
	done := make(chan struct{})
	go func() { wg.Wait(); close(done) }()
	select {
	case <-done:
	case <-time.After(shutdownDeadline):
		logger.Warn("event-flow goroutines did not stop within deadline",
			slog.Duration("deadline", shutdownDeadline))
	}
	return nil
}

func SitemapTargets(cfg *config.Config) map[pub.Kind]sitemapping.Target {
	t := sitemapping.Target{
		Bucket:          cfg.Sitemap.Target.Bucket,
		Prefix:          cfg.Sitemap.Target.Prefix,
		PublicBaseURL:   cfg.Sitemap.Target.PublicBaseURL,
		IndexFileName:   cfg.Sitemap.Target.IndexFileName,
		PageFilePattern: cfg.Sitemap.Target.PageFilePattern,
		PageLimit:       cfg.Sitemap.PageLimit,
	}
	return map[pub.Kind]sitemapping.Target{
		pub.KindOpenInfoSitemap:              t,
		pub.KindProactiveDisclosureSitemap:   t,
		pub.KindOpenInfoUnpublish:            t,
		pub.KindProactiveDisclosureUnpublish: t,
	}
}
