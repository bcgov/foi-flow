"""empty message

Revision ID: 07ff5b14f1f0
Revises: 2e1165cddc53
Create Date: 2023-02-16 11:12:04.379912

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '07ff5b14f1f0'
down_revision = '2e1165cddc53'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('INSERT INTO public."FOIRequestTeams"(requesttype, requeststatusid, teamid, programareaid, isactive)\
    SELECT FRT.requesttype,FRT.requeststatusid,FRT.teamid, (SELECT programareaid FROM "ProgramAreas"\
    WHERE iaocode =\'HSG\' and isactive=true),true as isactive FROM public."FOIRequestTeams" FRT JOIN public."OperatingTeams" OT \
    ON FRT.teamid = OT.teamid WHERE FRT.programareaid in (SELECT programareaid FROM "ProgramAreas" \
    WHERE iaocode in(\'PSS\') and isactive = true) AND OT."type" =\'iao\'')


def downgrade():
    op.execute('DELETE FROM public."FOIRequestTeams"\
	WHERE teamid = (SELECT teamid FROM public."OperatingTeams" where name in (\'Justice Health Team\')) \
	AND programareaid =(SELECT programareaid FROM "ProgramAreas" WHERE iaocode =\'HSG\' and isactive=true);')