package publish

import (
	"fmt"
	"strings"
	"time"

	"publication-service/internal/htmlindex"
	pub "publication-service/internal/publish"
)

func buildTemplateVars(d *Domain, res pub.CopyResult, publicURL string, now time.Time) htmlindex.TemplateVariables {
	base := strings.TrimRight(publicURL, "/") + "/" + d.Destination.Bucket + "/" + d.Destination.Prefix

	var letterLinks, otherLinks []htmlindex.Link
	var letterNames, letterSizes []string
	var fileNames, fileSizes []string

	for _, obj := range res.Objects {
		mb := fmt.Sprintf("%.2f", float64(obj.Size)/(1024*1024))
		lnk := htmlindex.Link{URL: base + obj.Key, FileName: obj.Key}
		if strings.HasPrefix(obj.Key, "Response_Letter_") {
			letterLinks = append(letterLinks, lnk)
			letterNames = append(letterNames, obj.Key)
			letterSizes = append(letterSizes, mb)
		} else {
			otherLinks = append(otherLinks, lnk)
			fileNames = append(fileNames, obj.Key)
			fileSizes = append(fileSizes, mb)
		}
	}

	htmlFile := d.RequestID + ".html"
	htmlURL := base + htmlFile

	allLinks := letterLinks
	allLinks = append(allLinks, otherLinks...)

	titlePrefix, _ := kindLabels(d.Kind)

	dcTitle := d.Title
	if dcTitle == "" {
		dcTitle = titlePrefix + " - " + d.RequestID
	}

	metaTags := []htmlindex.MetaTag{
		{Name: "dc.title", Content: d.Title},
		{Name: "dc.description", Content: d.Description},
		{Name: "high_level_subject", Content: d.HighLevelSubject},
		{Name: "dc.subject", Content: d.Subject},
		{Name: "dc.published_date", Content: d.PublishedDate},
		{Name: "timestamp", Content: fmt.Sprintf("%d", now.Unix())},
		{Name: "dc.contributor", Content: d.Contributor},
		{Name: "recorduid", Content: d.RequestID},
		{Name: "recordurl", Content: htmlURL},
		{Name: "month", Content: d.Month},
		{Name: "year", Content: d.Year},
		{Name: "letter", Content: strings.Join(letterNames, ",")},
		{Name: "letter_file_sizes", Content: strings.Join(letterSizes, ",")},
		{Name: "notes", Content: ""},
		{Name: "notes_file_sizes", Content: ""},
		{Name: "files", Content: strings.Join(fileNames, ",")},
		{Name: "file_sizes", Content: strings.Join(fileSizes, ",")},
		{Name: "applicant_type", Content: d.ApplicantType},
		{Name: "fees", Content: formatFees(d.Fees)},
		{Name: "position_title", Content: " "},
		{Name: "individual_name", Content: ""},
	}

	if d.Kind == pub.KindProactiveDisclosure {
		metaTags = append(metaTags,
			htmlindex.MetaTag{Name: "proactivedisclosure.category", Content: d.Category},
			htmlindex.MetaTag{Name: "proactivedisclosure.report_period", Content: d.ReportPeriod},
		)
	}

	return htmlindex.TemplateVariables{
		Title:    d.RequestID,
		MetaTags: metaTags,
		Links:    allLinks,
		Content:  dcTitle + " " + d.Description,
	}
}

func formatFees(fees *int) string {
	if fees == nil {
		return " "
	}
	return fmt.Sprintf("$%.2f", float64(*fees)/100)
}

func kindLabels(k pub.Kind) (titlePrefix, subject string) {
	switch k {
	case pub.KindProactiveDisclosure:
		return "Proactive Disclosure", "Proactive Disclosure"
	default:
		return "FOI Request", "FOI Request"
	}
}
