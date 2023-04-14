"""empty message

Revision ID: 08143691b340
Revises: b1ae2497530c
Create Date: 2022-12-19 15:54:32.701667

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '08143691b340'
down_revision = 'b1ae2497530c'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('FOIRequestRecords', sa.Column('isactive', sa.Boolean, nullable=False, server_default="true"))


def downgrade():
    op.drop_column('FOIRequestRecords', 'isactive')
