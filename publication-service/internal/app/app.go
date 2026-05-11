package app

import (
	"context"
	"errors"
	"fmt"
	"log/slog"
	"net/http"
	"time"
)

const shutdownTimeout = 10 * time.Second

type server interface {
	ListenAndServe() error
	Shutdown(ctx context.Context) error
}

type App struct {
	server          server
	logger          *slog.Logger
	addr            string
	shutdownTimeout time.Duration
}

func New(server server, logger *slog.Logger, addr string) *App {
	return &App{
		server:          server,
		logger:          logger,
		addr:            addr,
		shutdownTimeout: shutdownTimeout,
	}
}

func (a *App) Run(ctx context.Context) error {
	serverErr := make(chan error, 1)

	go func() {
		a.logger.Info("starting server", "addr", a.addr)

		err := a.server.ListenAndServe()
		if err != nil && !errors.Is(err, http.ErrServerClosed) {
			serverErr <- fmt.Errorf("listen and serve: %w", err)
			return
		}

		serverErr <- nil
	}()

	select {
	case err := <-serverErr:
		return err
	case <-ctx.Done():
		a.logger.Info("shutdown signal received")
	}

	shutdownCtx, cancel := context.WithTimeout(context.Background(), a.shutdownTimeout)
	defer cancel()

	if err := a.server.Shutdown(shutdownCtx); err != nil {
		return fmt.Errorf("shutdown server: %w", err)
	}

	a.logger.Info("server stopped")
	return nil
}
