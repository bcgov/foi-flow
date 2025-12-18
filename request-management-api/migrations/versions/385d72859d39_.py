"""empty message

Revision ID: 385d72859d39
Revises: ce5a31546d60
Create Date: 2021-08-05 12:46:10.853195

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '385d72859d39'
down_revision = 'ce5a31546d60'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('FOIRawRequests', sa.Column('sourceofsubmission', sa.String(length=120), nullable=True))


def downgrade():
    op.drop_column('FOIRawRequests', 'sourceofsubmission')
