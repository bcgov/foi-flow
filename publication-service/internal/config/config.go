package config

import (
	"errors"
	"fmt"
	"log/slog"
	"os"
	"strconv"
	"strings"
	"time"
)

const (
	defaultPort        = "9085"
	defaultServiceName = "publication-service"
	defaultEnvironment = "dev"
	defaultPageLimit   = 50000

	defaultRedisStreamPublishRequested   = "publication.publish.requested"
	defaultRedisStreamPublishCompleted   = "publication.publish.completed"
	defaultRedisPublishConsumerGroup     = "publication-publish"
	defaultRedisPublishConsumerName      = "pub-worker-1"
	defaultRedisStreamUnpublishRequested = "publication.unpublish.requested"
	defaultRedisStreamUnpublishCompleted = "publication.unpublish.completed"
	defaultRedisUnpublishConsumerGroup   = "publication-unpublish"
	defaultRedisUnpublishConsumerName    = "unpub-worker-1"
	defaultRedisStreamSitemapRequested   = "publication.sitemapping.requested"
	defaultRedisStreamSitemapCompleted   = "publication.sitemapping.completed"
	defaultRedisSitemapConsumerGroup     = "publication-sitemapping"
	defaultRedisSitemapConsumerName      = "sitemap-worker-1"
)

type Config struct {
	Port        string
	ServiceName string
	Environment string
	LogLevel    slog.Level

	PostgresURL string

	RedisAddr     string
	RedisPassword string
	RedisTLS      bool

	RedisStreamPublishRequested string
	RedisStreamPublishCompleted string
	RedisPublishConsumerGroup   string
	RedisPublishConsumerName    string

	RedisStreamUnpublishRequested string
	RedisStreamUnpublishCompleted string
	RedisUnpublishConsumerGroup   string
	RedisUnpublishConsumerName    string

	ConsumerWorkers       int
	SchedulerInterval     time.Duration
	OutboxInterval        time.Duration
	RetryMaxAttempts      int
	StuckTimeout          time.Duration
	HandlerTimeout        time.Duration
	MaxInFlightEvents     int
	PoisonRepeatThreshold int

	StreamMaxLen       int64
	StreamTrimInterval time.Duration

	SourceAllowlist          []string
	UnpublishSourceAllowlist []string

	S3      S3Config
	Sitemap SitemapConfig

	PublishWindow PublishWindowConfig
}

type S3Config struct {
	Endpoint        string
	Region          string
	AccessKeyID     string
	SecretAccessKey string
	UsePathStyle    bool
	RequestTimeout  time.Duration
	PublicURL       string // public-facing base URL for HTML link generation
}

type SitemapConfig struct {
	PageLimit int

	Target SitemapTargetConfig

	RequestedStream string
	CompletedStream string
	ConsumerGroup   string
	ConsumerName    string

	SourceAllowlist []string
}

type SitemapTargetConfig struct {
	Bucket          string
	Prefix          string
	PublicBaseURL   string
	IndexFileName   string
	PageFilePattern string
}

type TimeOfDay struct {
	Hour   int
	Minute int
}

func (t TimeOfDay) String() string {
	return fmt.Sprintf("%02d:%02d", t.Hour, t.Minute)
}

func (t TimeOfDay) Before(other TimeOfDay) bool {
	return t.Hour < other.Hour || (t.Hour == other.Hour && t.Minute < other.Minute)
}

type PublishWindowConfig struct {
	Enabled  bool
	Start    TimeOfDay
	End      TimeOfDay
	Location *time.Location
}

