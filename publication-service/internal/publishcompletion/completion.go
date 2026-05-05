package publishcompletion

import (
	"encoding/json"

	pub "publication-service/internal/publish"
	"publication-service/internal/sitemapping"
)

type Payload struct {
	TenantID             string `json:"tenant_id"`
	RequestEventID       string `json:"request_event_id"`
	CorrelationID        string `json:"correlation_id"`
	PublicationID        string `json:"publication_id"`
	PublicURL            string `json:"public_url"`
	HTMLKey              string `json:"html_key"`
	SitemapIndexKey      string `json:"sitemap_index_key"`
	SitemapPageKey       string `json:"sitemap_page_key"`
	SitemapPageURL       string `json:"sitemap_page_url"`
	SitemapResult        string `json:"sitemap_result"`
	SitemapIndexUpdated  bool   `json:"sitemap_index_updated"`
	FOIMinistryRequestID *int   `json:"foiministryrequest_id,omitempty"`
	FOIRequestID         *int   `json:"foirequest_id,omitempty"`
}

func BuildPayload(tenantID, requestEventID, correlationID string, foiMinistryRequestID, foiRequestID *int, publishResult pub.PublishResult, sitemapResult sitemapping.Result) ([]byte, error) {
	return json.Marshal(Payload{
		TenantID:             tenantID,
		RequestEventID:       requestEventID,
		CorrelationID:        correlationID,
		PublicationID:        publishResult.PublicationID,
		PublicURL:            publishResult.PublicURL,
		HTMLKey:              publishResult.HTMLKey,
		SitemapIndexKey:      sitemapResult.SitemapIndexKey,
		SitemapPageKey:       sitemapResult.SitemapPageKey,
		SitemapPageURL:       sitemapResult.SitemapPageURL,
		SitemapResult:        string(sitemapResult.Status),
		SitemapIndexUpdated:  sitemapResult.IndexUpdated,
		FOIMinistryRequestID: foiMinistryRequestID,
		FOIRequestID:         foiRequestID,
	})
}
