package server

import (
	"io"
	"log/slog"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"publication-service/internal/http/handlers"
)

var testBuild = handlers.BuildInfo{Version: "v0.0.0-test", Commit: "abc123", BuildDate: "2026-04-15T00:00:00Z"}

func testLogger() *slog.Logger {
	return slog.New(slog.NewTextHandler(io.Discard, nil))
}

func TestNew(t *testing.T) {
	t.Parallel()

	srv := New(":9085", testLogger(), testBuild, Options{})

	if srv.Addr != ":9085" {
		t.Fatalf("server addr = %q, want %q", srv.Addr, ":9085")
	}

	if srv.ReadHeaderTimeout != 5*time.Second {
		t.Fatalf("read header timeout = %s, want %s", srv.ReadHeaderTimeout, 5*time.Second)
	}

	if srv.ReadTimeout != 10*time.Second {
		t.Fatalf("read timeout = %s, want %s", srv.ReadTimeout, 10*time.Second)
	}

	if srv.WriteTimeout != 10*time.Second {
		t.Fatalf("write timeout = %s, want %s", srv.WriteTimeout, 10*time.Second)
	}

	if srv.IdleTimeout != 60*time.Second {
		t.Fatalf("idle timeout = %s, want %s", srv.IdleTimeout, 60*time.Second)
	}
}

func TestRoutes(t *testing.T) {
	t.Parallel()

	tests := []struct {
		name           string
		method         string
		target         string
		wantStatusCode int
		wantBody       string
	}{
		{
			name:           "root route is registered",
			method:         http.MethodGet,
			target:         "/",
			wantStatusCode: http.StatusOK,
			wantBody:       "Hello, World!\n",
		},
		{
			name:           "health route is registered",
			method:         http.MethodGet,
			target:         "/health",
			wantStatusCode: http.StatusOK,
			wantBody:       "{\"status\":\"ok\"}\n",
		},
		{
			name:           "version route is registered",
			method:         http.MethodGet,
			target:         "/version",
			wantStatusCode: http.StatusOK,
			wantBody:       "{\"version\":\"v0.0.0-test\",\"commit\":\"abc123\",\"buildDate\":\"2026-04-15T00:00:00Z\"}\n",
		},
		{
			name:           "unknown route is not found",
			method:         http.MethodGet,
			target:         "/missing",
			wantStatusCode: http.StatusNotFound,
			wantBody:       "404 page not found\n",
		},
	}

	handler := buildHandler(testLogger(), testBuild, Options{})

	for _, tt := range tests {
		tt := tt
		t.Run(tt.name, func(t *testing.T) {
			t.Parallel()

			req := httptest.NewRequest(tt.method, tt.target, nil)
			rec := httptest.NewRecorder()

			handler.ServeHTTP(rec, req)

			if rec.Code != tt.wantStatusCode {
				t.Fatalf("status code = %d, want %d", rec.Code, tt.wantStatusCode)
			}

			if got := rec.Body.String(); got != tt.wantBody {
				t.Fatalf("body = %q, want %q", got, tt.wantBody)
			}
		})
	}
}

func TestRoutes_PublicationsRouteIsRegisteredWhenProvided(t *testing.T) {
	t.Parallel()

	publications := http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) {
		_, _ = w.Write([]byte("published\n"))
	})
	handler := buildHandler(testLogger(), testBuild, Options{Publications: publications})

	req := httptest.NewRequest(http.MethodPost, "/publications", nil)
	rec := httptest.NewRecorder()

	handler.ServeHTTP(rec, req)

	if rec.Code != http.StatusOK {
		t.Fatalf("status code = %d, want %d", rec.Code, http.StatusOK)
	}
	if got := rec.Body.String(); got != "published\n" {
		t.Fatalf("body = %q, want %q", got, "published\n")
	}
}

func TestShouldTraceHTTPRequest(t *testing.T) {
	t.Parallel()

	tests := []struct {
		name string
		path string
		want bool
	}{
		{name: "skips health checks", path: "/health", want: false},
		{name: "traces root requests", path: "/", want: true},
		{name: "traces version requests", path: "/version", want: true},
		{name: "traces publications requests", path: "/publications", want: true},
		{name: "traces unknown requests", path: "/missing", want: true},
	}

	for _, tt := range tests {
		tt := tt
		t.Run(tt.name, func(t *testing.T) {
			t.Parallel()

			req := httptest.NewRequest(http.MethodGet, tt.path, nil)

			if got := shouldTraceHTTPRequest(req); got != tt.want {
				t.Fatalf("shouldTraceHTTPRequest(%q) = %t, want %t", tt.path, got, tt.want)
			}
		})
	}
}

func TestSpanName_Publications(t *testing.T) {
	t.Parallel()

	req := httptest.NewRequest(http.MethodPost, "/publications", nil)

	if got := spanName("", req); got != "http.publications.post" {
		t.Fatalf("spanName = %q, want %q", got, "http.publications.post")
	}
}
