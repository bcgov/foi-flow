package publishcompletion

import (
	"fmt"
	"time"

	pub "publication-service/internal/publish"
	"publication-service/internal/sitemapping"
)

// errInvalidDate wraps the parse error as a permanent input error.
func errInvalidDate(raw string, cause error) error {
	return pub.NewPermanent(fmt.Sprintf("published_date must use YYYY-MM-DD: %q: %v", raw, cause))
}

func SitemapRequest(kind pub.Kind, tenantID, correlationID, sourceEventID string, result pub.PublishResult, publishedDate string) (sitemapping.Request, error) {
	lastModified, err := time.Parse("2006-01-02", publishedDate)
	if err != nil {
		return sitemapping.Request{}, errInvalidDate(publishedDate, err)
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
