"""your next change

Revision ID: 2d8cf3fb689f
Revises: bd62026741e2
Create Date: 2025-11-24 15:35:25.038358

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2d8cf3fb689f'
down_revision = 'bd62026741e2'
branch_labels = None
depends_on = None



def upgrade():
    # --- Parent/group entity table ---
    op.create_table(
        'FOIRequestRecordGroup',
        sa.Column('document_set_id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('ministry_request_id', sa.Integer(), nullable=False),
        sa.Column('request_id', sa.Integer(), nullable=False),

        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),

        sa.Column('created_by', sa.String(length=120), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('updated_by', sa.String(length=120), nullable=True),
    )

    # Index on ministry_request_id
    op.create_index(
        op.f('ix_FOIRequestRecordGroup_ministry_request_id'),
        'FOIRequestRecordGroup',
        ['ministry_request_id'],
        unique=False,
    )

    # --- Association table (many-to-many) ---
    op.create_table(
        'FOIRequestRecordGroups',
        sa.Column('document_set_id', sa.Integer(), nullable=False),
        sa.Column('record_id', sa.Integer(), nullable=False),

        sa.ForeignKeyConstraint(
            ['document_set_id'],
            ['FOIRequestRecordGroup.document_set_id'],
            name='fk_groups_setid',
            ondelete='CASCADE',
        ),
        sa.ForeignKeyConstraint(
            ['record_id'],
            ['FOIRequestRecords.recordid'],
            name='fk_groups_record_id',
            ondelete='CASCADE',
        ),

        # PK no longer includes version
        sa.PrimaryKeyConstraint(
            'document_set_id', 'record_id',
            name='pk_groups'
        ),
    )

    # Indexes
    op.create_index(
        op.f('ix_FOIRequestRecordGroups_document_set_id'),
        'FOIRequestRecordGroups',
        ['document_set_id'],
        unique=False,
    )
    op.create_index(
        'ix_FOIRequestRecordGroups_record_id',
        'FOIRequestRecordGroups',
        ['record_id'],
        unique=False,
    )


def downgrade():
    # Drop association indexes + table
    op.drop_index('ix_FOIRequestRecordGroups_record_id', table_name='FOIRequestRecordGroups')
    op.drop_index(op.f('ix_FOIRequestRecordGroups_document_set_id'), table_name='FOIRequestRecordGroups')
    op.drop_table('FOIRequestRecordGroups')

    # Drop group table indexes + table
    op.drop_index(op.f('ix_FOIRequestRecordGroup_ministry_request_id'), table_name='FOIRequestRecordGroup')
    op.drop_table('FOIRequestRecordGroup')

