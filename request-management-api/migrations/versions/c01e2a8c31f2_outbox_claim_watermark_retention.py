"""outbox claim, ordering and retention columns

Moves the idempotency, ordering and error-mapping state that FOI Request Routing used to keep in
the n8n foi-process-audit Data Table into the FOIWorkflowEventOutbox table (no other table):
  - the claim lease (claimedat) and the execution that holds it (n8nexecutionid, existing column),
  - the request ids recorded at claim time,
  - stateoccurredat: the occurred_at of a state event once it was allowed to run. The newest value
    per raw request / ministry request is the ordering watermark,
  - a payload-scrub marker for retention.

Revision ID: c01e2a8c31f2
Revises: 1b34e2d861aa
Create Date: 2026-11-12 13:26:22.244391

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c01e2a8c31f2'
down_revision = '1b34e2d861aa'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        ALTER TABLE "FOIWorkflowEventOutbox"
            ADD COLUMN IF NOT EXISTS claimedat         TIMESTAMP,
            ADD COLUMN IF NOT EXISTS payloadscrubbedat TIMESTAMP,
            ADD COLUMN IF NOT EXISTS rawrequestid     VARCHAR(50),
            ADD COLUMN IF NOT EXISTS foirequestid     VARCHAR(50),
            ADD COLUMN IF NOT EXISTS ministryrequestid VARCHAR(50),
            ADD COLUMN IF NOT EXISTS requeststatus    VARCHAR(100),
            ADD COLUMN IF NOT EXISTS stateoccurredat  TIMESTAMP;
    """)
    # n8n failure handler: failed execution -> event
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_foiworkflowoutbox_n8nexecutionid
        ON "FOIWorkflowEventOutbox" (n8nexecutionid) WHERE n8nexecutionid IS NOT NULL;
    """)
    # ordering check: newest state event already allowed to run for a request
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_foiworkflowoutbox_rawrequestid_stateoccurredat
        ON "FOIWorkflowEventOutbox" (rawrequestid, stateoccurredat) WHERE rawrequestid IS NOT NULL;
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_foiworkflowoutbox_ministryrequestid_stateoccurredat
        ON "FOIWorkflowEventOutbox" (ministryrequestid, stateoccurredat) WHERE ministryrequestid IS NOT NULL;
    """)
    # find the events of one FOI request without scanning the JSON payload
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_foiworkflowoutbox_foirequestid
        ON "FOIWorkflowEventOutbox" (foirequestid) WHERE foirequestid IS NOT NULL;
    """)
    # retention: COMPLETED rows whose payload has not been scrubbed yet
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_foiworkflowoutbox_completed_unscrubbed
        ON "FOIWorkflowEventOutbox" (completedat) WHERE status = 'COMPLETED' AND payloadscrubbedat IS NULL;
    """)
    # retention: COMPLETED rows to delete
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_foiworkflowoutbox_completed
        ON "FOIWorkflowEventOutbox" (completedat) WHERE status = 'COMPLETED';
    """)


def downgrade():
    for index in ('ix_foiworkflowoutbox_completed', 'ix_foiworkflowoutbox_completed_unscrubbed',
                  'ix_foiworkflowoutbox_foirequestid', 'ix_foiworkflowoutbox_ministryrequestid_stateoccurredat',
                  'ix_foiworkflowoutbox_rawrequestid_stateoccurredat', 'ix_foiworkflowoutbox_n8nexecutionid'):
        op.execute('DROP INDEX IF EXISTS %s;' % index)
    op.execute("""
        ALTER TABLE "FOIWorkflowEventOutbox"
            DROP COLUMN IF EXISTS stateoccurredat,
            DROP COLUMN IF EXISTS requeststatus,
            DROP COLUMN IF EXISTS ministryrequestid,
            DROP COLUMN IF EXISTS foirequestid,
            DROP COLUMN IF EXISTS rawrequestid,
            DROP COLUMN IF EXISTS payloadscrubbedat,
            DROP COLUMN IF EXISTS claimedat;
    """)

