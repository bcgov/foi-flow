package htmlindex_test

import (
	"strings"
	"testing"

	"publication-service/internal/htmlindex"
)

func TestRender_ContainsTitle(t *testing.T) {
	vars := htmlindex.TemplateVariables{
		Title: "HTH-2025-52023",
		MetaTags: []htmlindex.MetaTag{
			{Name: "fees", Content: "$0.00"},
		},
		Links:   []htmlindex.Link{{URL: "https://example.com/file.pdf", FileName: "file.pdf"}},
		Content: "FOI Request - HTH-2025-52023 description",
	}
	got, err := htmlindex.Render(vars)
	if err != nil {
		t.Fatalf("Render: %v", err)
	}
	html := string(got)
	for _, want := range []string{
		"<title>HTH-2025-52023</title>",
		`<meta name="fees" content="$0.00">`,
		`<a href="https://example.com/file.pdf">file.pdf</a>`,
		"FOI Request - HTH-2025-52023 description",
	} {
		if !strings.Contains(html, want) {
			t.Errorf("output missing %q\ngot:\n%s", want, html)
		}
	}
}

func TestRender_EmptyLinksAndMetaTags(t *testing.T) {
	vars := htmlindex.TemplateVariables{Title: "EMPTY"}
	got, err := htmlindex.Render(vars)
	if err != nil {
		t.Fatalf("Render: %v", err)
	}
	if !strings.Contains(string(got), "<title>EMPTY</title>") {
		t.Errorf("title not found in output: %s", got)
	}
}
