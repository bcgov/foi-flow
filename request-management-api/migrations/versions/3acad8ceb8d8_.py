"""empty message

Revision ID: 3acad8ceb8d8
Revises: bce04425c3b4
Create Date: 2021-09-22 16:09:23.533169

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3acad8ceb8d8'
down_revision = 'bce04425c3b4'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('FOIMinistryRequests', sa.Column('assignedministryperson', sa.String(length=120), nullable=True))
    op.add_column('FOIMinistryRequests', sa.Column('assignedministrygroup', sa.String(length=120), nullable=True))


def downgrade():
    op.drop_column('FOIMinistryRequests', 'assignedministryperson')
    op.drop_column('FOIMinistryRequests', 'assignedministrygroup')
