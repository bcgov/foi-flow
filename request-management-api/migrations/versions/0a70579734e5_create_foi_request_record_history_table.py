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
    op.create_table(
        'FOIRequestRecordHistory',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),

        # original PK components
        sa.Column('recordid', sa.Integer(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),

        # full record schema
        sa.Column('foirequestid', sa.Integer(), nullable=False),
        sa.Column('ministryrequestid', sa.Integer(), nullable=True),
        sa.Column('ministryrequestversion', sa.Integer(), nullable=True),
        sa.Column('filename', sa.Text(), nullable=True),
        sa.Column('s3uripath', sa.Text(), nullable=True),
        sa.Column('attributes', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('createdby', sa.String(length=120), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('updatedby', sa.String(length=120), nullable=True),
        sa.Column('isactive', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('replacementof', sa.Integer(), nullable=True),

        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('recordid', 'version', name='uq_foirequestrecordhist_recordid_version')
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


def downgrade():
    op.drop_table('FOIRequestRecordHistory')