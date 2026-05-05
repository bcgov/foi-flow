package sitemapping

import (
	"strings"
	"testing"
)

func TestURLSetAppendAndRender(t *testing.T) {
	page, err := ParseURLSet([]byte(`<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"></urlset>`))
	if err != nil {
		t.Fatalf("ParseURLSet: %v", err)
	}
	page.Append(URLEntry{
		Loc:     "https://example.gov.bc.ca/openinfopub/record.html",
		LastMod: "2026-04-01",
	})
	if !page.Contains("https://example.gov.bc.ca/openinfopub/record.html") {
		t.Fatal("expected appended URL")
	}
	got, err := page.Render()
	if err != nil {
		t.Fatalf("Render: %v", err)
	}
	if !strings.Contains(string(got), `<loc>https://example.gov.bc.ca/openinfopub/record.html</loc>`) {
		t.Fatalf("render missing loc:\n%s", got)
	}
}

func TestURLSetContainsParsedURL(t *testing.T) {
	page, err := ParseURLSet([]byte(`
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://example.gov.bc.ca/openinfopub/existing.html</loc>
    <lastmod>2026-04-01</lastmod>
  </url>
</urlset>`))
	if err != nil {
		t.Fatalf("ParseURLSet: %v", err)
	}
	if !page.Contains("https://example.gov.bc.ca/openinfopub/existing.html") {
		t.Fatal("expected parsed URL")
	}
	if page.Contains("https://example.gov.bc.ca/openinfopub/missing.html") {
		t.Fatal("did not expect missing URL")
	}
}

func TestSitemapIndexAppendAndRender(t *testing.T) {
	idx := NewSitemapIndex()
	idx.Append(SitemapEntry{
		Loc:     "https://example.gov.bc.ca/openinfopub/sitemap/sitemap_pages_1.xml",
		LastMod: "2026-04-01",
	})
	got, err := idx.Render()
	if err != nil {
		t.Fatalf("Render: %v", err)
	}
	if !strings.Contains(string(got), `<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">`) {
		t.Fatalf("missing sitemapindex root:\n%s", got)
	}
	if !strings.Contains(string(got), `<loc>https://example.gov.bc.ca/openinfopub/sitemap/sitemap_pages_1.xml</loc>`) {
		t.Fatalf("render missing sitemap loc:\n%s", got)
	}
}
