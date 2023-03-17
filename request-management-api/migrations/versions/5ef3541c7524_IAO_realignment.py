"""IAO Re-alignment Apr 2023

Revision ID: 5ef3541c7524
Revises: e0cdabe946cc
Create Date: 2023-03-15 12:41:10.175274

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5ef3541c7524'
down_revision = 'e0cdabe946cc'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('''INSERT INTO public."OperatingTeams"(name, description, type, isactive) VALUES ('Central and Economy Team', 'Central and Economy Team', 'iao', true);commit;''')
    op.execute('''INSERT INTO public."OperatingTeams"(name, description, type, isactive) VALUES ('Justice and Resource Team', 'Justice and Resource Team', 'iao', true);commit;''')
    op.execute('''INSERT INTO public."OperatingTeams"(name, description, type, isactive) VALUES ('Community and Health Team', 'Community and Health Team', 'iao', true);commit;''')
    op.execute('''INSERT INTO public."OperatingTeams"(name, description, type, isactive) VALUES ('Children and Family Team', 'Children and Family Team', 'iao', true);commit;''')
    op.execute('''INSERT INTO public."OperatingTeams"(name, description, type, isactive) VALUES ('Children and Education Team', 'Children and Family Team', 'iao', true);commit;''')
    op.execute('''INSERT INTO public."OperatingTeams"(name, description, type, isactive) VALUES ('Coordinated Response Unit', 'Coordinated Response Unit', 'iao', true);commit;''')

    # insert into FOI Request Teams for Central and Economy Team
    op.execute('''INSERT INTO public."FOIRequestTeams"(	requesttype, requeststatusid, teamid, programareaid, isactive)
	select requesttype, requeststatusid, teamid, programareaid, isactive from
	(select 'General' as requesttype, (select teamid from public."OperatingTeams" where name = 'Central and Economy Team') as teamid, requeststatusid, true as isactive
	 from public."FOIRequestStatuses" where name in (
        'Call For Records','Closed','Records Review','Fee Estimate','Consult','Ministry Sign Off','On Hold','Harms Assessment','Response'
    )) sq,
	(select programareaid from public."ProgramAreas" where iaocode in ('OOP', 'PSA', 'FIN', 'TRA', 'TIC',  'GCP', 'JED', 'MMA','LBR','TAC','CTZ','CAS','LDB','OBC','MGC')) sq2
    ''')

    op.execute('''INSERT INTO public."FOIRequestTeams"(	requesttype, requeststatusid, teamid, programareaid, isactive)
	select requesttype, requeststatusid, teamid, programareaid, isactive from
	(select 'Personal' as requesttype, (select teamid from public."OperatingTeams" where name = 'Central and Economy Team') as teamid, requeststatusid, true as isactive
	 from public."FOIRequestStatuses" where name in (
        'Open','Call For Records','Closed','Records Review','Fee Estimate','Consult','Ministry Sign Off','On Hold','Deduplication','Harms Assessment','Response'
    )) sq,
	(select programareaid from public."ProgramAreas" where iaocode in ('OOP', 'PSA', 'FIN', 'TRA', 'TIC',  'GCP', 'JED', 'MMA','LBR','TAC','CTZ','CAS','LDB','OBC','MGC')) sq2
    ''')

    # insert into FOI Request Teams for Justice and Resource Team
    op.execute('''INSERT INTO public."FOIRequestTeams"(	requesttype, requeststatusid, teamid, programareaid, isactive)
	select requesttype, requeststatusid, teamid, programareaid, isactive from
	(select 'General' as requesttype, (select teamid from public."OperatingTeams" where name = 'Justice and Resource Team') as teamid, requeststatusid, true as isactive
	 from public."FOIRequestStatuses" where name in (
        'Call For Records','Closed','Records Review','Fee Estimate','Consult','Ministry Sign Off','On Hold','Harms Assessment','Response'
    )) sq,
	(select programareaid from public."ProgramAreas" where iaocode in ('FOR','EML','PSS','COR','EMC', 'MAG','OCC', 'HSG', 'IIO', 'MOE', 'EAO', 'WLR')) sq2
    ''')

    op.execute('''INSERT INTO public."FOIRequestTeams"(	requesttype, requeststatusid, teamid, programareaid, isactive)
	select requesttype, requeststatusid, teamid, programareaid, isactive from
	(select 'Personal' as requesttype, (select teamid from public."OperatingTeams" where name = 'Justice and Resource Team') as teamid, requeststatusid, true as isactive
	 from public."FOIRequestStatuses" where name in (
        'Open','Call For Records','Closed','Records Review','Fee Estimate','Consult','Ministry Sign Off','On Hold','Deduplication','Harms Assessment','Response'
    )) sq,
	(select programareaid from public."ProgramAreas" where iaocode in ('FOR','EML','PSS','COR','EMC', 'MAG','OCC', 'HSG', 'IIO', 'MOE', 'EAO', 'WLR')) sq2
    ''')

    # insert into FOI Request Teams for Community and Health Team
    op.execute('''INSERT INTO public."FOIRequestTeams"(	requesttype, requeststatusid, teamid, programareaid, isactive)
	select requesttype, requeststatusid, teamid, programareaid, isactive from
	(select 'General' as requesttype, (select teamid from public."OperatingTeams" where name = 'Community and Health Team') as teamid, requeststatusid, true as isactive
	 from public."FOIRequestStatuses" where name in (
        'Call For Records','Closed','Records Review','Fee Estimate','Consult','Ministry Sign Off','On Hold','Harms Assessment','Response'
    )) sq,
	(select programareaid from public."ProgramAreas" where iaocode in ('MSD', 'CLB', 'PSE', 'HLTH', 'MHA', 'IRR', 'DAS', 'AGR')) sq2
    ''')

    op.execute('''INSERT INTO public."FOIRequestTeams"(	requesttype, requeststatusid, teamid, programareaid, isactive)
	select requesttype, requeststatusid, teamid, programareaid, isactive from
	(select 'Personal' as requesttype, (select teamid from public."OperatingTeams" where name = 'Community and Health Team') as teamid, requeststatusid, true as isactive
	 from public."FOIRequestStatuses" where name in (
        'Open','Call For Records','Closed','Records Review','Fee Estimate','Consult','Ministry Sign Off','On Hold','Deduplication','Harms Assessment','Response'
    )) sq,
	(select programareaid from public."ProgramAreas" where iaocode in ('MSD', 'CLB', 'PSE', 'HLTH', 'MHA', 'IRR', 'DAS', 'AGR')) sq2
    ''')

    # insert into FOI Request Teams for Children and Education Team
    op.execute('''INSERT INTO public."FOIRequestTeams"(	requesttype, requeststatusid, teamid, programareaid, isactive)
	select requesttype, requeststatusid, teamid, programareaid, isactive from
	(select 'General' as requesttype, (select teamid from public."OperatingTeams" where name = 'Children and Education Team') as teamid, requeststatusid, true as isactive
	 from public."FOIRequestStatuses" where name in (
        'Call For Records','Closed','Records Review','Fee Estimate','Consult','Ministry Sign Off','On Hold','Harms Assessment','Response'
    )) sq,
	(select programareaid from public."ProgramAreas" where iaocode in ('CFD', 'ECC')) sq2
    ''')

    op.execute('''INSERT INTO public."FOIRequestTeams"(	requesttype, requeststatusid, teamid, programareaid, isactive)
	select requesttype, requeststatusid, teamid, programareaid, isactive from
	(select 'Personal' as requesttype, (select teamid from public."OperatingTeams" where name = 'Children and Education Team') as teamid, requeststatusid, true as isactive
	 from public."FOIRequestStatuses" where name in (
        'Open','Call For Records','Closed','Records Review','Fee Estimate','Consult','Ministry Sign Off','On Hold','Deduplication','Harms Assessment','Response'
    )) sq,
	(select programareaid from public."ProgramAreas" where iaocode in ('CFD', 'ECC')) sq2
    ''')



    # insert into FOI Request Teams for Children and Family Team
    op.execute('''INSERT INTO public."FOIRequestTeams"(	requesttype, requeststatusid, teamid, programareaid, isactive)
	select requesttype, requeststatusid, teamid, programareaid, isactive from
	(select 'General' as requesttype, (select teamid from public."OperatingTeams" where name = 'Children and Family Team') as teamid, requeststatusid, true as isactive
	 from public."FOIRequestStatuses" where name in (
        'Call For Records','Closed','Records Review','Fee Estimate','Consult','Ministry Sign Off','On Hold','Harms Assessment','Response'
    )) sq,
	(select programareaid from public."ProgramAreas" where iaocode in ('CFD')) sq2
    ''')

    op.execute('''INSERT INTO public."FOIRequestTeams"(	requesttype, requeststatusid, teamid, programareaid, isactive)
	select requesttype, requeststatusid, teamid, programareaid, isactive from
	(select 'Personal' as requesttype, (select teamid from public."OperatingTeams" where name = 'Children and Family Team') as teamid, requeststatusid, true as isactive
	 from public."FOIRequestStatuses" where name in (
        'Open','Call For Records','Closed','Records Review','Fee Estimate','Consult','Ministry Sign Off','On Hold','Deduplication','Harms Assessment','Response'
    )) sq,
	(select programareaid from public."ProgramAreas" where iaocode in ('CFD')) sq2
    ''')



def downgrade():
    op.execute('''Delete from public."FOIRequestTeams" where teamid in
    (select teamid from public."OperatingTeams" where name in ('Central and Economy Team','Justice and Resource Team','Community and Health Team','Children and Family Team','Children and Education Team','Coordinated Response Unit'))''')

    op.execute('''Delete from public."OperatingTeams" where name in ('Central and Economy Team','Justice and Resource Team','Community and Health Team','Children and Family Team','Children and Education Team','Coordinated Response Unit')''')