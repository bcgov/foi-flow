"""empty message

Revision ID: ec27defe9178
Revises: 1d60153653db
Create Date: 2024-09-06 19:46:07.867757

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ec27defe9178'
down_revision = '1d60153653db'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('''INSERT INTO public."ProgramAreas"(name, type, isactive, bcgovcode, iaocode)	VALUES ('Ministry of Children and Family Development (Generals)', 'BC GOV Ministry', True, 'CAF', 'CAF');commit;''')
    
    op.execute('''INSERT INTO public."ProgramAreaDivisions"(
                    programareaid, name, isactive, created_at, createdby, sortorder, updated_at, updatedby, issection, parentid, specifictopersonalrequests, type)
                    SELECT 
                    (select programareaid from public."ProgramAreas" where bcgovcode='CAF'), name, isactive, created_at, createdby, sortorder, updated_at, updatedby, issection, parentid, specifictopersonalrequests, type
                    FROM public."ProgramAreaDivisions"
                    where programareaid = (select programareaid from public."ProgramAreas" where bcgovcode = 'MCF')
                    and specifictopersonalrequests is false
                    and isactive = true
                ORDER BY divisionid ASC ''')
    
    op.execute('''INSERT INTO public."OperatingTeams"(name, description, isactive, type) VALUES ('CAF Ministry Team', 'CAF Ministry Team', True, 'ministry');commit;''')

    op.execute('''INSERT INTO public."FOIRequestTeams"(
                    requesttype, requeststatusid, teamid, programareaid, isactive, requeststatuslabel)
                    SELECT 
                    requesttype, requeststatusid, 
                    case when ot.name = 'MCF Ministry Team' 
                        then (select teamid from public."OperatingTeams" where name = 'CAF Ministry Team')
                        else (rt.teamid) end,
                    (select programareaid from public."ProgramAreas" where bcgovcode = 'CAF'), rt.isactive, requeststatuslabel
                    FROM public."FOIRequestTeams" rt
                    join public."OperatingTeams" ot on rt.teamid = ot.teamid
                    where 
                    programareaid = (select programareaid from public."ProgramAreas" where bcgovcode = 'MCF') and
                    requesttype = 'General' and rt.isactive = true''')

def downgrade():
    op.execute('''delete from public."FOIRequestTeams" where programareaid in (select programareaid from public."ProgramAreas" where bcgovcode = 'CAF')''')
    
    op.execute('''delete from public."OperatingTeams" where name = 'CAF Ministry Team' ''')

    op.execute('''delete from public."ProgramAreaDivisions" where programareaid in (select programareaid from public."ProgramAreas" where bcgovcode = 'CAF')''')

    op.execute('''delete from public."ProgramAreas" where bcgovcode = 'CAF' ''')
#