"""Add foiministryrequestid to FOIRequestApplicationFees

Revision ID: f7c3b1d2e9f4
Revises: 9aff8eac5dda
Create Date: 2026-06-25 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f7c3b1d2e9f4'
down_revision = '9aff8eac5dda'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('FOIRequestApplicationFees', sa.Column('ministryrequestid', sa.Integer(), nullable=True))


def downgrade():
    op.drop_column('FOIRequestApplicationFees', 'ministryrequestid')
