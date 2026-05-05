package unpublish

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"time"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"

	pub "publication-service/internal/publish"
)

type RequestRepo struct {
	pool *pgxpool.Pool
}

func NewRequestRepo(pool *pgxpool.Pool) *RequestRepo {
	return &RequestRepo{pool: pool}
}

func (r *RequestRepo) FindCompleted(ctx context.Context, kind pub.Kind, publicationID string) (Result, bool, error) {
	const q = `
SELECT result
FROM workflow_request
WHERE state='completed'
  AND kind=$1
  AND payload->>'publication_id'=$2
  AND result IS NOT NULL
ORDER BY completed_at DESC NULLS LAST
LIMIT 1`
	var raw []byte
	err := r.pool.QueryRow(ctx, q, string(kind), publicationID).Scan(&raw)
	if errors.Is(err, pgx.ErrNoRows) {
		return Result{}, false, nil
	}
	if err != nil {
		return Result{}, false, fmt.Errorf("unpublish.RequestRepo.FindCompleted: %w", err)
	}
	var result Result
	if err := json.Unmarshal(raw, &result); err != nil {
		return Result{}, false, fmt.Errorf("unpublish.RequestRepo.FindCompleted: unmarshal result: %w", err)
	}
	return result, true, nil
}

func (r *RequestRepo) MarkSucceeded(ctx context.Context, eventID string, result Result) error {
	completedAt := result.CompletedAt
	if completedAt.IsZero() {
		completedAt = time.Now().UTC()
		result.CompletedAt = completedAt
	}
	raw, err := json.Marshal(result)
	if err != nil {
		return fmt.Errorf("unpublish.RequestRepo.MarkSucceeded: marshal result: %w", err)
	}
	const q = `
UPDATE workflow_request
SET state='completed',
    completed_at=$2,
    last_error=NULL,
    last_error_class=NULL,
    error_hash=NULL,
    error_hash_repeat=0,
    result=$3
WHERE event_id=$1`
	tag, err := r.pool.Exec(ctx, q, eventID, completedAt, raw)
	if err != nil {
		return fmt.Errorf("unpublish.RequestRepo.MarkSucceeded: %w", err)
	}
	if tag.RowsAffected() != 1 {
		return fmt.Errorf("unpublish.RequestRepo.MarkSucceeded: %s not found", eventID)
	}
	return nil
}
