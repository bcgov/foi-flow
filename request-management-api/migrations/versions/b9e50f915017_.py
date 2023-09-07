"""empty message

Revision ID: b9e50f915017
Revises: 01e12dbc3581
Create Date: 2023-04-21 15:24:08.259830

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b9e50f915017'
down_revision = '01e12dbc3581'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('UPDATE public."FOIMinistryRequests" SET  assignedministrygroup=\'HTH Ministry Team\' WHERE assignedministrygroup=\'HLTH Ministry Team\';commit;')  


def downgrade():
    op.execute('UPDATE public."FOIMinistryRequests" SET  assignedministrygroup=\'HLTH Ministry Team\' WHERE assignedministrygroup=\'HTH Ministry Team\';commit;')
