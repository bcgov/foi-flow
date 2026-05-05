package config

import (
	"log/slog"
	"testing"
)

func TestLoad(t *testing.T) {
	tests := []struct {
		name   string
		value  string
		setEnv bool
		want   string
	}{
		{
			name:   "uses configured port",
			value:  "9090",
			setEnv: true,
			want:   "9090",
		},
		{
			name:   "falls back to default port",
			value:  "",
			setEnv: true,
			want:   "9085",
		},
		{
			name:   "uses default when port is absent",
			setEnv: false,
			want:   "9085",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			setBaseEnv(t)

			if tt.setEnv {
				t.Setenv("PORT", tt.value)
			}

			if !tt.setEnv {
				t.Setenv("PORT", "")
			}

			cfg, err := Load()
			if err != nil {
				t.Fatalf("Load: %v", err)
			}
			if cfg.Port != tt.want {
				t.Fatalf("config port = %q, want %q", cfg.Port, tt.want)
			}
		})
	}
}

func TestLoad_EventFlowDefaults(t *testing.T) {
	for _, k := range eventFlowEnvKeys() {
		t.Setenv(k, "")
	}
	setBaseEnv(t)
	cfg, err := Load()
	if err != nil {
		t.Fatalf("Load: %v", err)
	}
	if cfg.RedisAddr != "localhost:6379" {
		t.Errorf("RedisAddr = %q", cfg.RedisAddr)
	}
	if cfg.LogLevel != 0 {
		t.Errorf("LogLevel = %s, want INFO", cfg.LogLevel)
	}
	if cfg.RedisStreamPublishRequested != "publication.publish.requested" {
		t.Errorf("RedisStreamPublishRequested = %q", cfg.RedisStreamPublishRequested)
	}
	if cfg.RedisStreamPublishCompleted != "publication.publish.completed" {
		t.Errorf("RedisStreamPublishCompleted = %q", cfg.RedisStreamPublishCompleted)
	}
	if cfg.RedisPublishConsumerGroup != "publication-publish" {
		t.Errorf("RedisPublishConsumerGroup = %q", cfg.RedisPublishConsumerGroup)
	}
	if cfg.ConsumerWorkers != 1 {
		t.Errorf("ConsumerWorkers = %d", cfg.ConsumerWorkers)
	}
	if cfg.SchedulerInterval.String() != "5s" {
		t.Errorf("SchedulerInterval = %s", cfg.SchedulerInterval)
	}
	if cfg.OutboxInterval.String() != "1s" {
		t.Errorf("OutboxInterval = %s", cfg.OutboxInterval)
	}
	if cfg.RetryMaxAttempts != 5 {
		t.Errorf("RetryMaxAttempts = %d", cfg.RetryMaxAttempts)
	}
	if cfg.StuckTimeout.String() != "2m0s" {
		t.Errorf("StuckTimeout = %s", cfg.StuckTimeout)
	}
	if cfg.HandlerTimeout.String() != "30s" {
		t.Errorf("HandlerTimeout = %s", cfg.HandlerTimeout)
	}
	if cfg.MaxInFlightEvents != 64 {
		t.Errorf("MaxInFlightEvents = %d", cfg.MaxInFlightEvents)
	}
	if cfg.PoisonRepeatThreshold != 3 {
		t.Errorf("PoisonRepeatThreshold = %d", cfg.PoisonRepeatThreshold)
	}
	if cfg.StreamMaxLen != 100000 {
		t.Errorf("StreamMaxLen = %d", cfg.StreamMaxLen)
	}
	if cfg.StreamTrimInterval.String() != "1h0m0s" {
		t.Errorf("StreamTrimInterval = %s", cfg.StreamTrimInterval)
	}
	if cfg.RedisTLS {
		t.Errorf("RedisTLS = true, want false")
	}
	if got := cfg.SourceAllowlist; len(got) != 1 || got[0] != "openinfo.enqueue.service" {
		t.Errorf("SourceAllowlist = %v", got)
	}
}

func TestLoad_PostgresURLRequired(t *testing.T) {
	t.Setenv("POSTGRES_URL", "")
	if _, err := Load(); err == nil {
		t.Fatal("expected error when POSTGRES_URL is unset")
	}
}

