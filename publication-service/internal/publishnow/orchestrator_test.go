package publishnow

import (
	"context"
	"encoding/json"
	"errors"
	"testing"
	"time"

	"github.com/jackc/pgx/v5/pgconn"

	"publication-service/internal/events"
	pubpub "publication-service/internal/publication/publish"
	pub "publication-service/internal/publish"
	"publication-service/internal/sitemapping"
)

type fakePublisher struct {
	calls int
	got   *pubpub.Domain
	res   pub.PublishResult
	err   error
}

func (f *fakePublisher) Handle(_ context.Context, d *pubpub.Domain) (pub.PublishResult, error) {
	f.calls++
	f.got = d
	return f.res, f.err
}

type fakeSitemapWriter struct {
	calls int
	got   sitemapping.Request
	res   sitemapping.Result
	err   error
}

func (f *fakeSitemapWriter) Handle(_ context.Context, req sitemapping.Request) (sitemapping.Result, error) {
	f.calls++
	f.got = req
	return f.res, f.err
}

type fakeSitemapClaimer struct {
	calls int
	got   pub.ClaimRequest
	err   error
}

func (f *fakeSitemapClaimer) Claim(_ context.Context, req pub.ClaimRequest) (pub.ClaimResult, error) {
	f.calls++
	f.got = req
	return pub.ClaimResult{EventID: req.EventID, Won: true}, f.err
}

func TestPublish_DecodesWrapperAndPublishesOpenInfoWithSitemap(t *testing.T) {
	fp := &fakePublisher{res: pub.PublishResult{
		PublicationID: "HTH-2025-52023",
		HTMLKey:       "out/HTH-2025-52023.html",
		PublicURL:     "https://pub.example/foi-published/out/HTH-2025-52023.html",
	}}
	sm := &fakeSitemapWriter{res: sitemapping.Result{
		SitemapIndexKey: "openinfo/sitemap/sitemap.xml",
		SitemapPageKey:  "openinfo/sitemap/sitemap-1.xml",
		Status:          sitemapping.StatusWritten,
	}}
	claimer := &fakeSitemapClaimer{}
	orch := New(fp, sm).WithSitemapClaimer(claimer)

	resp, err := orch.Publish(context.Background(), wrapperJSON(PublicationTypeOpenInfo, openInfoPayload()))
	if err != nil {
		t.Fatalf("Publish: %v", err)
	}
	if fp.calls != 1 {
		t.Fatalf("publisher calls = %d, want 1", fp.calls)
	}
	if fp.got.RequestID != "HTH-2025-52023" {
		t.Fatalf("publisher RequestID = %q", fp.got.RequestID)
	}
	if sm.calls != 1 {
		t.Fatalf("sitemap calls = %d, want 1", sm.calls)
	}
	if sm.got.Kind != pub.KindOpenInfoSitemap {
		t.Fatalf("sitemap kind = %q", sm.got.Kind)
	}
	if claimer.calls != 1 {
		t.Fatalf("sitemap claim calls = %d, want 1", claimer.calls)
	}
	if claimer.got.EventID != sm.got.SourceEventID {
		t.Fatalf("sitemap claim event ID = %q, want %q", claimer.got.EventID, sm.got.SourceEventID)
	}
	if claimer.got.Kind != pub.KindOpenInfoSitemap {
		t.Fatalf("sitemap claim kind = %q, want %q", claimer.got.Kind, pub.KindOpenInfoSitemap)
	}
	if claimer.got.EventType != events.TypePublicationSitemappingRequested {
		t.Fatalf("sitemap claim event type = %q, want %q", claimer.got.EventType, events.TypePublicationSitemappingRequested)
	}
	if sm.got.PublicURL != fp.res.PublicURL {
		t.Fatalf("sitemap PublicURL = %q, want %q", sm.got.PublicURL, fp.res.PublicURL)
	}
	if got := sm.got.LastModified.Format("2006-01-02"); got != "2026-02-03" {
		t.Fatalf("sitemap LastModified = %q", got)
	}
	want := Response{
		Status:          "completed",
		PublicationType: "openinfo",
		PublicationID:   "HTH-2025-52023",
		PublicURL:       fp.res.PublicURL,
		HTMLKey:         fp.res.HTMLKey,
		SitemapIndexKey: sm.res.SitemapIndexKey,
		SitemapPageKey:  sm.res.SitemapPageKey,
		SitemapResult:   string(sitemapping.StatusWritten),
	}
	if resp != want {
		t.Fatalf("response = %+v, want %+v", resp, want)
	}
}

