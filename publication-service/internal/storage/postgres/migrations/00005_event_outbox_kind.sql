-- +goose Up
ALTER TABLE event_outbox
    ADD COLUMN kind text NOT NULL DEFAULT 'openinfo';

ALTER TABLE event_outbox
    ADD CONSTRAINT event_outbox_kind_chk
    CHECK (kind IN ('openinfo','pd'));

ALTER TABLE event_outbox
    ALTER COLUMN kind DROP DEFAULT;

-- +goose Down
ALTER TABLE event_outbox DROP CONSTRAINT event_outbox_kind_chk;
ALTER TABLE event_outbox DROP COLUMN kind;
