"""merge heads 3a4f7b2c6d9e and cfe019598f8b

Revision ID: 8f16afbd3bae
Revises: 3a4f7b2c6d9e, cfe019598f8b
Create Date: 2025-12-10 07:06:28.887482

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8f16afbd3bae'
down_revision = ('3a4f7b2c6d9e', 'cfe019598f8b')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
