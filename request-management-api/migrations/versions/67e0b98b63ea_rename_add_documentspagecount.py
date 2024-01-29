"""empty message

Revision ID: 67e0b98b63ea
Revises: b4da31675bd0
Create Date: 2024-01-29 13:56:24.154203

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '67e0b98b63ea'
down_revision = 'b4da31675bd0'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('ALTER TABLE public."FOIMinistryRequests" RENAME COLUMN requestpagecount TO axispagecount;')
    op.add_column('FOIMinistryRequests', sa.Column('documentspagecount', sa.String(length=20), nullable=True))


def downgrade():
    op.execute('ALTER TABLE public."FOIMinistryRequests" RENAME COLUMN axispagecount TO requestpagecount;')
    op.drop_column('FOIMinistryRequests', 'documentspagecount')
