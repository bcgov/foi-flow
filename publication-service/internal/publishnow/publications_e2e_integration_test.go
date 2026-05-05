package publishnow

import (
	"context"
	"errors"
	"io"
	"log/slog"
	"strings"
	"testing"
	"time"

	pubpub "publication-service/internal/publication/publish"
	pub "publication-service/internal/publish"
	"publication-service/internal/sitemapping"
)

type memoryObjectStore struct {
	objects map[string]map[string][]byte
}

func newMemoryObjectStore() *memoryObjectStore {
	return &memoryObjectStore{objects: map[string]map[string][]byte{}}
}

func (s *memoryObjectStore) put(bucket, key string, body []byte) {
	if s.objects[bucket] == nil {
		s.objects[bucket] = map[string][]byte{}
	}
	s.objects[bucket][key] = append([]byte(nil), body...)
}

func (s *memoryObjectStore) Copy(_ context.Context, src, dst pub.S3Location) (pub.CopyResult, error) {
	var result pub.CopyResult
	for key, body := range s.objects[src.Bucket] {
		if !strings.HasPrefix(key, src.Prefix) {
			continue
		}
		rel := strings.TrimPrefix(key, src.Prefix)
		if rel == "" || strings.HasSuffix(rel, "/") {
			continue
		}
		s.put(dst.Bucket, dst.Prefix+rel, body)
		result.Objects = append(result.Objects, pub.CopiedObject{Key: rel, Size: int64(len(body))})
		result.ObjectsCopied++
		result.BytesCopied += int64(len(body))
	}
	return result, nil
}

func (s *memoryObjectStore) Upload(_ context.Context, bucket, key string, body []byte, _ string) error {
	s.put(bucket, key, body)
	return nil
}

func (s *memoryObjectStore) Get(_ context.Context, bucket, key string) ([]byte, error) {
	body, ok := s.objects[bucket][key]
	if !ok {
		return nil, sitemapping.ErrObjectNotFound
	}
	return append([]byte(nil), body...), nil
}

func (s *memoryObjectStore) Delete(_ context.Context, bucket, key string) error {
	delete(s.objects[bucket], key)
	return nil
}

type memoryResultStore struct {
	results map[string]sitemapping.Result
}

func newMemoryResultStore() *memoryResultStore {
	return &memoryResultStore{results: map[string]sitemapping.Result{}}
}

func (s *memoryResultStore) FindCompleted(_ context.Context, kind pub.Kind, publicationID string) (sitemapping.Result, bool, error) {
	result, ok := s.results[string(kind)+":"+publicationID]
	return result, ok, nil
}

func (s *memoryResultStore) MarkSucceeded(_ context.Context, _ string, result sitemapping.Result) error {
	if result.PublicationID == "" {
		return errors.New("publication id required")
	}
	s.results[string(result.Kind)+":"+result.PublicationID] = result
	return nil
}

func TestPublish_OpenInfoEndToEndWithoutRedis(t *testing.T) {
	store := newMemoryObjectStore()
	store.put("foi-raw", "incoming/a/Response_Letter_HTH-2025-52023.pdf", []byte("letter"))
	orchestrator := newTestOrchestrator(store)

	resp, err := orchestrator.Publish(context.Background(), wrapperJSON(PublicationTypeOpenInfo, openInfoPayload()))
	if err != nil {
		t.Fatalf("Publish: %v", err)
	}

	assertObject(t, store, "foi-published", "out/a/Response_Letter_HTH-2025-52023.pdf", "letter")
	html := assertObject(t, store, "foi-published", "out/a/HTH-2025-52023.html", "")
	for _, want := range []string{"HTH-2025-52023", "Response_Letter_HTH-2025-52023.pdf"} {
		if !strings.Contains(html, want) {
			t.Fatalf("HTML missing %q:\n%s", want, html)
		}
	}
	index := assertObject(t, store, "sitemap-bucket", "openinfo/sitemap/sitemap_index.xml", "")
	page := assertObject(t, store, "sitemap-bucket", "openinfo/sitemap/sitemap_pages_1.xml", "")
	if !strings.Contains(index, "https://sitemap.example/openinfo/sitemap/sitemap_pages_1.xml") {
		t.Fatalf("sitemap index missing page URL:\n%s", index)
	}
	if !strings.Contains(page, resp.PublicURL) {
		t.Fatalf("sitemap page missing public URL %q:\n%s", resp.PublicURL, page)
	}
}

func TestPublish_ProactiveDisclosureEndToEndWithoutRedis(t *testing.T) {
	store := newMemoryObjectStore()
	store.put("foi-raw", "incoming/a/notes.pdf", []byte("notes"))
	orchestrator := newTestOrchestrator(store)

	resp, err := orchestrator.Publish(context.Background(), wrapperJSON(PublicationTypeProactiveDisclosure, pdPayload()))
	if err != nil {
		t.Fatalf("Publish: %v", err)
	}

	assertObject(t, store, "foi-published", "out/a/notes.pdf", "notes")
	html := assertObject(t, store, "foi-published", "out/a/PD-2026-001.html", "")
	for _, want := range []string{`name="proactivedisclosure.category"`, `Travel Expenses`, `name="proactivedisclosure.report_period"`} {
		if !strings.Contains(html, want) {
			t.Fatalf("PD HTML missing %q:\n%s", want, html)
		}
	}
	index := assertObject(t, store, "sitemap-bucket", "pd/sitemap/sitemap_index.xml", "")
	page := assertObject(t, store, "sitemap-bucket", "pd/sitemap/sitemap_pages_1.xml", "")
	if !strings.Contains(index, "https://sitemap.example/pd/sitemap/sitemap_pages_1.xml") {
		t.Fatalf("PD sitemap index missing page URL:\n%s", index)
	}
	if !strings.Contains(page, resp.PublicURL) {
		t.Fatalf("PD sitemap page missing public URL %q:\n%s", resp.PublicURL, page)
	}
}

func newTestOrchestrator(store *memoryObjectStore) *Orchestrator {
	logger := slog.New(slog.NewTextHandler(io.Discard, nil))
	targets := map[pub.Kind]sitemapping.Target{
		pub.KindOpenInfoSitemap: {
			Bucket:          "sitemap-bucket",
			Prefix:          "openinfo/sitemap/",
			PublicBaseURL:   "https://sitemap.example/openinfo/sitemap/",
			IndexFileName:   "sitemap_index.xml",
			PageFilePattern: "sitemap_pages_%d.xml",
			PageLimit:       50000,
		},
		pub.KindProactiveDisclosureSitemap: {
			Bucket:          "sitemap-bucket",
			Prefix:          "pd/sitemap/",
			PublicBaseURL:   "https://sitemap.example/pd/sitemap/",
			IndexFileName:   "sitemap_index.xml",
			PageFilePattern: "sitemap_pages_%d.xml",
			PageLimit:       50000,
		},
	}
	writer := sitemapping.NewWriter(store, newMemoryResultStore(), targets)
	svc := pubpub.NewService(store, store, "https://objects.example", logger)
	orchestrator := New(svc, writer)
	orchestrator.now = func() time.Time { return time.Date(2026, 4, 27, 12, 0, 0, 0, time.UTC) }
	return orchestrator
}

func assertObject(t *testing.T, store *memoryObjectStore, bucket, key, want string) string {
	t.Helper()
	body, err := store.Get(context.Background(), bucket, key)
	if err != nil {
		t.Fatalf("Get(%s, %s): %v", bucket, key, err)
	}
	got := string(body)
	if want != "" && got != want {
		t.Fatalf("object %s/%s = %q, want %q", bucket, key, got, want)
	}
	return got
}
