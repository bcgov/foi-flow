package unpublish

import (
	"context"
	"time"

	pub "publication-service/internal/publish"
	"publication-service/internal/sitemapping"
)

type PublicRepositoryLocation struct {
	Bucket string
	Prefix string
}

type Request struct {
	Kind             pub.Kind
	TenantID         string
	PublicationID    string
	PublicURL        string
	PublicRepository PublicRepositoryLocation
	LastModified         time.Time
	SourceEventID        string
	CorrelationID        string
	FOIMinistryRequestID *int
	FOIRequestID         *int
}

type Result struct {
	Kind                   pub.Kind  `json:"kind"`
	TenantID               string    `json:"tenant_id"`
	PublicationID          string    `json:"publication_id"`
	PublicURL              string    `json:"public_url"`
	PublicRepositoryBucket string    `json:"public_repository_bucket"`
	PublicRepositoryPrefix string    `json:"public_repository_prefix"`
	ObjectsDeleted         int       `json:"objects_deleted"`
	SitemapIndexKey        string    `json:"sitemap_index_key"`
	SitemapPageKey         string    `json:"sitemap_page_key,omitempty"`
	SitemapResult          string    `json:"sitemap_result"`
	CompletedAt            time.Time `json:"completed_at"`
}

type PublicRepository interface {
	DeletePrefix(ctx context.Context, bucket, prefix string) (int, error)
}

type SitemapRemover interface {
	Remove(ctx context.Context, req sitemapping.RemovalRequest) (sitemapping.RemovalResult, error)
}

type ResultStore interface {
	FindCompleted(ctx context.Context, kind pub.Kind, publicationID string) (Result, bool, error)
	MarkSucceeded(ctx context.Context, eventID string, result Result) error
}
