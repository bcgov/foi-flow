package handlers

import (
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestHello(t *testing.T) {
	t.Parallel()

	tests := []struct {
		name           string
		method         string
		target         string
		wantStatusCode int
		wantBody       string
		wantContent    string
	}{
		{
			name:           "root returns hello world",
			method:         http.MethodGet,
			target:         "/",
			wantStatusCode: http.StatusOK,
			wantBody:       "Hello, World!\n",
			wantContent:    "text/plain; charset=utf-8",
		},
		{
			name:           "non root path returns not found",
			method:         http.MethodGet,
			target:         "/missing",
			wantStatusCode: http.StatusNotFound,
			wantBody:       "404 page not found\n",
			wantContent:    "text/plain; charset=utf-8",
		},
		{
			name:           "method not allowed",
			method:         http.MethodPost,
			target:         "/",
			wantStatusCode: http.StatusMethodNotAllowed,
			wantBody:       "Method Not Allowed\n",
			wantContent:    "text/plain; charset=utf-8",
		},
	}

	for _, tt := range tests {
		tt := tt
		t.Run(tt.name, func(t *testing.T) {
			t.Parallel()

			req := httptest.NewRequest(tt.method, tt.target, nil)
			rec := httptest.NewRecorder()

			Hello(rec, req)

			if rec.Code != tt.wantStatusCode {
				t.Fatalf("status code = %d, want %d", rec.Code, tt.wantStatusCode)
			}

			if got := rec.Body.String(); got != tt.wantBody {
				t.Fatalf("body = %q, want %q", got, tt.wantBody)
			}

			if got := rec.Header().Get("Content-Type"); got != tt.wantContent {
				t.Fatalf("content type = %q, want %q", got, tt.wantContent)
			}
		})
	}
}

func TestHealth(t *testing.T) {
	t.Parallel()

	tests := []struct {
		name           string
		method         string
		wantStatusCode int
		wantBody       string
		wantContent    string
	}{
		{
			name:           "returns ok json",
			method:         http.MethodGet,
			wantStatusCode: http.StatusOK,
			wantBody:       "{\"status\":\"ok\"}\n",
			wantContent:    "application/json",
		},
		{
			name:           "rejects unsupported methods",
			method:         http.MethodPost,
			wantStatusCode: http.StatusMethodNotAllowed,
			wantBody:       "Method Not Allowed\n",
			wantContent:    "text/plain; charset=utf-8",
		},
	}

	for _, tt := range tests {
		tt := tt
		t.Run(tt.name, func(t *testing.T) {
			t.Parallel()

			req := httptest.NewRequest(tt.method, "/health", nil)
			rec := httptest.NewRecorder()

			Health(rec, req)

			if rec.Code != tt.wantStatusCode {
				t.Fatalf("status code = %d, want %d", rec.Code, tt.wantStatusCode)
			}

			if got := rec.Body.String(); got != tt.wantBody {
				t.Fatalf("body = %q, want %q", got, tt.wantBody)
			}

			if got := rec.Header().Get("Content-Type"); got != tt.wantContent {
				t.Fatalf("content type = %q, want %q", got, tt.wantContent)
			}
		})
	}
}
