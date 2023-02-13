"""empty message

Revision ID: 5254ab336fec
Revises: c9d654c84d59
Create Date: 2022-06-22 17:25:19.091432

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '5254ab336fec'
down_revision = 'c9d654c84d59'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('FOIMinistryRequestDivisions', sa.Column('divisionreceiveddate', sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column('FOIMinistryRequestDivisions', 'divisionreceiveddate')
