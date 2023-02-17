"""empty message

Revision ID: f6b634c49b35
Revises: c58724c6ae0d
Create Date: 2023-02-16 11:51:23.884073

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f6b634c49b35'
down_revision = 'c58724c6ae0d'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('INSERT INTO public."FOIRequestTeams"(requesttype, requeststatusid, teamid, programareaid, isactive)\
    SELECT FRT.requesttype,FRT.requeststatusid, (SELECT teamid FROM public."OperatingTeams" where name in (\'COR Ministry Team\')),\
    (SELECT programareaid FROM "ProgramAreas" WHERE iaocode =\'COR\' and isactive=true), true as isactive\
    FROM public."FOIRequestTeams" FRT JOIN public."OperatingTeams" OT ON FRT.teamid = OT.teamid WHERE FRT.programareaid in (SELECT programareaid FROM "ProgramAreas" \
    WHERE iaocode in(\'PSS\') and isactive = true) AND OT."type" =\'ministry\'')


def downgrade():
    op.execute('DELETE FROM public."FOIRequestTeams"\
	WHERE teamid = (SELECT teamid FROM public."OperatingTeams" where name in (\'COR Ministry Team\')) \
	AND programareaid =(SELECT programareaid FROM "ProgramAreas" WHERE iaocode =\'COR\' and isactive=true);')
