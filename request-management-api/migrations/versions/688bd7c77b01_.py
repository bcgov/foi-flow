"""empty message

Revision ID: 688bd7c77b01
Revises: 6523dfc49ad0
Create Date: 2022-04-01 14:13:45.626252

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '688bd7c77b01'
down_revision = 'e8bf3ced66ab'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('FOIMinistryRequestDivisions', sa.Column('divisionduedate', sa.DateTime(), nullable=True))
    op.add_column('FOIMinistryRequestDivisions', sa.Column('eapproval', sa.String(length=12), nullable=True))


def downgrade():
    op.drop_column('FOIMinistryRequestDivisions', 'divisionduedate')
    op.drop_column('FOIMinistryRequestDivisions', 'eapproval')