func TestLoad_PostgresURLProvided(t *testing.T) {
	setBaseEnv(t)
	cfg, err := Load()
	if err != nil {
		t.Fatalf("Load: %v", err)
	}
	if cfg.PostgresURL != "postgres://u:p@localhost:5432/db" {
		t.Errorf("PostgresURL = %q", cfg.PostgresURL)
	}
}

func eventFlowEnvKeys() []string {
	return []string{
		"REDIS_ADDR", "REDIS_STREAM_PUBLISH_REQUESTED", "REDIS_STREAM_PUBLISH_COMPLETED",
		"REDIS_PUBLISH_CONSUMER_GROUP", "REDIS_PUBLISH_CONSUMER_NAME", "POSTGRES_URL",
		"CONSUMER_WORKERS", "SCHEDULER_INTERVAL", "OUTBOX_INTERVAL",
		"RETRY_MAX_ATTEMPTS", "STUCK_TIMEOUT", "HANDLER_TIMEOUT",
		"MAX_IN_FLIGHT_EVENTS", "POISON_REPEAT_THRESHOLD",
		"STREAM_MAXLEN", "STREAM_TRIM_INTERVAL",
		"REDIS_PASSWORD", "REDIS_TLS", "SOURCE_ALLOWLIST",
		"S3_ENDPOINT", "S3_REGION", "S3_ACCESS_KEY_ID",
		"S3_SECRET_ACCESS_KEY", "S3_USE_PATH_STYLE", "S3_REQUEST_TIMEOUT",
		"SITEMAP_BUCKET", "SITEMAP_PREFIX",
		"SITEMAP_PUBLIC_BASE_URL",
		"SITEMAP_PAGE_LIMIT", "REDIS_STREAM_SITEMAP_REQUESTED",
		"REDIS_STREAM_SITEMAP_COMPLETED", "REDIS_SITEMAP_CONSUMER_GROUP",
		"REDIS_SITEMAP_CONSUMER_NAME", "SITEMAP_SOURCE_ALLOWLIST",
		"REDIS_STREAM_UNPUBLISH_REQUESTED", "REDIS_STREAM_UNPUBLISH_COMPLETED",
		"REDIS_UNPUBLISH_CONSUMER_GROUP", "REDIS_UNPUBLISH_CONSUMER_NAME",
		"UNPUBLISH_SOURCE_ALLOWLIST",
	}
}

func TestLoad_S3Defaults(t *testing.T) {
	setBaseEnv(t)
	t.Setenv("S3_ENDPOINT", "http://localhost:8333")
	t.Setenv("S3_ACCESS_KEY_ID", "devkey")
	t.Setenv("S3_SECRET_ACCESS_KEY", "devsecret")
	// Leave optional vars unset.
	t.Setenv("S3_REGION", "")
	t.Setenv("S3_USE_PATH_STYLE", "")
	t.Setenv("S3_REQUEST_TIMEOUT", "")

	cfg, err := Load()
	if err != nil {
		t.Fatalf("Load: %v", err)
	}
	if cfg.S3.Endpoint != "http://localhost:8333" {
		t.Errorf("S3.Endpoint = %q", cfg.S3.Endpoint)
	}
	if cfg.S3.Region != "us-east-1" {
		t.Errorf("S3.Region = %q, want us-east-1", cfg.S3.Region)
	}
	if cfg.S3.AccessKeyID != "devkey" {
		t.Errorf("S3.AccessKeyID = %q", cfg.S3.AccessKeyID)
	}
	if cfg.S3.SecretAccessKey != "devsecret" {
		t.Errorf("S3.SecretAccessKey = %q", cfg.S3.SecretAccessKey)
	}
	if !cfg.S3.UsePathStyle {
		t.Errorf("S3.UsePathStyle = false, want true (default)")
	}
	if cfg.S3.RequestTimeout.String() != "30s" {
		t.Errorf("S3.RequestTimeout = %s, want 30s", cfg.S3.RequestTimeout)
	}
}

func TestLoad_S3MissingEndpoint(t *testing.T) {
	t.Setenv("POSTGRES_URL", "postgres://u:p@localhost:5432/db")
	t.Setenv("S3_ENDPOINT", "")
	t.Setenv("S3_ACCESS_KEY_ID", "devkey")
	t.Setenv("S3_SECRET_ACCESS_KEY", "devsecret")
	if _, err := Load(); err == nil {
		t.Fatal("expected error when S3_ENDPOINT is empty")
	}
}