func TestPublish_PublishesProactiveDisclosureWithSitemap(t *testing.T) {
	fp := &fakePublisher{res: pub.PublishResult{
		PublicationID: "PD-2026-001",
		HTMLKey:       "pd/out/PD-2026-001.html",
		PublicURL:     "https://pub.example/pd-published/pd/out/PD-2026-001.html",
	}}
	sm := &fakeSitemapWriter{res: sitemapping.Result{
		SitemapIndexKey: "pd/sitemap/sitemap.xml",
		SitemapPageKey:  "pd/sitemap/sitemap-1.xml",
		Status:          sitemapping.StatusAlreadyPresent,
	}}
	claimer := &fakeSitemapClaimer{}
	orch := New(fp, sm).WithSitemapClaimer(claimer)

	resp, err := orch.Publish(context.Background(), wrapperJSON(PublicationTypeProactiveDisclosure, pdPayload()))
	if err != nil {
		t.Fatalf("Publish: %v", err)
	}
	if fp.calls != 1 {
		t.Fatalf("publisher calls = %d, want 1", fp.calls)
	}
	if fp.got.Category != "Travel Expenses" {
		t.Fatalf("publisher Category = %q", fp.got.Category)
	}
	if sm.got.Kind != pub.KindProactiveDisclosureSitemap {
		t.Fatalf("sitemap kind = %q", sm.got.Kind)
	}
	if claimer.calls != 1 {
		t.Fatalf("sitemap claim calls = %d, want 1", claimer.calls)
	}
	if claimer.got.Kind != pub.KindProactiveDisclosureSitemap {
		t.Fatalf("sitemap claim kind = %q, want %q", claimer.got.Kind, pub.KindProactiveDisclosureSitemap)
	}
	if claimer.got.EventType != events.TypePublicationSitemappingRequested {
		t.Fatalf("sitemap claim event type = %q, want %q", claimer.got.EventType, events.TypePublicationSitemappingRequested)
	}
	if resp.PublicationType != "proactivedisclosure" || resp.SitemapResult != string(sitemapping.StatusAlreadyPresent) {
		t.Fatalf("response = %+v", resp)
	}
}

func TestPublish_RejectsUnsupportedPublicationType(t *testing.T) {
	orch := New(&fakePublisher{}, &fakeSitemapWriter{})

	_, err := orch.Publish(context.Background(), wrapperJSON(PublicationType("bad"), openInfoPayload()))
	if !IsClientError(err) {
		t.Fatalf("err = %v, want client error", err)
	}
}

func TestPublish_RejectsMissingPayload(t *testing.T) {
	orch := New(&fakePublisher{}, &fakeSitemapWriter{})

	_, err := orch.Publish(context.Background(), []byte(`{"publication_type":"openinfo"}`))
	if !IsClientError(err) {
		t.Fatalf("err = %v, want client error", err)
	}
}

func TestPublish_RejectsInvalidPublishedDate(t *testing.T) {
	payload := openInfoPayload()
	payload["published_date"] = "02/03/2026"
	orch := New(&fakePublisher{res: pub.PublishResult{
		PublicationID: "HTH-2025-52023",
		PublicURL:     "https://pub.example/foi-published/out/HTH-2025-52023.html",
	}}, &fakeSitemapWriter{})

	_, err := orch.Publish(context.Background(), wrapperJSON(PublicationTypeOpenInfo, payload))
	if !IsClientError(err) {
		t.Fatalf("err = %v, want client error", err)
	}
}

