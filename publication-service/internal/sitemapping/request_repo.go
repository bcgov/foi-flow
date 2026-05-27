package sitemapping

import (
	"context"
	"encoding/json"
	"fmt"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"

	"publication-service/internal/workflowresult"
)

// RequestRepo stores sitemap-specific completion results in workflow_request.
type RequestRepo struct {
	*workflowresult.Repo[Result]
	pool *pgxpool.Pool
}

// NewRequestRepo constructs a RequestRepo around a pgxpool.
func NewRequestRepo(pool *pgxpool.Pool) *RequestRepo {
	return &RequestRepo{
		Repo: workflowresult.NewRepo[Result](
			pool,
			"sitemapping.RequestRepo",
			workflowresult.CompletedAt[Result]{Get: sitemapCompletedAt, Set: setSitemapCompletedAt},
		),
		pool: pool,
	}
}

func sitemapCompletedAt(result *Result) time.Time {
	return result.CompletedAt
}

func setSitemapCompletedAt(result *Result, completedAt time.Time) {
	result.CompletedAt = completedAt
}

func (r *RequestRepo) MarkSucceeded(ctx context.Context, eventID string, result Result) error {
	if result.CompletedAt.IsZero() {
		result.CompletedAt = time.Now().UTC()
	}
	raw, err := json.Marshal(result)
	if err != nil {
		return fmt.Errorf("sitemapping.RequestRepo.MarkSucceeded: marshal result: %w", err)
	}
	const q = `
WITH target AS (
    SELECT event_id
    FROM workflow_request
    WHERE event_id=$1
    UNION ALL
    SELECT event_id
    FROM workflow_request
    WHERE kind=$4
      AND tenant_id=$5
      AND payload->>'public_url'=$6
      AND NOT EXISTS (
          SELECT 1
          FROM workflow_request
          WHERE event_id=$1
      )
    LIMIT 1
)
UPDATE workflow_request
SET state='completed',
    completed_at=$2,
    last_error=NULL,
    last_error_class=NULL,
    error_hash=NULL,
    error_hash_repeat=0,
    result=$3
WHERE event_id=(SELECT event_id FROM target)`
	tag, err := r.pool.Exec(ctx, q, eventID, result.CompletedAt, raw, string(result.Kind), result.TenantID, result.PublicURL)
	if err != nil {
		return fmt.Errorf("sitemapping.RequestRepo.MarkSucceeded: %w", err)
	}
	if tag.RowsAffected() != 1 {
		return fmt.Errorf("sitemapping.RequestRepo.MarkSucceeded: %s not found", eventID)
	}
	return nil
}
