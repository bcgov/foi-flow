package sitemapping

import (
	"context"
	"errors"
	"strings"
	"testing"
	"time"

	pub "publication-service/internal/publish"
)

type fakeStore struct {
	objects map[string][]byte
	errPut  error
}

func (f *fakeStore) Get(_ context.Context, bucket, key string) ([]byte, error) {
	b, ok := f.objects[bucket+"/"+key]
	if !ok {
		return nil, ErrObjectNotFound
	}
	return append([]byte(nil), b...), nil
}

func (f *fakeStore) Upload(_ context.Context, bucket, key string, body []byte, _ string) error {
	if f.errPut != nil {
		return f.errPut
	}
	f.objects[bucket+"/"+key] = append([]byte(nil), body...)
	return nil
}

func (f *fakeStore) Delete(_ context.Context, bucket, key string) error {
	delete(f.objects, bucket+"/"+key)
	return nil
}

type fakeResultStore struct {
	completed           Result
	completedOK         bool
	marked              []Result
	findCompletedKind   pub.Kind
	findCompletedTenant string
	findCompletedCorrID string
	findCompletedCalls  int
}

func (f *fakeResultStore) FindCompleted(_ context.Context, kind pub.Kind, tenantID string, correlationID string) (Result, bool, error) {
	f.findCompletedKind = kind
	f.findCompletedTenant = tenantID
	f.findCompletedCorrID = correlationID
	f.findCompletedCalls++
	return f.completed, f.completedOK, nil
}

func (f *fakeResultStore) MarkSucceeded(_ context.Context, _ string, result Result) error {
	f.marked = append(f.marked, result)
	return nil
}

func testTarget() Target {
	return Target{
		Bucket:          "public",
		Prefix:          "openinfopub/sitemap/",
		PublicBaseURL:   "https://example.gov.bc.ca/openinfopub/sitemap/",
		IndexFileName:   "sitemap_index.xml",
		PageFilePattern: "sitemap_pages_%d.xml",
		PageLimit:       2,
	}
}

func testRequest() Request {
	return Request{
		Kind:                 pub.KindOpenInfoSitemap,
		TenantID:             "a7d9b2f1-4c3e-4e8b-9a21-1c2e8f7b9d10",
		PublicationID:        "HTH-2025-52023:v1",
		PublicURL:            "https://example.gov.bc.ca/openinfopub/packages/HTH-2025-52023/openinfo/HTH-2025-52023.html",
		LastModified:         time.Date(2026, 4, 1, 0, 0, 0, 0, time.UTC),
		PublicationResultRef: "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d90",
		SourceEventID:        "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d90",
		CorrelationID:        "corr-1",
	}
}

func existingSitemapResult() Result {
	return Result{
		Kind:                 pub.KindOpenInfoSitemap,
		TenantID:             "a7d9b2f1-4c3e-4e8b-9a21-1c2e8f7b9d10",
		PublicationID:        "HTH-2025-52023:v1",
		PublicURL:            "https://example.gov.bc.ca/openinfopub/packages/HTH-2025-52023/openinfo/HTH-2025-52023.html",
		LastModified:         time.Date(2026, 4, 1, 0, 0, 0, 0, time.UTC),
		SitemapIndexKey:      "openinfopub/sitemap/sitemap_index.xml",
		SitemapPageKey:       "openinfopub/sitemap/sitemap_pages_1.xml",
		SitemapPageURL:       "https://example.gov.bc.ca/openinfopub/sitemap/sitemap_pages_1.xml",
		Status:               StatusWritten,
		IndexUpdated:         false,
		PublicationResultRef: "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d90",
		CompletedAt:          time.Date(2026, 4, 21, 12, 0, 0, 0, time.UTC),
	}
}

func TestWriter_WritesFirstURLAndIndex(t *testing.T) {
	store := &fakeStore{objects: map[string][]byte{}}
	repo := &fakeResultStore{}
	w := NewWriter(store, repo, map[pub.Kind]Target{pub.KindOpenInfoSitemap: testTarget()})
	w.now = func() time.Time { return time.Date(2026, 4, 21, 12, 0, 0, 0, time.UTC) }

	got, err := w.Handle(context.Background(), testRequest())
	if err != nil {
		t.Fatalf("Handle: %v", err)
	}
	if got.Status != StatusWritten {
		t.Fatalf("Status = %q, want %q", got.Status, StatusWritten)
	}
	if !got.IndexUpdated {
		t.Fatal("expected index update for first sitemap page")
	}
	page := string(store.objects["public/openinfopub/sitemap/sitemap_pages_1.xml"])
	if !strings.Contains(page, testRequest().PublicURL) {
		t.Fatalf("page missing public URL:\n%s", page)
	}
	index := string(store.objects["public/openinfopub/sitemap/sitemap_index.xml"])
	if !strings.Contains(index, "https://example.gov.bc.ca/openinfopub/sitemap/sitemap_pages_1.xml") {
		t.Fatalf("index missing first page:\n%s", index)
	}
	if len(repo.marked) != 1 {
		t.Fatalf("MarkSucceeded calls = %d, want 1", len(repo.marked))
	}
}

