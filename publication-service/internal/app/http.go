package app

import (
	"context"
	"fmt"
	"log/slog"

	"publication-service/internal/config"
	"publication-service/internal/http/handlers"
	httpserver "publication-service/internal/http/server"
	pubpub "publication-service/internal/publication/publish"
	pub "publication-service/internal/publish"
	"publication-service/internal/publishnow"
	"publication-service/internal/sitemapping"
	pg "publication-service/internal/storage/postgres"
	pubs3 "publication-service/internal/storage/s3"
	"publication-service/internal/unpublish"
	"publication-service/internal/unpublishnow"
)

// NewHTTPOptions wires request-scoped HTTP dependencies. The REST publication
// path owns a separate Postgres pool from the background event flow so the
// server can expose the route before the event workers finish starting.
func NewHTTPOptions(ctx context.Context, cfg *config.Config, logger *slog.Logger) (httpserver.Options, func(), error) {
	if err := pg.Migrate(ctx, cfg.PostgresURL); err != nil {
		return httpserver.Options{}, nil, fmt.Errorf("migrate: %w", err)
	}

	pool, err := pg.NewPool(ctx, cfg.PostgresURL)
	if err != nil {
		return httpserver.Options{}, nil, fmt.Errorf("postgres pool: %w", err)
	}
	cleanup := func() {
		pool.Close()
	}

	s3Client, err := pubs3.NewClient(cfg.S3)
	if err != nil {
		cleanup()
		return httpserver.Options{}, nil, fmt.Errorf("s3 client: %w", err)
	}

	pubService := pubpub.NewService(s3Client, s3Client, cfg.S3.PublicURL, logger)
	sitemapRepo := sitemapping.NewRequestRepo(pool)
	workflowRepo := pub.NewRepo(pool)
	sitemapWriter := sitemapping.NewWriter(s3Client, sitemapRepo, SitemapTargets(cfg))
	orchestrator := publishnow.New(pubService, sitemapWriter).WithSitemapClaimer(workflowRepo)
	unpublishRepo := unpublish.NewRequestRepo(pool)
	unpublishService := unpublish.NewService(s3Client, sitemapWriter, unpublishRepo)
	unpublishOrchestrator := unpublishnow.New(unpublishService).WithClaimer(workflowRepo)

	return httpserver.Options{
		Publications:          handlers.Publications(orchestrator),
		PublicationsUnpublish: handlers.PublicationsUnpublish(unpublishOrchestrator),
	}, cleanup, nil
}
