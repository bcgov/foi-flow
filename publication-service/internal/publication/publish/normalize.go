package publish

import (
	"encoding/json"
	"fmt"
	"net/url"
	"strings"

	"publication-service/internal/events"
	pub "publication-service/internal/publish"
)

// AdditionalFile is a single extra file to copy to the destination.
type AdditionalFile struct {
	ID       int
	Filename string
	S3URI    string
}

type rawAdditionalFile struct {
	ID       int    `json:"additionalfileid"`
	Filename string `json:"filename"`
	S3URI    string `json:"s3uripath"`
	IsActive bool   `json:"isactive"`
}

// Domain is the version-stripped, handler-friendly view of a publish request.
type Domain struct {
	EventID       string
	CorrelationID string
	TenantID      string
	Kind          pub.Kind
	Source        pub.S3Location
	Destination   pub.S3Location
	RequestID     string
	Description   string
	PublishedDate string
	Contributor   string
	Fees             *int
	ApplicantType    string
	HighLevelSubject string
	Subject          string
	Month            string
	Year             string

	// Title is the caller-supplied dc.title value.
	// When empty the template falls back to "<kind> - <RequestID>".
	Title string

	// PD-specific (zero-valued for openinfo)
	Category             string
	ReportPeriod         string
	FOIMinistryRequestID *int
	FOIRequestID         *int

	// AdditionalFiles are extra files to copy to the destination.
	AdditionalFiles []AdditionalFile
}

type requestedPayloadV1 struct {
	TenantID             string          `json:"tenant_id"`
	Kind                 string          `json:"kind"`
	Source               rawLocation     `json:"source"`
	Destination          rawLocation     `json:"destination"`
	AxisRequestID        string          `json:"axis_request_id"`
	Description          string          `json:"description"`
	PublishedDate        string          `json:"published_date"`
	Contributor          string          `json:"contributor"`
	Fees                 *int            `json:"fees"`
	ApplicantType        json.RawMessage `json:"applicant_type"`
	HighLevelSubject     string          `json:"high_level_subject"`
	Subject              string          `json:"subject"`
	Month                string          `json:"month"`
	Year                 string          `json:"year"`
	Title                string          `json:"title"`
	Category             string          `json:"proactivedisclosure_category"`
	ReportPeriod         string          `json:"report_period"`
	FOIMinistryRequestID *int            `json:"foiministryrequest_id"`
	FOIRequestID         *int            `json:"foirequest_id"`
	AdditionalFiles      []rawAdditionalFile `json:"additionalfiles"`
}

type rawLocation struct {
	Bucket string `json:"bucket"`
	Prefix string `json:"prefix"`
}

