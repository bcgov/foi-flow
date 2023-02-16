"""empty message

Revision ID: c58724c6ae0d
Revises: 07ff5b14f1f0
Create Date: 2023-02-16 11:41:05.306024

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c58724c6ae0d'
down_revision = '07ff5b14f1f0'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('INSERT INTO public."FOIRequestTeams"(requesttype, requeststatusid, teamid, programareaid, isactive)\
    SELECT FRT.requesttype,FRT.requeststatusid, (SELECT teamid FROM public."OperatingTeams" where name in (\'HSG Ministry Team\')),\
    (SELECT programareaid FROM "ProgramAreas" WHERE iaocode =\'HSG\' and isactive=true), true as isactive\
    FROM public."FOIRequestTeams" FRT JOIN public."OperatingTeams" OT ON FRT.teamid = OT.teamid WHERE FRT.programareaid in (SELECT programareaid FROM "ProgramAreas" \
    WHERE iaocode in(\'PSS\') and isactive = true) AND OT."type" =\'ministry\'')


def downgrade():
    op.execute('DELETE FROM public."FOIRequestTeams"\
	WHERE teamid = (SELECT teamid FROM public."OperatingTeams" where name in (\'HSG Ministry Team\')) \
	AND programareaid =(SELECT programareaid FROM "ProgramAreas" WHERE iaocode =\'HSG\' and isactive=true);')