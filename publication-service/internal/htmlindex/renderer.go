package htmlindex

import (
	"bytes"
	_ "embed"
	"html/template"
)

//go:embed template.html
var templateSrc string

// TemplateVariables is the data passed to the HTML index template.
type TemplateVariables struct {
	Title    string
	MetaTags []MetaTag
	Links    []Link
	Content  string
}

// MetaTag represents a single <meta name="..." content="..."> element.
type MetaTag struct {
	Name    string
	Content string
}

// Link represents a single <a href="..."> element.
type Link struct {
	URL      string
	FileName string
}

var tmpl = template.Must(template.New("index").Parse(templateSrc))

// Render executes the HTML index template with the given variables.
func Render(vars TemplateVariables) ([]byte, error) {
	var buf bytes.Buffer
	if err := tmpl.Execute(&buf, vars); err != nil {
		return nil, err
	}
	return buf.Bytes(), nil
}
