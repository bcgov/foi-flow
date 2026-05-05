package app

import (
	"context"
	"errors"
	"io"
	"log/slog"
	"net/http"
	"testing"
	"time"
)

func TestRunReturnsServerError(t *testing.T) {
	t.Parallel()

	wantErr := errors.New("listen failed")
	server := &stubServer{
		listenAndServeErr: wantErr,
	}

	app := New(
		server,
		slog.New(slog.NewTextHandler(io.Discard, nil)),
		":9085",
	)

	err := app.Run(context.Background())
	if !errors.Is(err, wantErr) {
		t.Fatalf("Run() error = %v, want %v", err, wantErr)
	}
}

func TestRunShutsDownOnContextCancellation(t *testing.T) {
	t.Parallel()

	server := &stubServer{
		listenAndServeErr: http.ErrServerClosed,
		listenStarted:     make(chan struct{}),
		shutdownReleased:  make(chan struct{}),
	}

	app := New(
		server,
		slog.New(slog.NewTextHandler(io.Discard, nil)),
		":9085",
	)

	ctx, cancel := context.WithCancel(context.Background())
	done := make(chan error, 1)

	go func() {
		done <- app.Run(ctx)
	}()

	<-server.listenStarted
	cancel()

	select {
	case err := <-done:
		if err != nil {
			t.Fatalf("Run() error = %v, want nil", err)
		}
	case <-time.After(time.Second):
		t.Fatal("Run() did not return after context cancellation")
	}

	if !server.shutdownCalled {
		t.Fatal("expected Shutdown to be called")
	}
}

type stubServer struct {
	listenAndServeErr error
	listenStarted     chan struct{}
	shutdownReleased  chan struct{}
	shutdownCalled    bool
}

func (s *stubServer) ListenAndServe() error {
	if s.listenStarted != nil {
		close(s.listenStarted)
	}

	if s.shutdownReleased != nil {
		<-s.shutdownReleased
	}

	return s.listenAndServeErr
}

func (s *stubServer) Shutdown(context.Context) error {
	s.shutdownCalled = true
	if s.shutdownReleased != nil {
		close(s.shutdownReleased)
	}

	return nil
}