func TestLoad_S3MissingAccessKey(t *testing.T) {
	t.Setenv("POSTGRES_URL", "postgres://u:p@localhost:5432/db")
	t.Setenv("S3_ENDPOINT", "http://localhost:8333")
	t.Setenv("S3_ACCESS_KEY_ID", "")
	t.Setenv("S3_SECRET_ACCESS_KEY", "devsecret")
	if _, err := Load(); err == nil {
		t.Fatal("expected error when S3_ACCESS_KEY_ID is empty")
	}
}

func TestLoad_S3MissingSecretKey(t *testing.T) {
	t.Setenv("POSTGRES_URL", "postgres://u:p@localhost:5432/db")
	t.Setenv("S3_ENDPOINT", "http://localhost:8333")
	t.Setenv("S3_ACCESS_KEY_ID", "devkey")
	t.Setenv("S3_SECRET_ACCESS_KEY", "")
	if _, err := Load(); err == nil {
		t.Fatal("expected error when S3_SECRET_ACCESS_KEY is empty")
	}
}

func setBaseEnv(t *testing.T) {
	t.Helper()
	t.Setenv("POSTGRES_URL", "postgres://u:p@localhost:5432/db")
	t.Setenv("S3_ENDPOINT", "http://s3.example:8333")
	t.Setenv("S3_ACCESS_KEY_ID", "k")
	t.Setenv("S3_SECRET_ACCESS_KEY", "s")
	t.Setenv("S3_PUBLIC_URL", "http://localhost:8333")
	setSitemapEnv(t)
}

func TestLoad_RedisStreamDefaults(t *testing.T) {
	setBaseEnv(t)
	t.Setenv("REDIS_STREAM_PUBLISH_REQUESTED", "")
	t.Setenv("REDIS_STREAM_PUBLISH_COMPLETED", "")
	t.Setenv("REDIS_PUBLISH_CONSUMER_GROUP", "")
	t.Setenv("REDIS_PUBLISH_CONSUMER_NAME", "")
	t.Setenv("REDIS_STREAM_UNPUBLISH_REQUESTED", "")
	t.Setenv("REDIS_STREAM_UNPUBLISH_COMPLETED", "")
	t.Setenv("REDIS_UNPUBLISH_CONSUMER_GROUP", "")
	t.Setenv("REDIS_UNPUBLISH_CONSUMER_NAME", "")
	t.Setenv("REDIS_STREAM_SITEMAP_REQUESTED", "")
	t.Setenv("REDIS_STREAM_SITEMAP_COMPLETED", "")
	t.Setenv("REDIS_SITEMAP_CONSUMER_GROUP", "")
	t.Setenv("REDIS_SITEMAP_CONSUMER_NAME", "")

	cfg, err := Load()
	if err != nil {
		t.Fatalf("Load: %v", err)
	}
	if cfg.RedisStreamPublishRequested != "publication.publish.requested" ||
		cfg.RedisStreamPublishCompleted != "publication.publish.completed" ||
		cfg.RedisPublishConsumerGroup != "publication-publish" ||
		cfg.RedisPublishConsumerName != "pub-worker-1" {
		t.Errorf("Publish defaults not wired: %+v", cfg)
	}
	if cfg.RedisStreamUnpublishRequested != "publication.unpublish.requested" ||
		cfg.RedisStreamUnpublishCompleted != "publication.unpublish.completed" ||
		cfg.RedisUnpublishConsumerGroup != "publication-unpublish" ||
		cfg.RedisUnpublishConsumerName != "unpub-worker-1" {
		t.Errorf("Unpublish defaults not wired: %+v", cfg)
	}
	if cfg.Sitemap.RequestedStream != "publication.sitemapping.requested" ||
		cfg.Sitemap.CompletedStream != "publication.sitemapping.completed" ||
		cfg.Sitemap.ConsumerGroup != "publication-sitemapping" ||
		cfg.Sitemap.ConsumerName != "sitemap-worker-1" {
		t.Errorf("Sitemap defaults not wired: %+v", cfg.Sitemap)
	}
}

func TestLoad_PopulatesUnifiedFields(t *testing.T) {
	setBaseEnv(t)
	cfg, err := Load()
	if err != nil {
		t.Fatalf("Load: %v", err)
	}
	if cfg.RedisStreamPublishRequested != "publication.publish.requested" ||
		cfg.RedisStreamPublishCompleted != "publication.publish.completed" ||
		cfg.RedisPublishConsumerGroup != "publication-publish" {
		t.Errorf("Unified publish config not wired: %+v", cfg)
	}
}

