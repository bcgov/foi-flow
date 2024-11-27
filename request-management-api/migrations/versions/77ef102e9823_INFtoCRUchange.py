"""empty message

Revision ID: 77ef102e9823
Revises: ddcd4045fc38
Create Date: 2024-11-27 10:48:56.279792

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '77ef102e9823'
down_revision = 'ddcd4045fc38'
branch_labels = None
depends_on = None


def upgrade():
     # add INF to Coordinated Response Unit
    op.execute('''INSERT INTO public."FOIRequestTeams"(	requesttype, requeststatusid, teamid, programareaid, isactive, requeststatuslabel)
	select requesttype, requeststatusid, teamid, programareaid, isactive, statuslabel from
	(select 'General' as requesttype, (select teamid from public."OperatingTeams" where name = 'Coordinated Response Unit') as teamid, requeststatusid, true as isactive, statuslabel
	 from public."FOIRequestStatuses" where name in (
        'Call For Records','Closed','Records Review','Fee Estimate','Consult','Ministry Sign Off','On Hold','Harms Assessment','Response'
    )) sq,
	(select programareaid from public."ProgramAreas" where iaocode in ('INF')) sq2
    ''')


    op.execute('''UPDATE public."FOIRequestTeams" SET isactive=false WHERE programareaid in(
        SELECT programareaid FROM public."ProgramAreas" WHERE iaocode='INF') AND 
        teamid in  (SELECT teamid FROM public."OperatingTeams" WHERE name='Central and Economy Team');commit;''')


def downgrade():
    # remove CRU INF entries
    op.execute('''
        delete from public."FOIRequestTeams" where 
        programareaid in (select programareaid from public."ProgramAreas" where iaocode = 'INF') and 
        teamid in  (SELECT teamid FROM public."OperatingTeams" WHERE name='Coordinated Response Unit') ;commit;
    ''')

    op.execute('''UPDATE public."FOIRequestTeams" SET isactive=true WHERE programareaid in(
        SELECT programareaid FROM public."ProgramAreas" WHERE iaocode='INF') AND 
        teamid in  (SELECT teamid FROM public."OperatingTeams" WHERE name='Central and Economy Team');commit;''')
