"""empty message

Revision ID: c92673c110fe
Revises: 7959ccaa7f9d
Create Date: 2022-10-03 13:29:49.177590

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c92673c110fe'
down_revision = '7959ccaa7f9d'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('UPDATE public."FOIRequestTeams" set teamid = (select teamid from public."OperatingTeams" where name = \'Central Team\') where teamid = (select teamid from public."OperatingTeams" where name = \'Business Team\') and programareaid in (select programareaid from public."ProgramAreas" where iaocode in (\'JER\', \'LBR\', \'MMA\', \'TAC\', \'TIC\', \'TRA\'));')
    op.execute('UPDATE public."OperatingTeams" set isactive = false where name = \'Business Team\';')

def downgrade():    
    op.execute('UPDATE public."FOIRequestTeams" set teamid = (select teamid from public."OperatingTeams" where name = \'Business Team\') where teamid = (select teamid from public."OperatingTeams" where name = \'Central Team\') and programareaid in (select programareaid from public."ProgramAreas" where iaocode in (\'JER\', \'LBR\', \'MMA\', \'TA\', \'TIC\', \'TRA\'));')
    op.execute('UPDATE public."OperatingTeams" set isactive = true where name = \'Business Team\';')
    
