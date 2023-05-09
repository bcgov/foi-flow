"""empty message

Revision ID: 3ef2a6dbf556
Revises: 93566cbde728
Create Date: 2023-05-09 10:32:01.796078

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3ef2a6dbf556'
down_revision = '93566cbde728'
branch_labels = None
depends_on = None


def upgrade():
     op.add_column('FOIRequestRecords', sa.Column('replacementof', sa.INTEGER, nullable=True))


def downgrade():
     op.drop_column('FOIRequestRecords', 'replacementof')
