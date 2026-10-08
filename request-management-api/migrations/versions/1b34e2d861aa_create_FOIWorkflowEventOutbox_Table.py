"""empty message

Revision ID: 1b34e2d861aa
Revises: 5a7ce876a293
Create Date: 2026-10-05 11:56:23.270277

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1b34e2d861aa'
down_revision = '5a7ce876a293'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        CREATE TABLE IF NOT EXISTS "FOIWorkflowEventOutbox" (
            outboxid        BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            eventid         VARCHAR(36)  NOT NULL,
            eventname       VARCHAR(100) NOT NULL,
            payload         JSONB        NOT NULL,
            status          VARCHAR(20)  NOT NULL DEFAULT 'PENDING',
            attempts        INTEGER      NOT NULL DEFAULT 0,
            nextattemptat   TIMESTAMP    NOT NULL DEFAULT (now() AT TIME ZONE 'utc'),
            lasterror       TEXT,
            n8nexecutionid  VARCHAR(100),
            replaycount     INTEGER      NOT NULL DEFAULT 0,
            deliveredat     TIMESTAMP,
            completedat     TIMESTAMP,
            created_at      TIMESTAMP    NOT NULL DEFAULT (now() AT TIME ZONE 'utc'),
            updated_at      TIMESTAMP    NOT NULL DEFAULT (now() AT TIME ZONE 'utc'),
            CONSTRAINT uq_foiworkflowoutbox_eventid UNIQUE (eventid),
            CONSTRAINT ck_foiworkflowoutbox_status
                CHECK (status IN ('PENDING', 'DELIVERED', 'COMPLETED', 'FAILED', 'DEAD'))
        );
    """)
    # dispatcher claim: due PENDING rows
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_foiworkflowoutbox_pending_due
        ON "FOIWorkflowEventOutbox" (nextattemptat, outboxid) WHERE status = 'PENDING';
    """)
    # sweeper: DELIVERED rows waiting for an outcome
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_foiworkflowoutbox_delivered
        ON "FOIWorkflowEventOutbox" (deliveredat) WHERE status = 'DELIVERED';
    """)
    # replay listing: DEAD / FAILED rows
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_foiworkflowoutbox_dead_failed
        ON "FOIWorkflowEventOutbox" (outboxid DESC) WHERE status IN ('DEAD', 'FAILED');
    """)


def downgrade():
    op.execute('DROP TABLE IF EXISTS "FOIWorkflowEventOutbox";')