// Normalize converts a validated envelope into the Domain struct.
func Normalize(env *events.Envelope) (*Domain, error) {
	if env.SchemaVersion != events.SchemaVersionV1 {
		return nil, pub.NewPermanent(fmt.Sprintf("publish.Normalize: unsupported schema_version %q", env.SchemaVersion))
	}
	var p requestedPayloadV1
	if err := json.Unmarshal(env.Payload, &p); err != nil {
		return nil, fmt.Errorf("publish.Normalize: payload: %w", err)
	}

	kind, err := parseKind(p.Kind)
	if err != nil {
		return nil, err
	}

	src, err := canonicalizeLocation(p.Source, "source")
	if err != nil {
		return nil, err
	}
	dst, err := canonicalizeLocation(p.Destination, "destination")
	if err != nil {
		return nil, err
	}
	if err := checkNoOverlap(src, dst); err != nil {
		return nil, err
	}

	applicantType := ""
	if len(p.ApplicantType) > 0 && string(p.ApplicantType) != "null" {
		if err := json.Unmarshal(p.ApplicantType, &applicantType); err != nil {
			return nil, pub.NewPermanent(fmt.Sprintf("publish.Normalize: applicant_type: %v", err))
		}
	}

	if kind == pub.KindProactiveDisclosure {
		if p.Category == "" || p.ReportPeriod == "" {
			return nil, pub.NewPermanent("publish.Normalize: proactivedisclosure requires proactivedisclosure_category and report_period")
		}
	}

	var additionalFiles []AdditionalFile
	for _, af := range p.AdditionalFiles {
		if af.IsActive {
			additionalFiles = append(additionalFiles, AdditionalFile{
				ID:       af.ID,
				Filename: af.Filename,
				S3URI:    af.S3URI,
			})
		}
	}

	return &Domain{
		EventID:              env.EventID,
		CorrelationID:        env.CorrelationID,
		TenantID:             p.TenantID,
		Kind:                 kind,
		Source:               src,
		Destination:          dst,
		RequestID:            p.AxisRequestID,
		Description:          p.Description,
		PublishedDate:        p.PublishedDate,
		Contributor:          p.Contributor,
		Fees:                 p.Fees,
		ApplicantType:        applicantType,
		HighLevelSubject:     p.HighLevelSubject,
		Subject:              p.Subject,
		Month:                p.Month,
		Year:                 p.Year,
		Title:                p.Title,
		Category:             p.Category,
		ReportPeriod:         p.ReportPeriod,
		FOIMinistryRequestID: p.FOIMinistryRequestID,
		FOIRequestID:         p.FOIRequestID,
		AdditionalFiles:      additionalFiles,
	}, nil
}

func parseKind(raw string) (pub.Kind, error) {
	switch raw {
	case "openinfo":
		return pub.KindOpenInfo, nil
	case "proactivedisclosure":
		return pub.KindProactiveDisclosure, nil
	default:
		return pub.KindUnknown, pub.NewPermanent(fmt.Sprintf("publish.Normalize: unknown kind %q", raw))
	}
}

func canonicalizeLocation(loc rawLocation, label string) (pub.S3Location, error) {
	bucket := strings.TrimSpace(loc.Bucket)
	if bucket == "" {
		return pub.S3Location{}, pub.NewPermanent(
			fmt.Sprintf("publish.Normalize: %s.bucket is empty", label))
	}
	prefix := loc.Prefix
	if prefix != "" && !strings.HasSuffix(prefix, "/") {
		prefix += "/"
	}
	return pub.S3Location{Bucket: bucket, Prefix: prefix}, nil
}

func checkNoOverlap(src, dst pub.S3Location) error {
	if src.Bucket != dst.Bucket {
		return nil
	}
	if strings.HasPrefix(src.Prefix, dst.Prefix) || strings.HasPrefix(dst.Prefix, src.Prefix) {
		return pub.NewPermanent(fmt.Sprintf(
			"publish.Normalize: source and destination prefixes overlap in bucket %q (src=%q dst=%q)",
			src.Bucket, src.Prefix, dst.Prefix))
	}
	return nil
}

// parseS3URI extracts bucket and key from an HTTPS S3 URL.
// Expected format: https://<host>/<bucket>/<key-path>
func parseS3URI(uri string) (bucket, key string, err error) {
	u, parseErr := url.Parse(uri)
	if parseErr != nil || u.Scheme == "" || u.Host == "" {
		return "", "", pub.NewPermanent(fmt.Sprintf("parseS3URI: invalid URL %q", uri))
	}
	// Trim leading slash, split into bucket + key
	path := strings.TrimPrefix(u.Path, "/")
	slashIdx := strings.Index(path, "/")
	if slashIdx < 1 {
		return "", "", pub.NewPermanent(fmt.Sprintf("parseS3URI: no key in URL %q", uri))
	}
	bucket = path[:slashIdx]
	key = path[slashIdx+1:]
	if key == "" {
		return "", "", pub.NewPermanent(fmt.Sprintf("parseS3URI: empty key in URL %q", uri))
	}
	return bucket, key, nil
}
