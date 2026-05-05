-- +goose Up
DROP TABLE publish_request;

CREATE TABLE workflow_request (
    event_id            uuid        PRIMARY KEY,
    event_type          text        NOT NULL,
    tenant_id           uuid        NOT NULL,
    correlation_id      text        NOT NULL,
    schema_version      text        NOT NULL,
    payload             jsonb       NOT NULL,
    kind                text        NOT NULL,
    state               text        NOT NULL,
    retry_count         int         NOT NULL DEFAULT 0,
    next_retry_at       timestamptz NULL,
    last_error          text        NULL,
    last_error_class    text        NULL,
    error_hash          text        NULL,
    error_hash_repeat   int         NOT NULL DEFAULT 0,
    result              jsonb       NULL,
    first_seen_at       timestamptz NOT NULL,
    last_attempt_at     timestamptz NULL,
    completed_at        timestamptz NULL,
    CONSTRAINT workflow_request_state_chk
        CHECK (state IN ('pending','processing','pending_retry','completed','dead')),
    CONSTRAINT workflow_request_kind_chk
        CHECK (kind IN ('openinfo','pd','openinfo_sitemap','pd_sitemap'))
);

CREATE UNIQUE INDEX workflow_request_tenant_correlation_uq
    ON workflow_request (tenant_id, correlation_id);

CREATE INDEX workflow_request_due_idx
    ON workflow_request (state, next_retry_at)
    WHERE state = 'pending_retry';

CREATE INDEX workflow_request_tenant_state_idx
    ON workflow_request (tenant_id, state);

CREATE INDEX workflow_request_kind_state_idx
    ON workflow_request (kind, state);

CREATE INDEX workflow_request_processing_idx
    ON workflow_request (last_attempt_at)
    WHERE state = 'processing';

ALTER TABLE event_outbox DROP CONSTRAINT event_outbox_kind_chk;
ALTER TABLE event_outbox
    ADD CONSTRAINT event_outbox_kind_chk
    CHECK (kind IN ('openinfo','pd','openinfo_sitemap','pd_sitemap'));

CREATE UNIQUE INDEX workflow_request_sitemap_publication_uq
    ON workflow_request (kind, (payload->>'publication_id'))
    WHERE kind IN ('openinfo_sitemap','pd_sitemap');

CREATE UNIQUE INDEX workflow_request_sitemap_public_url_uq
    ON workflow_request (kind, (payload->>'public_url'))
    WHERE kind IN ('openinfo_sitemap','pd_sitemap');

-- +goose Down
DROP INDEX workflow_request_sitemap_public_url_uq;
DROP INDEX workflow_request_sitemap_publication_uq;
DROP INDEX workflow_request_processing_idx;
DROP INDEX workflow_request_kind_state_idx;
DROP INDEX workflow_request_tenant_state_idx;
DROP INDEX workflow_request_due_idx;
DROP INDEX workflow_request_tenant_correlation_uq;

ALTER TABLE event_outbox DROP CONSTRAINT event_outbox_kind_chk;
ALTER TABLE event_outbox
    ADD CONSTRAINT event_outbox_kind_chk
    CHECK (kind IN ('openinfo','pd'));

DROP TABLE workflow_request;

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
    kind                text        NOT NULL,
    CONSTRAINT publish_request_state_chk
        CHECK (state IN ('pending','processing','pending_retry','completed','dead')),
    CONSTRAINT publish_request_kind_chk
        CHECK (kind IN ('openinfo','pd'))
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

CREATE INDEX publish_request_kind_state_idx
    ON publish_request (kind, state);