func Load() (*Config, error) {
	cfg := &Config{
		Port:        envOr("PORT", defaultPort),
		ServiceName: envOr("SERVICE_NAME", defaultServiceName),
		Environment: envOr("ENVIRONMENT", defaultEnvironment),

		RedisAddr:       getEnvDefault("REDIS_ADDR", "localhost:6379"),
		RedisPassword:   os.Getenv("REDIS_PASSWORD"),
		SourceAllowlist: splitAndTrim(getEnvDefault("SOURCE_ALLOWLIST", "openinfo.enqueue.service")),
	}

	var err error
	if cfg.LogLevel, err = parseLogLevelDefault("LOG_LEVEL", slog.LevelInfo); err != nil {
		return nil, err
	}

	cfg.PostgresURL = os.Getenv("POSTGRES_URL")
	if cfg.PostgresURL == "" {
		return nil, errors.New("config: POSTGRES_URL is required")
	}

	cfg.S3.Endpoint = os.Getenv("S3_ENDPOINT")
	if cfg.S3.Endpoint == "" {
		return nil, errors.New("config: S3_ENDPOINT is required")
	}
	cfg.S3.AccessKeyID = os.Getenv("S3_ACCESS_KEY_ID")
	if cfg.S3.AccessKeyID == "" {
		return nil, errors.New("config: S3_ACCESS_KEY_ID is required")
	}
	cfg.S3.SecretAccessKey = os.Getenv("S3_SECRET_ACCESS_KEY")
	if cfg.S3.SecretAccessKey == "" {
		return nil, errors.New("config: S3_SECRET_ACCESS_KEY is required")
	}
	cfg.S3.PublicURL = os.Getenv("S3_PUBLIC_URL")
	if cfg.S3.PublicURL == "" {
		return nil, errors.New("config: S3_PUBLIC_URL is required")
	}
	cfg.S3.Region = getEnvDefault("S3_REGION", "us-east-1")

	if cfg.S3.UsePathStyle, err = parseBoolDefault("S3_USE_PATH_STYLE", true); err != nil {
		return nil, err
	}
	if cfg.S3.RequestTimeout, err = parseDurationDefault("S3_REQUEST_TIMEOUT", 30*time.Second); err != nil {
		return nil, err
	}
	if cfg.RedisTLS, err = parseBoolDefault("REDIS_TLS", false); err != nil {
		return nil, err
	}
	if cfg.ConsumerWorkers, err = parseIntDefault("CONSUMER_WORKERS", 1); err != nil {
		return nil, err
	}
	if cfg.SchedulerInterval, err = parseDurationDefault("SCHEDULER_INTERVAL", 5*time.Second); err != nil {
		return nil, err
	}
	if cfg.OutboxInterval, err = parseDurationDefault("OUTBOX_INTERVAL", time.Second); err != nil {
		return nil, err
	}
	if cfg.RetryMaxAttempts, err = parseIntDefault("RETRY_MAX_ATTEMPTS", 5); err != nil {
		return nil, err
	}
	if cfg.StuckTimeout, err = parseDurationDefault("STUCK_TIMEOUT", 2*time.Minute); err != nil {
		return nil, err
	}
	if cfg.HandlerTimeout, err = parseDurationDefault("HANDLER_TIMEOUT", 30*time.Second); err != nil {
		return nil, err
	}
	if cfg.MaxInFlightEvents, err = parseIntDefault("MAX_IN_FLIGHT_EVENTS", 64); err != nil {
		return nil, err
	}
	if cfg.PoisonRepeatThreshold, err = parseIntDefault("POISON_REPEAT_THRESHOLD", 3); err != nil {
		return nil, err
	}
	if cfg.StreamMaxLen, err = parseInt64Default("STREAM_MAXLEN", 100000); err != nil {
		return nil, err
	}
	if cfg.StreamTrimInterval, err = parseDurationDefault("STREAM_TRIM_INTERVAL", time.Hour); err != nil {
		return nil, err
	}

	cfg.RedisStreamPublishRequested = getEnvDefault("REDIS_STREAM_PUBLISH_REQUESTED", defaultRedisStreamPublishRequested)
	cfg.RedisStreamPublishCompleted = getEnvDefault("REDIS_STREAM_PUBLISH_COMPLETED", defaultRedisStreamPublishCompleted)
	cfg.RedisPublishConsumerGroup = getEnvDefault("REDIS_PUBLISH_CONSUMER_GROUP", defaultRedisPublishConsumerGroup)
	cfg.RedisPublishConsumerName = getEnvDefault("REDIS_PUBLISH_CONSUMER_NAME", defaultRedisPublishConsumerName)

	cfg.RedisStreamUnpublishRequested = getEnvDefault("REDIS_STREAM_UNPUBLISH_REQUESTED", defaultRedisStreamUnpublishRequested)
	cfg.RedisStreamUnpublishCompleted = getEnvDefault("REDIS_STREAM_UNPUBLISH_COMPLETED", defaultRedisStreamUnpublishCompleted)
	cfg.RedisUnpublishConsumerGroup = getEnvDefault("REDIS_UNPUBLISH_CONSUMER_GROUP", defaultRedisUnpublishConsumerGroup)
	cfg.RedisUnpublishConsumerName = getEnvDefault("REDIS_UNPUBLISH_CONSUMER_NAME", defaultRedisUnpublishConsumerName)

	cfg.UnpublishSourceAllowlist = splitAndTrim(getEnvDefault(
		"UNPUBLISH_SOURCE_ALLOWLIST",
		"openinfo.workflow.service,proactivedisclosure.workflow.service",
	))

	if cfg.Sitemap.PageLimit, err = parseIntDefault("SITEMAP_PAGE_LIMIT", defaultPageLimit); err != nil {
		return nil, err
	}
	if cfg.Sitemap.PageLimit <= 0 {
		return nil, errors.New("config: SITEMAP_PAGE_LIMIT must be positive")
	}
	sitemapBucket := os.Getenv("SITEMAP_BUCKET")
	if sitemapBucket == "" {
		return nil, errors.New("config: SITEMAP_BUCKET is required")
	}
	sitemapPrefix := os.Getenv("SITEMAP_PREFIX")
	if sitemapPrefix == "" {
		return nil, errors.New("config: SITEMAP_PREFIX is required")
	}
	sitemapPublicBaseURL := os.Getenv("SITEMAP_PUBLIC_BASE_URL")
	if sitemapPublicBaseURL == "" {
		return nil, errors.New("config: SITEMAP_PUBLIC_BASE_URL is required")
	}
	cfg.Sitemap.Target = SitemapTargetConfig{
		Bucket:          sitemapBucket,
		Prefix:          sitemapPrefix,
		PublicBaseURL:   sitemapPublicBaseURL,
		IndexFileName:   "sitemap_index.xml",
		PageFilePattern: "sitemap_pages_%d.xml",
	}
	cfg.Sitemap.RequestedStream = getEnvDefault("REDIS_STREAM_SITEMAP_REQUESTED", defaultRedisStreamSitemapRequested)
	cfg.Sitemap.CompletedStream = getEnvDefault("REDIS_STREAM_SITEMAP_COMPLETED", defaultRedisStreamSitemapCompleted)
	cfg.Sitemap.ConsumerGroup = getEnvDefault("REDIS_SITEMAP_CONSUMER_GROUP", defaultRedisSitemapConsumerGroup)
	cfg.Sitemap.ConsumerName = getEnvDefault("REDIS_SITEMAP_CONSUMER_NAME", defaultRedisSitemapConsumerName)
	cfg.Sitemap.SourceAllowlist = splitAndTrim(getEnvDefault(
		"SITEMAP_SOURCE_ALLOWLIST",
		"openinfo.workflow.service,proactivedisclosure.workflow.service",
	))

	if cfg.PublishWindow.Enabled, err = parseBoolDefault("PUBLISH_WINDOW_ENABLED", true); err != nil {
		return nil, err
	}
	if cfg.PublishWindow.Enabled {
		startStr := getEnvDefault("PUBLISH_WINDOW_START", "13:00")
		if cfg.PublishWindow.Start, err = parseTimeOfDay(startStr); err != nil {
			return nil, fmt.Errorf("config: PUBLISH_WINDOW_START: %w", err)
		}
		endStr := getEnvDefault("PUBLISH_WINDOW_END", "15:00")
		if cfg.PublishWindow.End, err = parseTimeOfDay(endStr); err != nil {
			return nil, fmt.Errorf("config: PUBLISH_WINDOW_END: %w", err)
		}
		if !cfg.PublishWindow.Start.Before(cfg.PublishWindow.End) {
			return nil, errors.New("config: PUBLISH_WINDOW_START must be before PUBLISH_WINDOW_END")
		}
		tzName := getEnvDefault("PUBLISH_WINDOW_TIMEZONE", "America/Vancouver")
		cfg.PublishWindow.Location, err = time.LoadLocation(tzName)
		if err != nil {
			return nil, fmt.Errorf("config: PUBLISH_WINDOW_TIMEZONE: %w", err)
		}
	}

	return cfg, nil
}

