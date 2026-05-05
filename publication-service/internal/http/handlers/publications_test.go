package handlers

import (
	"bytes"
	"context"
	"errors"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	"publication-service/internal/publishnow"
)

type fakePublicationsOrchestrator struct {
	calls int
	body  []byte
	res   publishnow.Response
	err   error
}

func (f *fakePublicationsOrchestrator) Publish(_ context.Context, body []byte) (publishnow.Response, error) {
	f.calls++
	f.body = append([]byte(nil), body...)
	return f.res, f.err
}

func TestPublications_ReturnsJSONResponse(t *testing.T) {
	orch := &fakePublicationsOrchestrator{res: publishnow.Response{
		Status:          "completed",
		PublicationType: "openinfo",
		PublicationID:   "HTH-2025-52023",
		PublicURL:       "https://pub.example/out/HTH-2025-52023.html",
		HTMLKey:         "out/HTH-2025-52023.html",
		SitemapIndexKey: "sitemap.xml",
		SitemapPageKey:  "sitemap-1.xml",
		SitemapResult:   "written",
	}}
	handler := Publications(orch)

	rec := httptest.NewRecorder()
	req := httptest.NewRequest(http.MethodPost, "/publications", strings.NewReader(`{"publication_type":"openinfo","payload":{}}`))

	handler.ServeHTTP(rec, req)

	if rec.Code != http.StatusOK {
		t.Fatalf("status = %d, want %d; body=%s", rec.Code, http.StatusOK, rec.Body.String())
	}
	if got := rec.Header().Get("Content-Type"); got != "application/json" {
		t.Fatalf("Content-Type = %q", got)
	}
	if !strings.Contains(rec.Body.String(), `"publication_type":"openinfo"`) {
		t.Fatalf("body = %s", rec.Body.String())
	}
	if orch.calls != 1 || !bytes.Contains(orch.body, []byte(`"publication_type":"openinfo"`)) {
		t.Fatalf("orchestrator calls=%d body=%s", orch.calls, string(orch.body))
	}
}

func TestPublications_ReturnsJSONResponseForProactiveDisclosure(t *testing.T) {
	orch := &fakePublicationsOrchestrator{res: publishnow.Response{
		Status:          "completed",
		PublicationType: "proactivedisclosure",
		PublicationID:   "PD-2026-001",
	}}
	handler := Publications(orch)

	rec := httptest.NewRecorder()
	req := httptest.NewRequest(http.MethodPost, "/publications", strings.NewReader(`{"publication_type":"proactivedisclosure","payload":{}}`))

	handler.ServeHTTP(rec, req)

	if rec.Code != http.StatusOK {
		t.Fatalf("status = %d, want %d; body=%s", rec.Code, http.StatusOK, rec.Body.String())
	}
	if !strings.Contains(rec.Body.String(), `"publication_type":"proactivedisclosure"`) {
		t.Fatalf("body = %s", rec.Body.String())
	}
}

func TestPublications_RejectsNonPOST(t *testing.T) {
	handler := Publications(&fakePublicationsOrchestrator{})

	rec := httptest.NewRecorder()
	req := httptest.NewRequest(http.MethodGet, "/publications", nil)

	handler.ServeHTTP(rec, req)

	if rec.Code != http.StatusMethodNotAllowed {
		t.Fatalf("status = %d, want %d", rec.Code, http.StatusMethodNotAllowed)
	}
}

func TestPublications_RejectsMalformedJSON(t *testing.T) {
	handler := Publications(&fakePublicationsOrchestrator{})

	rec := httptest.NewRecorder()
	req := httptest.NewRequest(http.MethodPost, "/publications", strings.NewReader(`{`))

	handler.ServeHTTP(rec, req)

	if rec.Code != http.StatusBadRequest {
		t.Fatalf("status = %d, want %d", rec.Code, http.StatusBadRequest)
	}
}

func TestPublications_MapsClientErrorsToBadRequest(t *testing.T) {
	orch := &fakePublicationsOrchestrator{err: publishnow.NewClientError("unsupported publication_type")}
	handler := Publications(orch)

	rec := httptest.NewRecorder()
	req := httptest.NewRequest(http.MethodPost, "/publications", strings.NewReader(`{"publication_type":"bad","payload":{}}`))

	handler.ServeHTTP(rec, req)

	if rec.Code != http.StatusBadRequest {
		t.Fatalf("status = %d, want %d; body=%s", rec.Code, http.StatusBadRequest, rec.Body.String())
	}
}

func TestPublications_MapsOrchestratorFailuresToInternalServerError(t *testing.T) {
	orch := &fakePublicationsOrchestrator{err: errors.New("copy failed")}
	handler := Publications(orch)

	rec := httptest.NewRecorder()
	req := httptest.NewRequest(http.MethodPost, "/publications", strings.NewReader(`{"publication_type":"openinfo","payload":{}}`))

	handler.ServeHTTP(rec, req)

	if rec.Code != http.StatusInternalServerError {
		t.Fatalf("status = %d, want %d; body=%s", rec.Code, http.StatusInternalServerError, rec.Body.String())
	}
}
