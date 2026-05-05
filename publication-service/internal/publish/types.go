// Package publish contains shared types for both the openinfo and
// proactivedisclosure publish pipelines.
package publish

// Kind discriminates which pipeline a row or outbox message belongs to.
type Kind string

const (
	KindUnknown                      Kind = "" // zero value sentinel — rejected by Repo.Claim
	KindOpenInfo                     Kind = "openinfo"
	KindProactiveDisclosure          Kind = "pd"
	KindOpenInfoSitemap              Kind = "openinfo_sitemap"
	KindProactiveDisclosureSitemap   Kind = "pd_sitemap"
	KindOpenInfoUnpublish            Kind = "openinfo_unpublish"
	KindProactiveDisclosureUnpublish Kind = "pd_unpublish"
)

// S3Location is a bucket + canonical prefix.
// Prefix is either empty (whole bucket) or ends in "/".
type S3Location struct {
	Bucket string
	Prefix string
}

// CopiedObject is the per-file summary of a single S3 copy operation.
type CopiedObject struct {
	Key  string
	Size int64
}

// CopyResult is the per-event summary returned by a Copier.
type CopyResult struct {
	ObjectsCopied int
	BytesCopied   int64
	Objects       []CopiedObject
}

// PublishResult describes the generated publication artifact.
type PublishResult struct {
	PublicationID string
	HTMLKey       string
	PublicURL     string
}
