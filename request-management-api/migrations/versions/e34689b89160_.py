"""Processing Team Organizational Adjustments

Revision ID: e34689b89160
Revises: 7fe3c2636fbf
Create Date: 2025-11-07 16:02:27.125885

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'e34689b89160'
down_revision = '7fe3c2636fbf'
branch_labels = None
depends_on = None


def upgrade():
    # Deactivate old teams
    # op.execute('''UPDATE public."OperatingTeams" SET isactive = false WHERE name = 'Coordinated Response Unit';''')
    # op.execute('''UPDATE public."OperatingTeams" SET isactive = false WHERE name = 'Central and Economy Team';''')
    # op.execute('''UPDATE public."OperatingTeams" SET isactive = false WHERE name = 'Resource and Justice Team';''')

    # Create new teams
    op.execute('''INSERT INTO public."OperatingTeams" (name, description, type, isactive) VALUES ('Justice Team', 'Justice Team', 'iao', true);''')
    op.execute('''INSERT INTO public."OperatingTeams" (name, description, type, isactive) VALUES ('Infrastructure Team', 'Infrastructure Team', 'iao', true);''')
    op.execute('''UPDATE public."OperatingTeams" SET isactive = true WHERE name = 'Resource Team';''') # Resource Team exists in DB, therefore reactivate

    # FOIRequestTeams Ministry Mapping
    op.execute('''INSERT INTO public."FOIRequestTeams"(	requesttype, requeststatusid, teamid, programareaid, isactive, requeststatuslabel)
	select requesttype, requeststatusid, teamid, programareaid, isactive, statuslabel from
	(select 'General' as requesttype, (select teamid from public."OperatingTeams" where name = 'Justice Team') as teamid, requeststatusid, true as isactive, statuslabel
	 from public."FOIRequestStatuses" where name in (
        'Call For Records','Closed','Records Review','Fee Estimate','Consult','Ministry Sign Off','On Hold','Harms Assessment','Response'
    )) sq,
	(select programareaid from public."ProgramAreas" where iaocode in ('MAG', 'PSS', 'COR', 'IIO', 'OCC', 'CLB', 'GCP','FIN','TRA','TIC')) sq2
    ''')
    op.execute('''INSERT INTO public."FOIRequestTeams"(	requesttype, requeststatusid, teamid, programareaid, isactive, requeststatuslabel)
	select requesttype, requeststatusid, teamid, programareaid, isactive, statuslabel from
	(select 'Personal' as requesttype, (select teamid from public."OperatingTeams" where name = 'Justice Team') as teamid, requeststatusid, true as isactive, statuslabel
	 from public."FOIRequestStatuses" where name in (
        'Open','Call For Records','Closed','Records Review','Fee Estimate','Consult','Ministry Sign Off','On Hold','Deduplication','Harms Assessment','Response'
    )) sq,
	(select programareaid from public."ProgramAreas" where iaocode in ('MAG', 'PSS', 'COR', 'IIO', 'OCC', 'CLB', 'GCP','FIN','TRA','TIC')) sq2
    ''')

    op.execute('''INSERT INTO public."FOIRequestTeams"(	requesttype, requeststatusid, teamid, programareaid, isactive, requeststatuslabel)
	select requesttype, requeststatusid, teamid, programareaid, isactive, statuslabel from
	(select 'General' as requesttype, (select teamid from public."OperatingTeams" where name = 'Infrastructure Team') as teamid, requeststatusid, true as isactive, statuslabel
	 from public."FOIRequestStatuses" where name in (
        'Call For Records','Closed','Records Review','Fee Estimate','Consult','Ministry Sign Off','On Hold','Harms Assessment','Response'
    )) sq,
	(select programareaid from public."ProgramAreas" where iaocode in ('OOP', 'LDB', 'PSA', 'JED', 'TACS', 'LBR', 'HSG','CTZ','AGR')) sq2
    ''')
    op.execute('''INSERT INTO public."FOIRequestTeams"(	requesttype, requeststatusid, teamid, programareaid, isactive, requeststatuslabel)
	select requesttype, requeststatusid, teamid, programareaid, isactive, statuslabel from
	(select 'Personal' as requesttype, (select teamid from public."OperatingTeams" where name = 'Infrastructure Team') as teamid, requeststatusid, true as isactive, statuslabel
	 from public."FOIRequestStatuses" where name in (
        'Open','Call For Records','Closed','Records Review','Fee Estimate','Consult','Ministry Sign Off','On Hold','Deduplication','Harms Assessment','Response'
    )) sq,
	(select programareaid from public."ProgramAreas" where iaocode in ('OOP', 'LDB', 'PSA', 'JED', 'TACS', 'LBR', 'HSG','CTZ','AGR')) sq2
    ''')

    op.execute('''INSERT INTO public."FOIRequestTeams"(	requesttype, requeststatusid, teamid, programareaid, isactive, requeststatuslabel)
	select requesttype, requeststatusid, teamid, programareaid, isactive, statuslabel from
	(select 'General' as requesttype, (select teamid from public."OperatingTeams" where name = 'Resource Team') as teamid, requeststatusid, true as isactive, statuslabel
	 from public."FOIRequestStatuses" where name in (
        'Call For Records','Closed','Records Review','Fee Estimate','Consult','Ministry Sign Off','On Hold','Harms Assessment','Response'
    )) sq,
	(select programareaid from public."ProgramAreas" where iaocode in ('MCM', 'WLR', 'FOR', 'ECS', 'ENV', 'EAO', 'EMC','DAS','IRR')) sq2
    ''')
    op.execute('''INSERT INTO public."FOIRequestTeams"(	requesttype, requeststatusid, teamid, programareaid, isactive, requeststatuslabel)
	select requesttype, requeststatusid, teamid, programareaid, isactive, statuslabel from
	(select 'Personal' as requesttype, (select teamid from public."OperatingTeams" where name = 'Resource Team') as teamid, requeststatusid, true as isactive, statuslabel
	 from public."FOIRequestStatuses" where name in (
        'Open','Call For Records','Closed','Records Review','Fee Estimate','Consult','Ministry Sign Off','On Hold','Deduplication','Harms Assessment','Response'
    )) sq,
	(select programareaid from public."ProgramAreas" where iaocode in ('MCM', 'WLR', 'FOR', 'ECS', 'ENV', 'EAO', 'EMC','DAS','IRR')) sq2
    ''')

    # Deactivate FOIRequestTeam mapping for old teams
    # op.execute('''UPDATE public."FOIRequestTeams" SET isactive = false WHERE teamid = (SELECT teamid FROM public."OperatingTeams" WHERE name = 'Central and Economy Team');''')
    # op.execute('''UPDATE public."FOIRequestTeams" SET isactive = false WHERE teamid = (SELECT teamid FROM public."OperatingTeams" WHERE name = 'Resource and Justice Team');''')
    # op.execute('''UPDATE public."FOIRequestTeams" SET isactive = false WHERE teamid = (SELECT teamid FROM public."OperatingTeams" WHERE name = 'Coordinated Response Unit');''')

    # Template Operating Team Email adjustments
    op.execute('''UPDATE public."OperatingTeamEmails" SET teamid = (SELECT teamid FROM public."OperatingTeams" WHERE name = 'Infrastructure Team') WHERE email_address = 'IAO.CentralAndEconomyTeam@gov.bc.ca';''')
    op.execute('''UPDATE public."OperatingTeamEmails" SET teamid = (SELECT teamid FROM public."OperatingTeams" WHERE name = 'Resource Team') WHERE email_address = 'IAOResourceTeam@gov.bc.ca';''')
    op.execute('''UPDATE public."OperatingTeamEmails" SET teamid = (SELECT teamid FROM public."OperatingTeams" WHERE name = 'Justice Team') WHERE email_address = 'IAO.CoordinatedResponseUnit@gov.bc.ca';''')

    # Additional Reorg Adjustments
    op.execute('''UPDATE public."FOIRequestTeams" SET isactive = false WHERE teamid = (SELECT teamid from public."OperatingTeams" WHERE name = 'Children and Education Team');''')
    op.execute('''UPDATE public."OperatingTeams" SET isactive = false WHERE name = 'Children and Education Team';''')
    
def downgrade():
    op.execute('''UPDATE public."FOIRequestTeams" SET isactive = true WHERE teamid = (SELECT teamid from public."OperatingTeams" WHERE name = 'Children and Education Team');''')
    op.execute('''UPDATE public."OperatingTeams" SET isactive = true WHERE name = 'Children and Education Team';''')
    
    op.execute('''UPDATE public."OperatingTeamEmails" SET teamid = (SELECT teamid FROM public."OperatingTeams" WHERE name = 'Central and Economy Team') WHERE email_address = 'IAO.CentralAndEconomyTeam@gov.bc.ca';''')
    op.execute('''UPDATE public."OperatingTeamEmails" SET teamid = (SELECT teamid FROM public."OperatingTeams" WHERE name = 'Resource and Justice Team')  WHERE email_address = 'IAOResourceTeam@gov.bc.ca';''')
    op.execute('''UPDATE public."OperatingTeamEmails" SET teamid = (SELECT teamid FROM public."OperatingTeams" WHERE name = 'Coordinated Response Unit') WHERE email_address = 'IAO.CoordinatedResponseUnit@gov.bc.ca';''')

    # op.execute('''UPDATE public."FOIRequestTeams" SET isactive = true WHERE teamid = (SELECT teamid from public."OperatingTeams" WHERE name = 'Central and Economy Team');''')
    # op.execute('''UPDATE public."FOIRequestTeams" SET isactive = true WHERE teamid = (SELECT teamid from public."OperatingTeams" WHERE name = 'Resource and Justice Team');''')
    # op.execute('''UPDATE public."FOIRequestTeams" SET isactive = true WHERE teamid = (SELECT teamid from public."OperatingTeams" WHERE name = 'Coordinated Response Unit');''')

    op.execute('''DELETE FROM public."FOIRequestTeams" WHERE teamid in
    (SELECT teamid FROM public."OperatingTeams" WHERE name in ('Infrastructure Team', 'Justice Team'));''')
    op.execute('''DELETE FROM public."FOIRequestTeams" WHERE teamid = (SELECT teamid FROM public."OperatingTeams" WHERE name = 'Resource Team') AND isactive = true;''')

    op.execute('''DELETE FROM public."OperatingTeams" WHERE name = 'Justice Team';''')
    op.execute('''DELETE FROM public."OperatingTeams" WHERE name = 'Infrastructure Team';''')
    op.execute('''UPDATE public."OperatingTeams" SET isactive = false WHERE name = 'Resource Team';''')

    # op.execute('''UPDATE public."OperatingTeams" SET isactive = true WHERE name = 'Coordinated Response Unit';''')
    # op.execute('''UPDATE public."OperatingTeams" SET isactive = true WHERE name = 'Central and Economy Team';''')
    # op.execute('''UPDATE public."OperatingTeams" SET isactive = true WHERE name = 'Resource and Justice Team';''')