func TestPublish_PublishFailurePreventsSitemapCall(t *testing.T) {
	sentinel := errors.New("copy failed")
	fp := &fakePublisher{err: sentinel}
	sm := &fakeSitemapWriter{}
	orch := New(fp, sm)

	_, err := orch.Publish(context.Background(), wrapperJSON(PublicationTypeOpenInfo, openInfoPayload()))
	if !errors.Is(err, sentinel) {
		t.Fatalf("err = %v, want %v", err, sentinel)
	}
	if sm.calls != 0 {
		t.Fatalf("sitemap calls = %d, want 0", sm.calls)
	}
}

func TestPublish_DuplicateSitemapClaimStillReturnsExistingResult(t *testing.T) {
	fp := &fakePublisher{res: pub.PublishResult{
		PublicationID: "HTH-2025-52023",
		HTMLKey:       "out/HTH-2025-52023.html",
		PublicURL:     "https://pub.example/foi-published/out/HTH-2025-52023.html",
	}}
	sm := &fakeSitemapWriter{res: sitemapping.Result{
		SitemapIndexKey: "openinfo/sitemap/sitemap.xml",
		SitemapPageKey:  "openinfo/sitemap/sitemap-1.xml",
		Status:          sitemapping.StatusAlreadyPresent,
	}}
	claimer := &fakeSitemapClaimer{err: &pgconn.PgError{Code: "23505"}}
	orch := New(fp, sm).WithSitemapClaimer(claimer)

	resp, err := orch.Publish(context.Background(), wrapperJSON(PublicationTypeOpenInfo, openInfoPayload()))
	if err != nil {
		t.Fatalf("Publish: %v", err)
	}
	if sm.calls != 1 {
		t.Fatalf("sitemap calls = %d, want 1", sm.calls)
	}
	if resp.SitemapResult != string(sitemapping.StatusAlreadyPresent) {
		t.Fatalf("SitemapResult = %q, want %q", resp.SitemapResult, sitemapping.StatusAlreadyPresent)
	}
}

func TestPublish_SitemapFailureReturnsAfterPublish(t *testing.T) {
	sentinel := errors.New("sitemap failed")
	fp := &fakePublisher{res: pub.PublishResult{
		PublicationID: "HTH-2025-52023",
		PublicURL:     "https://pub.example/foi-published/out/HTH-2025-52023.html",
	}}
	sm := &fakeSitemapWriter{err: sentinel}
	orch := New(fp, sm)

	_, err := orch.Publish(context.Background(), wrapperJSON(PublicationTypeOpenInfo, openInfoPayload()))
	if !errors.Is(err, sentinel) {
		t.Fatalf("err = %v, want %v", err, sentinel)
	}
	if fp.calls != 1 || sm.calls != 1 {
		t.Fatalf("calls: pub=%d sitemap=%d", fp.calls, sm.calls)
	}
}

func wrapperJSON(t PublicationType, payload map[string]any) []byte {
	body, err := json.Marshal(Request{PublicationType: t, Payload: mustRaw(payload)})
	if err != nil {
		panic(err)
	}
	return body
}

func mustRaw(v any) json.RawMessage {
	b, err := json.Marshal(v)
	if err != nil {
		panic(err)
	}
	return b
}

func openInfoPayload() map[string]any {
	return map[string]any{
		"tenant_id":       "a7d9b2f1-4c3e-4e8b-9a21-1c2e8f7b9d10",
		"kind":            "openinfo",
		"axis_request_id": "HTH-2025-52023",
		"description":     "A briefing note",
		"published_date":  time.Date(2026, 2, 3, 0, 0, 0, 0, time.UTC).Format("2006-01-02"),
		"contributor":     "Ministry of Health",
		"fees":            0,
		"applicant_type":  "Interest Group",
		"source":          map[string]any{"bucket": "foi-raw", "prefix": "incoming/a/"},
		"destination":     map[string]any{"bucket": "foi-published", "prefix": "out/a/"},
	}
}

func pdPayload() map[string]any {
	p := openInfoPayload()
	p["kind"] = "proactivedisclosure"
	p["axis_request_id"] = "PD-2026-001"
	p["proactivedisclosure_category"] = "Travel Expenses"
	p["report_period"] = "2026-Q1"
	return p
}
