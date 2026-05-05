package main

import (
	"context"
	"log/slog"
	"os"
	"os/signal"
	"syscall"
	"time"

	redislogging "github.com/redis/go-redis/v9/logging"

	"publication-service/internal/app"
	"publication-service/internal/config"
	"publication-service/internal/http/handlers"
	httpserver "publication-service/internal/http/server"
	"publication-service/internal/observability"
)

const tracerShutdownTimeout = 5 * time.Second

// Populated via -ldflags "-X main.version=... -X main.commit=... -X main.buildDate=..."
var (
	version   = "dev"
	commit    = "unknown"
	buildDate = "unknown"
)

func main() {
	cfg, err := config.Load()
	if err != nil {
		logger := slog.Default()
		logger.Error("config load failed", slog.Any("error", err))
		os.Exit(1)
	}

	redislogging.Disable()

	logger := observability.NewLogger(os.Stdout, cfg.ServiceName, cfg.Environment, cfg.LogLevel)
	slog.SetDefault(logger)

	ctx, stop := signal.NotifyContext(context.Background(), syscall.SIGINT, syscall.SIGTERM)
	defer stop()

	shutdownTracer, err := observability.InitTracer(ctx, os.Stderr, cfg.ServiceName, cfg.Environment)
	if err != nil {
		logger.Error("init tracer failed", slog.Any("error", err))
		os.Exit(1)
	}
	defer func() {
		sCtx, cancel := context.WithTimeout(context.Background(), tracerShutdownTimeout)
		defer cancel()
		if err := shutdownTracer(sCtx); err != nil {
			logger.Error("tracer shutdown failed", slog.Any("error", err))
		}
	}()

	build := handlers.BuildInfo{Version: version, Commit: commit, BuildDate: buildDate}
	httpOptions, cleanupHTTP, err := app.NewHTTPOptions(ctx, cfg, logger)
	if err != nil {
		logger.Error("http dependency wiring failed", slog.Any("error", err))
		os.Exit(1)
	}
	defer cleanupHTTP()

	srv := httpserver.New(":"+cfg.Port, logger, build, httpOptions)
	application := app.New(srv, logger, srv.Addr)

	// Start event-flow components in background; they share the same shutdown context.
	go func() {
		if err := app.RunEventFlow(ctx, cfg, logger); err != nil {
			logger.Error("event-flow stopped with error", slog.Any("error", err))
		}
	}()

	if err := application.Run(ctx); err != nil {
		logger.Error("application stopped with error", slog.Any("error", err))
		os.Exit(1)
	}
}
