-- +goose Up
CREATE TABLE event_outbox (
    id            bigserial   PRIMARY KEY,
    event_id      uuid        NOT NULL UNIQUE,
    event_type    text        NOT NULL,
    tenant_id     uuid        NOT NULL,
    envelope      jsonb       NOT NULL,
    published_at  timestamptz NULL,
    attempts      int         NOT NULL DEFAULT 0,
    created_at    timestamptz NOT NULL DEFAULT NOW()
);

CREATE INDEX event_outbox_unpublished_idx
    ON event_outbox (id)
    WHERE published_at IS NULL;

-- +goose Down
DROP TABLE event_outbox;