func parseTimeOfDay(s string) (TimeOfDay, error) {
	t, err := time.Parse("15:04", s)
	if err != nil {
		return TimeOfDay{}, fmt.Errorf("invalid time %q: %w", s, err)
	}
	return TimeOfDay{Hour: t.Hour(), Minute: t.Minute()}, nil
}

func envOr(key, fallback string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return fallback
}

func getEnvDefault(k, def string) string {
	if v, ok := os.LookupEnv(k); ok && v != "" {
		return v
	}
	return def
}

func parseIntDefault(k string, def int) (int, error) {
	v, ok := os.LookupEnv(k)
	if !ok || v == "" {
		return def, nil
	}
	n, err := strconv.Atoi(v)
	if err != nil {
		return 0, fmt.Errorf("config: %s: %w", k, err)
	}
	return n, nil
}

func parseInt64Default(k string, def int64) (int64, error) {
	v, ok := os.LookupEnv(k)
	if !ok || v == "" {
		return def, nil
	}
	n, err := strconv.ParseInt(v, 10, 64)
	if err != nil {
		return 0, fmt.Errorf("config: %s: %w", k, err)
	}
	return n, nil
}

func parseBoolDefault(k string, def bool) (bool, error) {
	v, ok := os.LookupEnv(k)
	if !ok || v == "" {
		return def, nil
	}
	b, err := strconv.ParseBool(v)
	if err != nil {
		return false, fmt.Errorf("config: %s: %w", k, err)
	}
	return b, nil
}

func parseDurationDefault(k string, def time.Duration) (time.Duration, error) {
	v, ok := os.LookupEnv(k)
	if !ok || v == "" {
		return def, nil
	}
	d, err := time.ParseDuration(v)
	if err != nil {
		return 0, fmt.Errorf("config: %s: %w", k, err)
	}
	return d, nil
}

func parseLogLevelDefault(k string, def slog.Level) (slog.Level, error) {
	v, ok := os.LookupEnv(k)
	if !ok || v == "" {
		return def, nil
	}
	var level slog.Level
	if err := level.UnmarshalText([]byte(strings.ToUpper(strings.TrimSpace(v)))); err != nil {
		return 0, fmt.Errorf("config: %s: %w", k, err)
	}
	return level, nil
}

func splitAndTrim(s string) []string {
	parts := strings.Split(s, ",")
	out := parts[:0]
	for _, p := range parts {
		p = strings.TrimSpace(p)
		if p != "" {
			out = append(out, p)
		}
	}
	return out
}

func hostnameOrPID() string {
	if h, err := os.Hostname(); err == nil && h != "" {
		return h
	}
	return strconv.Itoa(os.Getpid())
}
