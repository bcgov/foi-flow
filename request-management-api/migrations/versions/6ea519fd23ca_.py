"""empty message

Revision ID: 6ea519fd23ca
Revises: e3fc2c864677
Create Date: 2021-12-13 18:10:24.149748

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '6ea519fd23ca'
down_revision = '7475fca04f69'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('FOIRequestComments', sa.Column('taggedusers', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.add_column('FOIRawRequestComments', sa.Column('taggedusers', postgresql.JSON(astext_type=sa.Text()), nullable=True))

def downgrade():
    op.drop_column('FOIRequestComments', 'taggedusers')
    op.drop_column('FOIRawRequestComments', 'taggedusers')
