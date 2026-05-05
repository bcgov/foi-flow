package publishcompletion

import (
	"fmt"
	"time"

	pub "publication-service/internal/publish"
	"publication-service/internal/sitemapping"
)

func SitemapRequest(kind pub.Kind, tenantID, correlationID, sourceEventID string, result pub.PublishResult, publishedDate string) (sitemapping.Request, error) {
	lastModified, err := time.Parse("2006-01-02", publishedDate)
	if err != nil {
		return sitemapping.Request{}, fmt.Errorf("published_date must use YYYY-MM-DD: %w", err)
	}
	return sitemapping.Request{
		Kind:                 kind,
		TenantID:             tenantID,
		PublicationID:        result.PublicationID,
		PublicURL:            result.PublicURL,
		LastModified:         lastModified,
		PublicationResultRef: result.HTMLKey,
		SourceEventID:        sourceEventID,
		CorrelationID:        correlationID,
	}, nil
}
