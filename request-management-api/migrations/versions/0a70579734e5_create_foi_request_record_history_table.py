"""create FOIRequestRecordHistory table

Revision ID: 0a70579734e5
Revises: 7fe3c2636fbf
Create Date: 2025-11-19 14:33:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0a70579734e5'
down_revision = '05dee3d60a8c'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        CREATE TABLE IF NOT EXISTS "FOIRequestRecordHistory" (
        id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

        -- original PK components
        recordid INTEGER NOT NULL,
        version INTEGER NOT NULL,

        -- full record schema
        foirequestid INTEGER NOT NULL,
        ministryrequestid INTEGER,
        ministryrequestversion INTEGER,
        filename TEXT,
        s3uripath TEXT,
        attributes JSON,
        created_at TIMESTAMP,
        createdby VARCHAR(120),
        updated_at TIMESTAMP,
        updatedby VARCHAR(120),
        isactive BOOLEAN NOT NULL DEFAULT true,
        replacementof INTEGER,

        CONSTRAINT uq_foirequestrecordhist_recordid_version
            UNIQUE (recordid, version)
    );
    
    """
    )

    # NOTE:
    # This backfill step will be executed manually in each environment.
    # You may uncomment the block below to run it locally if needed.
    #
    # ----------------------------------------------------------
    #  Backfill history rules:
    #  - Skip recordids that only have a single version (version_count = 1)
    #  - For recordids with multiple versions, move all older versions
    #    and keep only the latest in FOIRequestRecords
    #
    # Examples:
    #    versions: [1]        → no history created
    #    versions: [1,2]      → move 1, keep 2
    #    versions: [1,2,3]    → move 1 and 2, keep 3
    #
    # ----------------------------------------------------------
    # op.execute("""
    #            INSERT INTO "FOIRequestRecordHistory"
    #            (recordid, version, foirequestid, ministryrequestid, ministryrequestversion,
    #             filename, s3uripath, attributes, created_at, createdby, updated_at, updatedby,
    #             isactive, replacementof)
    #            SELECT fr.recordid,
    #                   fr.version,
    #                   fr.foirequestid,
    #                   fr.ministryrequestid,
    #                   fr.ministryrequestversion,
    #                   fr.filename,
    #                   fr.s3uripath,
    #                   fr.attributes::json, fr.created_at,
    #                   fr.createdby,
    #                   fr.updated_at,
    #                   fr.updatedby,
    #                   fr.isactive,
    #                   fr.replacementof
    #            FROM "FOIRequestRecords" fr
    #                     JOIN (SELECT recordid,
    #                                  MAX(version) AS maxversion,
    #                                  COUNT(*)     AS version_count
    #                           FROM "FOIRequestRecords"
    #                           GROUP BY recordid) stats
    #                          ON stats.recordid = fr.recordid
    #            WHERE stats.version_count > 1
    #              AND fr.version < stats.maxversion;
    #            """)
    # ----------------------------------------------------------
    # After inserting old versions into FOIRequestRecordHistory,
    # remove ONLY the older rows from FOIRequestRecords:
    #
    # This ensures FOIRequestRecords contains only the latest version
    # for each recordid.
    #
    # ----------------------------------------------------------
    #
    # op.execute("""
    #   DELETE FROM "FOIRequestRecords" fr
    #   USING (
    #       SELECT recordid, MAX(version) AS maxversion
    #       FROM "FOIRequestRecords"
    #       GROUP BY recordid
    #   ) latest
    #   WHERE fr.recordid = latest.recordid
    #     AND fr.version < latest.maxversion;
    #            """)
    #
    # ----------------------------------------------------------
    # Once FOIRequestRecords contains only the latest rows,
    # update the table structure:
    #
    # ----------------------------------------------------------
    # op.execute("""
    #   ALTER TABLE "FOIRequestRecords"
    #   DROP CONSTRAINT "FOIRequestRecords_pkey";
    #
    #   ALTER TABLE "FOIRequestRecords"
    #   ADD PRIMARY KEY (recordid);
    #
    #            """)

    # ----------------------------------------------------------

    # op.execute(
    #     """
    #         CREATE INDEX IF NOT EXISTS  idx_frg_record_id
    #         ON "FOIRequestRecordGroups"(record_id);
    #
    #         CREATE INDEX IF NOT EXISTS  idx_frg_document_set_id
    #         ON "FOIRequestRecordGroups"(document_set_id);
    #
    #         CREATE INDEX IF NOT EXISTS  idx_records_active_mrid_foireqid
    #         ON "FOIRequestRecords"(isactive, ministryrequestid, foirequestid);
    #
    #     """
    # )


# def downgrade():
#     op.execute("""
#         DROP TABLE IF EXISTS "FOIRequestRecordHistory";
#     """)