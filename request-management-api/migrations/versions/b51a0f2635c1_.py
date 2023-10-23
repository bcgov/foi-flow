"""empty message

Revision ID: b51a0f2635c1
Revises: d43db71d53e5
Create Date: 2023-09-06 10:53:17.474765

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b51a0f2635c1'
down_revision = 'd43db71d53e5'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('FOIMinistryRequests', sa.Column('ministrysignoffapproval', sa.JSON(), nullable=True))


def downgrade():
    op.drop_column('FOIMinistryRequests', 'ministrysignoffapproval')
