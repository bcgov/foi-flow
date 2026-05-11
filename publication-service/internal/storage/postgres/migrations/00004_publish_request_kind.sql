-- +goose Up
ALTER TABLE publish_request
    ADD COLUMN kind text NOT NULL DEFAULT 'openinfo';

ALTER TABLE publish_request
    ADD CONSTRAINT publish_request_kind_chk
    CHECK (kind IN ('openinfo','pd'));

-- Drop default so producer code is forced to set kind explicitly.
ALTER TABLE publish_request
    ALTER COLUMN kind DROP DEFAULT;

CREATE INDEX publish_request_kind_state_idx
    ON publish_request (kind, state);

-- +goose Down
DROP INDEX publish_request_kind_state_idx;
ALTER TABLE publish_request DROP CONSTRAINT publish_request_kind_chk;
ALTER TABLE publish_request DROP COLUMN kind;
