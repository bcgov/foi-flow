"""empty message

Revision ID: 6523dfc49ad0
Revises: e630f23aaaf9
Create Date: 2022-03-23 12:31:01.570943

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6523dfc49ad0'
down_revision = 'e630f23aaaf9'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('FOIMinistryRequests', sa.Column('requestpagecount', sa.String(length=20), nullable=True))


def downgrade():
    op.drop_column('FOIMinistryRequests', 'requestpagecount')
