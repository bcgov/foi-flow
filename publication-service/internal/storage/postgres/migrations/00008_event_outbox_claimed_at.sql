-- +goose Up
ALTER TABLE event_outbox ADD COLUMN claimed_at timestamptz NULL;

-- Replace the existing partial index with one that also excludes claimed rows,
-- so the UPDATE ... WHERE subquery hits the index.
DROP INDEX IF EXISTS event_outbox_unpublished_idx;
CREATE INDEX event_outbox_claimable_idx
    ON event_outbox (id)
    WHERE published_at IS NULL AND claimed_at IS NULL;

-- +goose Down
DROP INDEX IF EXISTS event_outbox_claimable_idx;
CREATE INDEX event_outbox_unpublished_idx
    ON event_outbox (id)
    WHERE published_at IS NULL;

ALTER TABLE event_outbox DROP COLUMN claimed_at;
