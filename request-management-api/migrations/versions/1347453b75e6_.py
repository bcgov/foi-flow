"""empty message

Revision ID: 1347453b75e6
Revises: e3839ed176e5
Create Date: 2021-11-10 15:10:53.897654

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1347453b75e6'
down_revision = 'e3839ed176e5'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('FOIMinistryRequestDocuments', sa.Column('version', sa.Integer, nullable=True))


def downgrade():
    op.drop_column('FOIMinistryRequestDocuments', 'version')