func TestWriter_FindsCompletedByKindTenantAndCorrelationID(t *testing.T) {
	store := &fakeStore{objects: map[string][]byte{}}
	repo := &fakeResultStore{}
	w := NewWriter(store, repo, map[pub.Kind]Target{pub.KindOpenInfoSitemap: testTarget()})

	if _, err := w.Handle(context.Background(), testRequest()); err != nil {
		t.Fatalf("Handle: %v", err)
	}
	if repo.findCompletedCalls != 1 {
		t.Fatalf("FindCompleted calls = %d, want 1", repo.findCompletedCalls)
	}
	if repo.findCompletedKind != testRequest().Kind {
		t.Fatalf("FindCompleted kind = %q, want %q", repo.findCompletedKind, testRequest().Kind)
	}
	if repo.findCompletedTenant != testRequest().TenantID {
		t.Fatalf("FindCompleted tenant = %q, want %q", repo.findCompletedTenant, testRequest().TenantID)
	}
	if repo.findCompletedCorrID != testRequest().CorrelationID {
		t.Fatalf("FindCompleted correlation = %q, want %q", repo.findCompletedCorrID, testRequest().CorrelationID)
	}
}

func TestWriter_AppendsBucketAndPrefixToPublicBaseURL(t *testing.T) {
	target := Target{
		Bucket:          "dev-openinfopub",
		Prefix:          "sitemap/",
		PublicBaseURL:   "https://citz-foi-prod.objectstore.gov.bc.ca",
		IndexFileName:   "sitemap_index.xml",
		PageFilePattern: "sitemap_pages_%d.xml",
		PageLimit:       2,
	}
	store := &fakeStore{objects: map[string][]byte{}}
	repo := &fakeResultStore{}
	w := NewWriter(store, repo, map[pub.Kind]Target{pub.KindOpenInfoSitemap: target})

	got, err := w.Handle(context.Background(), testRequest())
	if err != nil {
		t.Fatalf("Handle: %v", err)
	}
	wantURL := "https://citz-foi-prod.objectstore.gov.bc.ca/dev-openinfopub/sitemap/sitemap_pages_1.xml"
	if got.SitemapPageURL != wantURL {
		t.Fatalf("SitemapPageURL = %q", got.SitemapPageURL)
	}
	index := string(store.objects["dev-openinfopub/sitemap/sitemap_index.xml"])
	if !strings.Contains(index, wantURL) {
		t.Fatalf("index missing sitemap page URL:\n%s", index)
	}
}

func TestWriter_ReturnsAlreadyPresentForCompletedPublication(t *testing.T) {
	existing := existingSitemapResult()
	existing.Status = StatusAlreadyPresent
	store := &fakeStore{objects: map[string][]byte{}}
	repo := &fakeResultStore{completed: existing, completedOK: true}
	w := NewWriter(store, repo, map[pub.Kind]Target{pub.KindOpenInfoSitemap: testTarget()})

	got, err := w.Handle(context.Background(), testRequest())
	if err != nil {
		t.Fatalf("Handle: %v", err)
	}
	if got != existing {
		t.Fatalf("got %#v, want %#v", got, existing)
	}
	if len(store.objects) != 0 {
		t.Fatalf("expected no storage writes, got %d objects", len(store.objects))
	}
	if len(repo.marked) != 0 {
		t.Fatalf("expected no MarkSucceeded calls, got %d", len(repo.marked))
	}
}

func TestWriter_RollsToNextPageAtLimit(t *testing.T) {
	target := testTarget()
	target.PageLimit = 1
	store := &fakeStore{objects: map[string][]byte{
		"public/openinfopub/sitemap/sitemap_index.xml": []byte(`<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap>
    <loc>https://example.gov.bc.ca/openinfopub/sitemap/sitemap_pages_1.xml</loc>
    <lastmod>2026-04-01</lastmod>
  </sitemap>
</sitemapindex>`),
		"public/openinfopub/sitemap/sitemap_pages_1.xml": []byte(`<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://example.gov.bc.ca/openinfopub/existing.html</loc>
    <lastmod>2026-04-01</lastmod>
  </url>
</urlset>`),
	}}
	repo := &fakeResultStore{}
	w := NewWriter(store, repo, map[pub.Kind]Target{pub.KindOpenInfoSitemap: target})

	got, err := w.Handle(context.Background(), testRequest())
	if err != nil {
		t.Fatalf("Handle: %v", err)
	}
	if got.SitemapPageKey != "openinfopub/sitemap/sitemap_pages_2.xml" {
		t.Fatalf("SitemapPageKey = %q", got.SitemapPageKey)
	}
	if !got.IndexUpdated {
		t.Fatal("expected index update on rollover")
	}
	page2 := string(store.objects["public/openinfopub/sitemap/sitemap_pages_2.xml"])
	if !strings.Contains(page2, testRequest().PublicURL) {
		t.Fatalf("new page missing public URL:\n%s", page2)
	}
	index := string(store.objects["public/openinfopub/sitemap/sitemap_index.xml"])
	if !strings.Contains(index, "sitemap_pages_2.xml") {
		t.Fatalf("index missing rolled page:\n%s", index)
	}
}

