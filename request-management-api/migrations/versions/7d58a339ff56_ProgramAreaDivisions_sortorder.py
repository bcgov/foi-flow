"""empty message

Revision ID: 7d58a339ff56
Revises: e0b9df2555d2
Create Date: 2023-01-12 11:36:27.687775

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7d58a339ff56'
down_revision = 'e0b9df2555d2'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('ProgramAreaDivisions', sa.Column('sortorder', sa.INTEGER, nullable=True))
    


def downgrade():
    op.drop_column('ProgramAreaDivisions', 'sortorder')
