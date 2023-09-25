""" Adding specifictopersonalrequests boolean column to distinguish between section/dvisions for personal vs general requests

Revision ID: 0ab7d9683c9a
Revises: 7341bc012ca9
Create Date: 2023-08-30 15:59:55.514768

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0ab7d9683c9a'
down_revision = '7341bc012ca9'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('ProgramAreaDivisions', sa.Column('specifictopersonalrequests', sa.Boolean, nullable=True))


def downgrade():
     op.drop_column('ProgramAreaDivisions', 'specifictopersonalrequests')
