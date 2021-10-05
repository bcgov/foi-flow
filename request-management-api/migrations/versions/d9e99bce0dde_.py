"""empty message

Revision ID: d9e99bce0dde
Revises: 3acad8ceb8d8
Create Date: 2021-09-28 16:43:40.112449

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd9e99bce0dde'
down_revision = '3acad8ceb8d8'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('FOIMinistryRequests', sa.Column('cfrduedate', sa.DateTime, nullable=True))


def downgrade():
    op.drop_column('FOIMinistryRequests', 'cfrduedate')
