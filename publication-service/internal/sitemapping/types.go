package sitemapping

import (
	"context"
	"errors"
	"time"

	pub "publication-service/internal/publish"
)

var ErrObjectNotFound = errors.New("sitemapping: object not found")

// Status is the durable outcome of a sitemap mapping attempt.
type Status string

const (
	StatusWritten        Status = "written"
	StatusAlreadyPresent Status = "already_present"
)

// RemovalStatus is the durable outcome of removing an unpublished URL.
type RemovalStatus string

const (
	RemovalStatusRemoved       RemovalStatus = "removed"
	RemovalStatusPageDeleted   RemovalStatus = "page_deleted"
	RemovalStatusAlreadyAbsent RemovalStatus = "already_absent"
)

type Target struct {
	Bucket          string
	Prefix          string
	PublicBaseURL   string
	IndexFileName   string
	PageFilePattern string
	PageLimit       int
}

type Request struct {
	Kind                 pub.Kind
	TenantID             string
	PublicationID        string
	PublicURL            string
	LastModified         time.Time
	PublicationResultRef string
	SourceEventID        string
	CorrelationID        string
	FOIMinistryRequestID *int
	FOIRequestID         *int
}

// Result is stored in workflow_request.result after a sitemap request succeeds.
type Result struct {
	Kind                 pub.Kind  `json:"kind"`
	TenantID             string    `json:"tenant_id"`
	PublicationID        string    `json:"publication_id"`
	PublicURL            string    `json:"public_url"`
	LastModified         time.Time `json:"last_modified"`
	SitemapIndexKey      string    `json:"sitemap_index_key"`
	SitemapPageKey       string    `json:"sitemap_page_key"`
	SitemapPageURL       string    `json:"sitemap_page_url"`
	Status               Status    `json:"result"`
	IndexUpdated         bool      `json:"index_updated"`
	PublicationResultRef string    `json:"publication_result_ref"`
	CompletedAt          time.Time `json:"completed_at"`
}

type RemovalRequest struct {
	Kind          pub.Kind
	TenantID      string
	PublicationID string
	PublicURL     string
	LastModified  time.Time
	SourceEventID string
	CorrelationID string
}

type RemovalResult struct {
	Kind            pub.Kind      `json:"kind"`
	TenantID        string        `json:"tenant_id"`
	PublicationID   string        `json:"publication_id"`
	PublicURL       string        `json:"public_url"`
	LastModified    time.Time     `json:"last_modified"`
	SitemapIndexKey string        `json:"sitemap_index_key"`
	SitemapPageKey  string        `json:"sitemap_page_key,omitempty"`
	SitemapPageURL  string        `json:"sitemap_page_url,omitempty"`
	Status          RemovalStatus `json:"result"`
	IndexUpdated    bool          `json:"index_updated"`
	CompletedAt     time.Time     `json:"completed_at"`
}

type ObjectStore interface {
	Get(ctx context.Context, bucket, key string) ([]byte, error)
	Upload(ctx context.Context, bucket, key string, body []byte, contentType string) error
	Delete(ctx context.Context, bucket, key string) error
}
