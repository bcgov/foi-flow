-- +goose Up
ALTER TABLE workflow_request DROP CONSTRAINT workflow_request_kind_chk;
ALTER TABLE workflow_request
    ADD CONSTRAINT workflow_request_kind_chk
    CHECK (kind IN ('openinfo','pd','openinfo_sitemap','pd_sitemap','openinfo_unpublish','pd_unpublish'));

ALTER TABLE event_outbox DROP CONSTRAINT event_outbox_kind_chk;
ALTER TABLE event_outbox
    ADD CONSTRAINT event_outbox_kind_chk
    CHECK (kind IN ('openinfo','pd','openinfo_sitemap','pd_sitemap','openinfo_unpublish','pd_unpublish'));

-- +goose Down
ALTER TABLE event_outbox DROP CONSTRAINT event_outbox_kind_chk;
ALTER TABLE event_outbox
    ADD CONSTRAINT event_outbox_kind_chk
    CHECK (kind IN ('openinfo','pd','openinfo_sitemap','pd_sitemap'));

ALTER TABLE workflow_request DROP CONSTRAINT workflow_request_kind_chk;
ALTER TABLE workflow_request
    ADD CONSTRAINT workflow_request_kind_chk
    CHECK (kind IN ('openinfo','pd','openinfo_sitemap','pd_sitemap'));
