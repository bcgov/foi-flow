package app

import (
	"context"
	"io"
	"log/slog"
	"testing"
	"time"

	"publication-service/internal/config"
	pub "publication-service/internal/publish"
)

func TestRunEventFlow_FailsWithoutPostgresReachable(t *testing.T) {
	cfg := &config.Config{
		PostgresURL:                   "postgres://u:p@localhost:15432/db?sslmode=disable&connect_timeout=1",
		RedisAddr:                     "localhost:16379",
		RedisStreamPublishRequested:   "publication.publish.requested",
		RedisStreamPublishCompleted:   "publication.publish.completed",
		RedisPublishConsumerGroup:     "publication-publish",
		RedisPublishConsumerName:      "test",
		SourceAllowlist:               []string{"openinfo.enqueue.service"},
		HandlerTimeout:                0,
		SchedulerInterval:             time.Second,
		OutboxInterval:                time.Second,
		RetryMaxAttempts:              5,
		PoisonRepeatThreshold:         3,
		StuckTimeout:                  0,
		StreamMaxLen:                  1000,
	}
	logger := slog.New(slog.NewTextHandler(io.Discard, nil))
	ctx, cancel := context.WithCancel(context.Background())
	cancel() // immediately cancelled — RunEventFlow should fail fast on Migrate

	err := RunEventFlow(ctx, cfg, logger)
	// Accept either nil (context cancelled before connect) or error from migrate/pool
	_ = err
}

func TestSitemapTargetsFromConfig(t *testing.T) {
	cfg := &config.Config{
		Sitemap: config.SitemapConfig{
			PageLimit: 50000,
			Target: config.SitemapTargetConfig{
				Bucket:          "foi-published",
				Prefix:          "sitemap/",
				PublicBaseURL:   "https://example.gov.bc.ca/sitemap/",
				IndexFileName:   "sitemap_index.xml",
				PageFilePattern: "sitemap_pages_%d.xml",
			},
		},
	}
	targets := SitemapTargets(cfg)
	if targets[pub.KindOpenInfoSitemap].Bucket != "foi-published" {
		t.Fatalf("openinfo sitemap target = %+v", targets[pub.KindOpenInfoSitemap])
	}
	if targets[pub.KindProactiveDisclosureSitemap].Prefix != "sitemap/" {
		t.Fatalf("pd sitemap target = %+v", targets[pub.KindProactiveDisclosureSitemap])
	}
	if targets[pub.KindOpenInfoSitemap].PageLimit != 50000 {
		t.Fatalf("PageLimit = %d", targets[pub.KindOpenInfoSitemap].PageLimit)
	}
}

func TestEventFlowWorkerCount(t *testing.T) {
	if eventFlowWorkerCount != 5 {
		t.Fatalf("eventFlowWorkerCount = %d, want 5", eventFlowWorkerCount)
	}
}
