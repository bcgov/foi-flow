"""empty message

Revision ID: ea8dbc7b1ea0
Revises: b9411d30daac
Create Date: 2022-12-08 16:22:14.134901

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ea8dbc7b1ea0'
down_revision = 'b9411d30daac'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('FOIMinistryRequests', sa.Column('isiaorestricted', sa.Boolean, unique=False, nullable=True, default=False))


def downgrade():
    op.drop_column('FOIMinistryRequests', 'isiaorestricted')