func TestWriter_DoesNotMarkSucceededWhenUploadFails(t *testing.T) {
	sentinel := errors.New("upload failed")
	store := &fakeStore{objects: map[string][]byte{}, errPut: sentinel}
	repo := &fakeResultStore{}
	w := NewWriter(store, repo, map[pub.Kind]Target{pub.KindOpenInfoSitemap: testTarget()})

	_, err := w.Handle(context.Background(), testRequest())
	if !errors.Is(err, sentinel) {
		t.Fatalf("Handle error = %v, want %v", err, sentinel)
	}
	if len(repo.marked) != 0 {
		t.Fatalf("expected no MarkSucceeded calls, got %d", len(repo.marked))
	}
}

func TestSitemapLocKey_DoesNotDoublePrefixRelativePath(t *testing.T) {
	target := Target{
		Prefix:        "dev-openinfopub/sitemap/",
		PublicBaseURL: "https://example.gov.bc.ca/",
	}

	got, err := sitemapLocKey(target, "https://example.gov.bc.ca/dev-openinfopub/sitemap/sitemap_pages_1.xml")
	if err != nil {
		t.Fatalf("sitemapLocKey: %v", err)
	}
	if got != "dev-openinfopub/sitemap/sitemap_pages_1.xml" {
		t.Fatalf("sitemapLocKey = %q", got)
	}
}

func TestSitemapLocKey_StripsBucketFromPathStylePublicBaseURL(t *testing.T) {
	target := Target{
		Bucket:        "dev-openinfopub",
		Prefix:        "sitemap/",
		PublicBaseURL: "https://citz-foi-prod.objectstore.gov.bc.ca",
	}

	got, err := sitemapLocKey(target, "https://citz-foi-prod.objectstore.gov.bc.ca/dev-openinfopub/sitemap/sitemap_pages_1.xml")
	if err != nil {
		t.Fatalf("sitemapLocKey: %v", err)
	}
	if got != "sitemap/sitemap_pages_1.xml" {
		t.Fatalf("sitemapLocKey = %q", got)
	}
}

func TestWriter_NormalizesExistingDuplicatedSitemapPageURL(t *testing.T) {
	target := Target{
		Bucket:          "dev-openinfopub",
		Prefix:          "sitemap/",
		PublicBaseURL:   "https://citz-foi-prod.objectstore.gov.bc.ca",
		IndexFileName:   "sitemap_index.xml",
		PageFilePattern: "sitemap_pages_%d.xml",
		PageLimit:       2,
	}
	store := &fakeStore{objects: map[string][]byte{
		"dev-openinfopub/sitemap/sitemap_index.xml": []byte(`<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap>
    <loc>https://citz-foi-prod.objectstore.gov.bc.ca/dev-openinfopub/sitemap/dev-openinfopub/sitemap/sitemap_pages_1.xml</loc>
    <lastmod>2026-04-01</lastmod>
  </sitemap>
</sitemapindex>`),
		"dev-openinfopub/sitemap/sitemap_pages_1.xml": []byte(`<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://example.gov.bc.ca/openinfopub/existing.html</loc>
    <lastmod>2026-04-01</lastmod>
  </url>
</urlset>`),
	}}
	repo := &fakeResultStore{}
	w := NewWriter(store, repo, map[pub.Kind]Target{pub.KindOpenInfoSitemap: target})

	got, err := w.Handle(context.Background(), testRequest())
	if err != nil {
		t.Fatalf("Handle: %v", err)
	}
	wantURL := "https://citz-foi-prod.objectstore.gov.bc.ca/dev-openinfopub/sitemap/sitemap_pages_1.xml"
	if got.SitemapPageURL != wantURL {
		t.Fatalf("SitemapPageURL = %q", got.SitemapPageURL)
	}
	index := string(store.objects["dev-openinfopub/sitemap/sitemap_index.xml"])
	if strings.Contains(index, "/sitemap/dev-openinfopub/sitemap/") {
		t.Fatalf("index still contains duplicated sitemap URL:\n%s", index)
	}
	if !strings.Contains(index, wantURL) {
		t.Fatalf("index missing normalized sitemap URL:\n%s", index)
	}
}
