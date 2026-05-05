package publish

import (
	"testing"
	"time"

	pub "publication-service/internal/publish"
)

func intPtr(v int) *int { return &v }

func TestBuildTemplateVars_OpenInfo(t *testing.T) {
	d := &Domain{
		Kind:          pub.KindOpenInfo,
		RequestID:     "HTH-2025-52023",
		Description:   "Test request",
		PublishedDate: "2025-04-01",
		Contributor:   "Ministry of Test",
		Fees:          intPtr(150),
		ApplicantType: "Business",
		Destination:   pub.S3Location{Bucket: "foi-published", Prefix: "out/a7d9b2f1/"},
	}
	res := pub.CopyResult{Objects: []pub.CopiedObject{{Key: "doc.pdf", Size: 1048576}}}
	now := time.Date(2025, 4, 1, 12, 0, 0, 0, time.UTC)

	vars := buildTemplateVars(d, res, "https://public.example", now)

	found := false
	for _, m := range vars.MetaTags {
		if m.Name == "dc.title" {
			if m.Content != "FOI Request - HTH-2025-52023" {
				t.Errorf("dc.title = %q", m.Content)
			}
			found = true
		}
		if m.Name == "proactivedisclosure.category" {
			t.Error("openinfo should not have proactivedisclosure.category meta tag")
		}
	}
	if !found {
		t.Error("dc.title meta tag not found")
	}
	if vars.Content != "FOI Request - HTH-2025-52023 Test request" {
		t.Errorf("Content = %q", vars.Content)
	}
}

func TestBuildTemplateVars_ProactiveDisclosure(t *testing.T) {
	d := &Domain{
		Kind:          pub.KindProactiveDisclosure,
		RequestID:     "PD-2025-001",
		Description:   "PD test",
		PublishedDate: "2025-04-01",
		Contributor:   "Ministry of PD",
		ApplicantType: "",
		Category:      "Travel",
		ReportPeriod:  "2025-Q1",
		Destination:   pub.S3Location{Bucket: "foi-published", Prefix: "out/pd/"},
	}
	res := pub.CopyResult{Objects: []pub.CopiedObject{{Key: "doc.pdf", Size: 2097152}}}
	now := time.Date(2025, 4, 1, 12, 0, 0, 0, time.UTC)

	vars := buildTemplateVars(d, res, "https://public.example", now)

	hasCat, hasRP := false, false
	for _, m := range vars.MetaTags {
		if m.Name == "dc.title" && m.Content != "Proactive Disclosure - PD-2025-001" {
			t.Errorf("dc.title = %q", m.Content)
		}
		if m.Name == "proactivedisclosure.category" {
			hasCat = true
			if m.Content != "Travel" {
				t.Errorf("category = %q", m.Content)
			}
		}
		if m.Name == "proactivedisclosure.report_period" {
			hasRP = true
			if m.Content != "2025-Q1" {
				t.Errorf("report_period = %q", m.Content)
			}
		}
	}
	if !hasCat {
		t.Error("missing proactivedisclosure.category meta tag")
	}
	if !hasRP {
		t.Error("missing proactivedisclosure.report_period meta tag")
	}
	if vars.Content != "Proactive Disclosure - PD-2025-001 PD test" {
		t.Errorf("Content = %q", vars.Content)
	}
}

func TestBuildTemplateVars_ExplicitTitle(t *testing.T) {
	d := &Domain{
		Kind:          pub.KindOpenInfo,
		RequestID:     "HTH-2025-52023",
		Title:         "Custom Title From Event",
		Description:   "Test request",
		PublishedDate: "2025-04-01",
		Contributor:   "Ministry of Test",
		Destination:   pub.S3Location{Bucket: "foi-published", Prefix: "out/a7d9b2f1/"},
	}
	res := pub.CopyResult{Objects: []pub.CopiedObject{{Key: "doc.pdf", Size: 1048576}}}
	now := time.Date(2025, 4, 1, 12, 0, 0, 0, time.UTC)

	vars := buildTemplateVars(d, res, "https://public.example", now)

	for _, m := range vars.MetaTags {
		if m.Name == "dc.title" {
			if m.Content != "Custom Title From Event" {
				t.Errorf("dc.title = %q, want %q", m.Content, "Custom Title From Event")
			}
		}
	}
	if vars.Content != "Custom Title From Event Test request" {
		t.Errorf("Content = %q", vars.Content)
	}
}

func TestBuildTemplateVars_NilFeesRendersSpace(t *testing.T) {
	d := &Domain{
		Kind:        pub.KindOpenInfo,
		RequestID:   "X-001",
		Fees:        nil,
		Destination: pub.S3Location{Bucket: "b", Prefix: "p/"},
	}
	res := pub.CopyResult{}
	now := time.Date(2025, 1, 1, 0, 0, 0, 0, time.UTC)

	vars := buildTemplateVars(d, res, "https://public.example", now)

	for _, m := range vars.MetaTags {
		if m.Name == "fees" {
			if m.Content != " " {
				t.Errorf("fees = %q, want %q", m.Content, " ")
			}
			return
		}
	}
	t.Error("fees meta tag not found")
}

func TestBuildTemplateVars_SeparatesLetters(t *testing.T) {
	d := &Domain{
		Kind:        pub.KindOpenInfo,
		RequestID:   "X-001",
		Destination: pub.S3Location{Bucket: "b", Prefix: "p/"},
	}
	res := pub.CopyResult{Objects: []pub.CopiedObject{
		{Key: "Response_Letter_1.pdf", Size: 512000},
		{Key: "record.pdf", Size: 1024000},
	}}
	now := time.Date(2025, 1, 1, 0, 0, 0, 0, time.UTC)

	vars := buildTemplateVars(d, res, "https://cdn.example", now)

	if len(vars.Links) != 2 {
		t.Fatalf("expected 2 links, got %d", len(vars.Links))
	}
	if vars.Links[0].FileName != "Response_Letter_1.pdf" {
		t.Errorf("first link = %q, want letter", vars.Links[0].FileName)
	}
	if vars.Links[1].FileName != "record.pdf" {
		t.Errorf("second link = %q, want other file", vars.Links[1].FileName)
	}

	for _, m := range vars.MetaTags {
		if m.Name == "files" && m.Content != "record.pdf" {
			t.Errorf("files meta = %q, want copied files only", m.Content)
		}
		if m.Name == "file_sizes" && m.Content != "0.98" {
			t.Errorf("file_sizes meta = %q, want copied file sizes only", m.Content)
		}
	}
}
