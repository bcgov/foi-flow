-- +goose Up
CREATE TABLE publish_request (
    event_id            uuid        PRIMARY KEY,
    tenant_id           uuid        NOT NULL,
    correlation_id      text        NOT NULL,
    schema_version      text        NOT NULL,
    payload             jsonb       NOT NULL,
    state               text        NOT NULL,
    retry_count         int         NOT NULL DEFAULT 0,
    next_retry_at       timestamptz NULL,
    last_error          text        NULL,
    last_error_class    text        NULL,
    error_hash          text        NULL,
    error_hash_repeat   int         NOT NULL DEFAULT 0,
    first_seen_at       timestamptz NOT NULL,
    last_attempt_at     timestamptz NULL,
    completed_at        timestamptz NULL,
    CONSTRAINT publish_request_state_chk
        CHECK (state IN ('pending','processing','pending_retry','completed','dead'))
);

CREATE INDEX publish_request_due_idx
    ON publish_request (state, next_retry_at)
    WHERE state = 'pending_retry';

CREATE INDEX publish_request_tenant_state_idx
    ON publish_request (tenant_id, state);

CREATE INDEX publish_request_processing_idx
    ON publish_request (last_attempt_at)
    WHERE state = 'processing';

CREATE UNIQUE INDEX publish_request_tenant_correlation_uq
    ON publish_request (tenant_id, correlation_id);

-- +goose Down
DROP TABLE publish_request;
