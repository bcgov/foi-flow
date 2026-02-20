"""Add other_notes column to FOIRequestApplicants

Revision ID: 786d5b509254
Revises: 05dee3d60a8c
Create Date: 2026-01-23 10:40:56.152119

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '786d5b509254'
down_revision = '05dee3d60a8c'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('FOIRequestApplicants', sa.Column('other_notes', sa.Text(), nullable=True))

def downgrade():
    op.drop_column('FOIRequestApplicants', 'other_notes')