func TestLoad_SitemapConfig(t *testing.T) {
	setBaseEnv(t)
	cfg, err := Load()
	if err != nil {
		t.Fatalf("Load: %v", err)
	}
	if cfg.Sitemap.Target.Bucket != "foi-published" {
		t.Errorf("Target.Bucket = %q", cfg.Sitemap.Target.Bucket)
	}
	if cfg.Sitemap.Target.Prefix != "sitemap/" {
		t.Errorf("Target.Prefix = %q", cfg.Sitemap.Target.Prefix)
	}
	if cfg.Sitemap.Target.PublicBaseURL != "https://example.gov.bc.ca/sitemap/" {
		t.Errorf("Target.PublicBaseURL = %q", cfg.Sitemap.Target.PublicBaseURL)
	}
	if cfg.Sitemap.PageLimit != 50000 {
		t.Errorf("PageLimit = %d", cfg.Sitemap.PageLimit)
	}
	if cfg.Sitemap.RequestedStream != "publication.sitemapping.requested" ||
		cfg.Sitemap.CompletedStream != "publication.sitemapping.completed" ||
		cfg.Sitemap.ConsumerGroup != "test-sitemap-group" ||
		cfg.Sitemap.ConsumerName != "test-sitemap-worker" {
		t.Errorf("Sitemap streams not wired: %+v", cfg.Sitemap)
	}
	if got := cfg.Sitemap.SourceAllowlist; len(got) != 2 ||
		got[0] != "openinfo.workflow.service" ||
		got[1] != "proactivedisclosure.workflow.service" {
		t.Errorf("Sitemap.SourceAllowlist = %v", got)
	}
	if cfg.Sitemap.Target.IndexFileName != "sitemap_index.xml" ||
		cfg.Sitemap.Target.PageFilePattern != "sitemap_pages_%d.xml" {
		t.Errorf("Sitemap file defaults not set: %+v", cfg.Sitemap.Target)
	}
}

func TestLoad_LogLevelConfigured(t *testing.T) {
	setBaseEnv(t)
	t.Setenv("LOG_LEVEL", "debug")

	cfg, err := Load()
	if err != nil {
		t.Fatalf("Load: %v", err)
	}
	if cfg.LogLevel != slog.LevelDebug {
		t.Fatalf("LogLevel = %s, want DEBUG", cfg.LogLevel)
	}
}

func TestLoad_LogLevelInvalid(t *testing.T) {
	setBaseEnv(t)
	t.Setenv("LOG_LEVEL", "verbose")

	if _, err := Load(); err == nil {
		t.Fatal("expected error when LOG_LEVEL is invalid")
	}
}

func setSitemapEnv(t *testing.T) {
	t.Helper()
	t.Setenv("SITEMAP_BUCKET", "foi-published")
	t.Setenv("SITEMAP_PREFIX", "sitemap/")
	t.Setenv("SITEMAP_PUBLIC_BASE_URL", "https://example.gov.bc.ca/sitemap/")
	t.Setenv("SITEMAP_PAGE_LIMIT", "50000")
	t.Setenv("REDIS_STREAM_SITEMAP_REQUESTED", "publication.sitemapping.requested")
	t.Setenv("REDIS_STREAM_SITEMAP_COMPLETED", "publication.sitemapping.completed")
	t.Setenv("REDIS_SITEMAP_CONSUMER_GROUP", "test-sitemap-group")
	t.Setenv("REDIS_SITEMAP_CONSUMER_NAME", "test-sitemap-worker")
	t.Setenv("SITEMAP_SOURCE_ALLOWLIST", "openinfo.workflow.service,proactivedisclosure.workflow.service")
	t.Setenv("REDIS_STREAM_UNPUBLISH_REQUESTED", "publication.unpublish.requested")
	t.Setenv("REDIS_STREAM_UNPUBLISH_COMPLETED", "publication.unpublish.completed")
	t.Setenv("REDIS_UNPUBLISH_CONSUMER_GROUP", "publication-unpublish")
	t.Setenv("REDIS_UNPUBLISH_CONSUMER_NAME", "test-unpublish")
	t.Setenv("UNPUBLISH_SOURCE_ALLOWLIST", "openinfo.workflow.service,proactivedisclosure.workflow.service")
}
