"""empty message

Revision ID: 9638286dc851
Revises: bd20ff56d1b1
Create Date: 2022-12-19 15:54:32.701667

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9638286dc851'
down_revision = 'bd20ff56d1b1'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('FOIMinistryRequests', sa.Column('estimatedpagecount', sa.Integer, nullable=True, server_default=0))
    op.add_column('FOIMinistryRequests', sa.Column('estimatedtaggedpagecount', sa.Integer, nullable=True, server_default=0))


def downgrade():
    op.drop_column('FOIMinistryRequests', 'estimatedpagecount')
    op.drop_column('FOIMinistryRequests', 'estimatedtaggedpagecount')
