"""empty message

Revision ID: 01e12dbc3581
Revises: f994bce775b6
Create Date: 2023-04-21 13:57:25.524147

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '01e12dbc3581'
down_revision = 'f994bce775b6'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('Update public."ProgramAreas" set bcgovcode = \'HTH\' , iaocode=\'HTH\' where iaocode = \'HLTH\';')    
    op.execute('Update public."OperatingTeams" set name = \'HTH Ministry Team\' , description = \'HTH Ministry Team\' where name = \'HLTH Ministry Team\';')

def downgrade():
    op.execute('Update public."ProgramAreas" set bcgovcode = \'HLTH\' , iaocode=\'HLTH\' where iaocode = \'HTH\';')
    op.execute('Update public."OperatingTeams" set name = \'HLTH Ministry Team\' , description = \'HLTH Ministry Team\' where name = \'HTH Ministry Team\';')
