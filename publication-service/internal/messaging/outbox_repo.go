package messaging

import (
	"context"
	"encoding/json"
	"fmt"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"

	pub "publication-service/internal/publish"
)

// OutboxRow is one outbound event awaiting publish.
type OutboxRow struct {
	ID        int64
	EventID   string
	EventType string
	TenantID  string
	Envelope  json.RawMessage
	Attempts  int
	Kind      pub.Kind // discriminates openinfo vs pd pipeline
}

// OutboxRepo wraps Postgres operations on event_outbox.
type OutboxRepo struct{ pool *pgxpool.Pool }

// NewOutboxRepo constructs an OutboxRepo around a pool.
func NewOutboxRepo(pool *pgxpool.Pool) *OutboxRepo { return &OutboxRepo{pool: pool} }

// Insert adds a new outbound event row.
func (r *OutboxRepo) Insert(ctx context.Context, row OutboxRow) error {
	const q = `
INSERT INTO event_outbox (event_id, event_type, tenant_id, envelope, kind)
VALUES ($1,$2,$3,$4,$5)`
	_, err := r.pool.Exec(ctx, q, row.EventID, row.EventType, row.TenantID, row.Envelope, string(row.Kind))
	if err != nil {
		return fmt.Errorf("outbox.Insert: %w", err)
	}
	return nil
}

// ClaimBatch reads up to limit unpublished rows with SKIP LOCKED.
func (r *OutboxRepo) ClaimBatch(ctx context.Context, limit int) ([]OutboxRow, error) {
	const q = `
SELECT id, event_id, event_type, tenant_id, envelope, attempts, kind
FROM event_outbox
WHERE published_at IS NULL
ORDER BY id
LIMIT $1
FOR UPDATE SKIP LOCKED`
	rows, err := r.pool.Query(ctx, q, limit)
	if err != nil {
		return nil, fmt.Errorf("outbox.ClaimBatch: %w", err)
	}
	defer rows.Close()
	var out []OutboxRow
	for rows.Next() {
		var row OutboxRow
		if err := rows.Scan(&row.ID, &row.EventID, &row.EventType, &row.TenantID, &row.Envelope, &row.Attempts, (*string)(&row.Kind)); err != nil {
			return nil, fmt.Errorf("outbox.ClaimBatch scan: %w", err)
		}
		out = append(out, row)
	}
	return out, rows.Err()
}

// MarkPublished sets published_at and increments attempts.
func (r *OutboxRepo) MarkPublished(ctx context.Context, id int64, now time.Time) error {
	const q = `UPDATE event_outbox SET published_at=$2, attempts=attempts+1 WHERE id=$1`
	_, err := r.pool.Exec(ctx, q, id, now)
	return err
}

// BumpAttempts records a failed publish without marking the row published.
func (r *OutboxRepo) BumpAttempts(ctx context.Context, id int64) error {
	const q = `UPDATE event_outbox SET attempts=attempts+1 WHERE id=$1`
	_, err := r.pool.Exec(ctx, q, id)
	return err
}
