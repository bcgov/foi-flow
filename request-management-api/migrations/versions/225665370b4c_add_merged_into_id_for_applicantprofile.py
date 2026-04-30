"""Add merged_into_id for applicantprofile

Revision ID: 225665370b4c
Revises: 4ac689489532
Create Date: 2026-04-27 10:58:41.166509

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '225665370b4c'
down_revision = '4ac689489532'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('FOIRequestApplicants', sa.Column('merged_into_id', sa.VARCHAR(120), nullable=True))


def downgrade():
    op.drop_column('FOIRequestApplicants', 'merged_into_id')
