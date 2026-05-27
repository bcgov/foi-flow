package workflowresult

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

type CompletedAt[R any] struct {
	Get func(*R) time.Time
	Set func(*R, time.Time)
}

type Repo[R any] struct {
	pool        *pgxpool.Pool
	name        string
	completedAt CompletedAt[R]
}

func NewRepo[R any](pool *pgxpool.Pool, name string, completedAt CompletedAt[R]) *Repo[R] {
	return &Repo[R]{pool: pool, name: name, completedAt: completedAt}
}

func (r *Repo[R]) FindCompleted(ctx context.Context, kind pub.Kind, tenantID string, correlationID string) (R, bool, error) {
	const q = `
SELECT result
FROM workflow_request
WHERE state='completed'
  AND kind=$1
  AND tenant_id=$2
  AND correlation_id=$3
  AND result IS NOT NULL
ORDER BY completed_at DESC NULLS LAST
LIMIT 1`
	var zero R
	var raw []byte
	err := r.pool.QueryRow(ctx, q, string(kind), tenantID, correlationID).Scan(&raw)
	if errors.Is(err, pgx.ErrNoRows) {
		return zero, false, nil
	}
	if err != nil {
		return zero, false, fmt.Errorf("%s.FindCompleted: %w", r.name, err)
	}
	var result R
	if err := json.Unmarshal(raw, &result); err != nil {
		return zero, false, fmt.Errorf("%s.FindCompleted: unmarshal result: %w", r.name, err)
	}
	return result, true, nil
}

func (r *Repo[R]) MarkSucceeded(ctx context.Context, eventID string, result R) error {
	completedAt := r.completedAt.Get(&result)
	if completedAt.IsZero() {
		completedAt = time.Now().UTC()
		r.completedAt.Set(&result, completedAt)
	}
	raw, err := json.Marshal(result)
	if err != nil {
		return fmt.Errorf("%s.MarkSucceeded: marshal result: %w", r.name, err)
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
		return fmt.Errorf("%s.MarkSucceeded: %w", r.name, err)
	}
	if tag.RowsAffected() != 1 {
		return fmt.Errorf("%s.MarkSucceeded: %s not found", r.name, eventID)
	}
	return nil
}
