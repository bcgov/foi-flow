"""empty message

Revision ID: b9411d30daac
Revises: 10daedc23a0d
Create Date: 2022-12-08 16:15:34.115618

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b9411d30daac'
down_revision = '10daedc23a0d'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('FOIRawRequests', sa.Column('isiaorestricted', sa.Boolean, unique=False, nullable=True, default=False))


def downgrade():
    op.drop_column('FOIRawRequests', 'isiaorestricted')
