package publish

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"time"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgconn"
	"github.com/jackc/pgx/v5/pgxpool"
)

// Repo wraps Postgres operations on the workflow_request table.
type Repo struct{ pool *pgxpool.Pool }

// NewRepo constructs a Repo around a pgxpool.
func NewRepo(pool *pgxpool.Pool) *Repo { return &Repo{pool: pool} }

// ClaimRequest carries the inputs for an idempotent claim.
type ClaimRequest struct {
	EventID       string
	EventType     string
	TenantID      string
	CorrelationID string
	SchemaVersion string
	Payload       json.RawMessage
	Now           time.Time
	Kind          Kind // pipeline discriminator
}

// ClaimResult tells the caller whether this consumer won the row.
type ClaimResult struct {
	EventID string
	Won     bool
}

// Claim runs the dedup-and-claim INSERT…ON CONFLICT for one envelope.
func (r *Repo) Claim(ctx context.Context, req ClaimRequest) (ClaimResult, error) {
	if req.Kind == KindUnknown {
		return ClaimResult{}, fmt.Errorf("publish.Repo.Claim: Kind must be set")
	}
	const q = `
INSERT INTO workflow_request (
    event_id, tenant_id, correlation_id, schema_version, payload,
    state, retry_count, first_seen_at, last_attempt_at, kind, event_type
) VALUES ($1,$2,$3,$4,$5,'processing',0,$6,$6,$7,$8)
ON CONFLICT (event_id) DO UPDATE
    SET state = 'processing',
        last_attempt_at = EXCLUDED.last_attempt_at
    WHERE workflow_request.state IN ('pending','pending_retry')
RETURNING event_id`
	var id string
	err := r.pool.QueryRow(ctx, q,
		req.EventID, req.TenantID, req.CorrelationID, req.SchemaVersion, req.Payload, req.Now, string(req.Kind), req.EventType,
	).Scan(&id)
	switch {
	case err == nil:
		return ClaimResult{EventID: id, Won: true}, nil
	case errors.Is(err, pgx.ErrNoRows):
		return ClaimResult{EventID: req.EventID, Won: false}, nil
	}
	return ClaimResult{}, err
}

// MarkCompleted transitions a claimed row to state='completed'.
func (r *Repo) MarkCompleted(ctx context.Context, eventID string, now time.Time) error {
	const q = `
UPDATE workflow_request
SET state='completed', completed_at=$2,
    last_error=NULL, last_error_class=NULL,
    error_hash=NULL, error_hash_repeat=0
WHERE event_id=$1`
	tag, err := r.pool.Exec(ctx, q, eventID, now)
	if err != nil {
		return fmt.Errorf("publish.Repo.MarkCompleted: %w", err)
	}
	if tag.RowsAffected() != 1 {
		return fmt.Errorf("publish.Repo.MarkCompleted: %s not found", eventID)
	}
	return nil
}

// MarkRetry transitions a claimed row back to pending_retry with backoff, or
// to dead when retry policy has been exhausted.
func (r *Repo) MarkRetry(
	ctx context.Context,
	eventID string,
	msg string,
	hash string,
	nextAt time.Time,
	maxRetries int,
	poisonRepeatThreshold int,
) (RetryResult, error) {
	const q = `
WITH next_values AS (
    SELECT
        event_id,
        retry_count + 1 AS next_retry_count,
        CASE WHEN error_hash=$4 THEN error_hash_repeat + 1 ELSE 1 END AS next_error_hash_repeat
    FROM workflow_request
    WHERE event_id=$1
),
decision AS (
    SELECT
        event_id,
        next_retry_count,
        next_error_hash_repeat,
        CASE
            WHEN $5 > 0 AND next_retry_count >= $5 THEN 'dead'
            WHEN $6 > 0 AND next_error_hash_repeat >= $6 THEN 'dead'
            ELSE 'pending_retry'
        END AS next_state,
        CASE
            WHEN $6 > 0 AND next_error_hash_repeat >= $6 THEN 'poison'
            ELSE 'transient'
        END AS next_error_class
    FROM next_values
)
UPDATE workflow_request
SET state=decision.next_state,
    retry_count=decision.next_retry_count,
    next_retry_at=CASE WHEN decision.next_state='dead' THEN NULL ELSE $2 END,
    last_error=$3,
    last_error_class=decision.next_error_class,
    error_hash_repeat=decision.next_error_hash_repeat,
    error_hash=$4
FROM decision
WHERE workflow_request.event_id=decision.event_id
RETURNING workflow_request.state, workflow_request.last_error_class`
	var state State
	var class Class
	err := r.pool.QueryRow(ctx, q, eventID, nextAt, msg, hash, maxRetries, poisonRepeatThreshold).Scan(&state, &class)
	if err != nil {
		return RetryResult{}, err
	}
	return RetryResult{Dead: state == StateDead, Class: class}, nil
}

