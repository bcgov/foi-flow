"""empty message

Revision ID: 4bd9d39a052e
Revises: 46e5ecb5339e
Create Date: 2022-10-12 15:02:08.299241

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4bd9d39a052e'
down_revision = '46e5ecb5339e'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('UPDATE public."FOIRequestTeams" set teamid = (select teamid from public."OperatingTeams" where name = \'Central Team\') where teamid = (select teamid from public."OperatingTeams" where name = \'Business Team\') and programareaid in (select programareaid from public."ProgramAreas" where iaocode in (\'JER\', \'LBR\', \'MMA\', \'TAC\', \'TIC\', \'TRA\'));')
    op.execute('UPDATE public."OperatingTeams" set isactive = false where name = \'Business Team\';')

def downgrade():
    op.execute('UPDATE public."FOIRequestTeams" set teamid = (select teamid from public."OperatingTeams" where name = \'Business Team\') where teamid = (select teamid from public."OperatingTeams" where name = \'Central Team\') and programareaid in (select programareaid from public."ProgramAreas" where iaocode in (\'JER\', \'LBR\', \'MMA\', \'TAC\', \'TIC\', \'TRA\'));')
    op.execute('UPDATE public."OperatingTeams" set isactive = true where name = \'Business Team\';')
