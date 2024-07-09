"""ADD LOCKRECORDS Column to FOIMinistryRequest

Revision ID: 5fdd5df3d642
Revises: e698b39da6bd
Create Date: 2024-07-09 13:18:22.022002

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '5fdd5df3d642'
down_revision = 'e698b39da6bd'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('FOIMinistryRequests', sa.Column('lockrecords', sa.Boolean(), nullable=True))


def downgrade():
    op.drop_column('FOIMinistryRequests', 'lockrecords')