// MarkDead transitions a row to dead and redacts the payload.
func (r *Repo) MarkDead(ctx context.Context, eventID string, msg string, class Class) error {
	const q = `
UPDATE workflow_request
SET state='dead',
    last_error=$2,
    last_error_class=$3,
    payload='{}'::jsonb
WHERE event_id=$1`
	_, err := r.pool.Exec(ctx, q, eventID, msg, string(class))
	return err
}

// IsDuplicate reports whether err is a unique-violation on a business key.
func IsDuplicate(err error) bool {
	var pg *pgconn.PgError
	return errors.As(err, &pg) && pg.Code == "23505"
}

// DueRow is a row the scheduler needs to re-enqueue.
type DueRow struct {
	EventID       string
	EventType     string
	TenantID      string
	CorrelationID string
	SchemaVersion string
	Payload       json.RawMessage
	RetryCount    int
	Kind          Kind // pipeline discriminator
}

// ClaimDue atomically transitions due pending_retry rows to pending and returns them.
func (r *Repo) ClaimDue(ctx context.Context, limit int, now time.Time) ([]DueRow, error) {
	const q = `
WITH cte AS (
    SELECT event_id
    FROM workflow_request
    WHERE state = 'pending_retry' AND next_retry_at <= $2
    ORDER BY next_retry_at
    FOR UPDATE SKIP LOCKED
    LIMIT $1
)
UPDATE workflow_request p
SET state='pending', next_retry_at=NULL
FROM cte
WHERE p.event_id = cte.event_id
RETURNING p.event_id, p.tenant_id, p.correlation_id, p.schema_version, p.payload, p.retry_count, p.kind, p.event_type`
	rows, err := r.pool.Query(ctx, q, limit, now)
	if err != nil {
		return nil, fmt.Errorf("publish.Repo.ClaimDue: %w", err)
	}
	defer rows.Close()
	var out []DueRow
	for rows.Next() {
		var d DueRow
		if err := rows.Scan(&d.EventID, &d.TenantID, &d.CorrelationID, &d.SchemaVersion, &d.Payload, &d.RetryCount, (*string)(&d.Kind), &d.EventType); err != nil {
			return nil, fmt.Errorf("publish.Repo.ClaimDue: scan: %w", err)
		}
		out = append(out, d)
	}
	return out, rows.Err()
}

// ResetStuck moves rows that have been 'processing' too long back to pending_retry.
func (r *Repo) ResetStuck(ctx context.Context, threshold time.Time) (int64, error) {
	const q = `
UPDATE workflow_request
SET state='pending_retry', next_retry_at=NOW()
WHERE state='processing' AND last_attempt_at < $1`
	tag, err := r.pool.Exec(ctx, q, threshold)
	if err != nil {
		return 0, fmt.Errorf("publish.Repo.ResetStuck: %w", err)
	}
	return tag.RowsAffected(), nil
}
