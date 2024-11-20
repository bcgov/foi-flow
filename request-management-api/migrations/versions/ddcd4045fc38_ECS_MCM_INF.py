"""empty message

Revision ID: ddcd4045fc38
Revises: bbee01df3e8d
Create Date: 2023-01-05 16:56:14.273444

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ddcd4045fc38'
down_revision = 'bbee01df3e8d'
branch_labels = None
depends_on = None


def upgrade():

    op.execute('''
        INSERT INTO public."ProgramAreas"(
        name, type, isactive, bcgovcode, iaocode)
        VALUES ('Ministry of Infrastructure', 'BC GOV Ministry', true, 'INF', 'INF');commit;
    ''')
    op.execute('''
        INSERT INTO public."ProgramAreas"(
        name, type, isactive, bcgovcode, iaocode)
        VALUES ('Ministry of Mining and Critical Minerals', 'BC GOV Ministry', true, 'MCM', 'MCM');commit;
    ''')
    op.execute('''
        INSERT INTO public."ProgramAreas"(
        name, type, isactive, bcgovcode, iaocode)
        VALUES ('Ministry of Energy and Climate Solutions', 'BC GOV Ministry', true, 'ECS', 'ECS');commit;
    ''')
    op.execute('''
        UPDATE public."ProgramAreas"
        SET name='Ministry of Housing and Municipal Affairs'
        WHERE iaocode='HSG';commit;
    ''')
    op.execute('''
        UPDATE public."ProgramAreas"
        SET name='Ministry of Environment and Parks'
        WHERE iaocode='MOE';commit;
    ''')
    op.execute('''
        UPDATE public."ProgramAreas"
        SET name='Ministry of Transportation and Transit'
        WHERE bcgovcode='TRA';commit;
    ''')
    op.execute('''
        INSERT INTO public."OperatingTeams"(
        name, description, type, isactive)
        VALUES ('INF Ministry Team', 'INF Ministry Team', 'ministry', true);commit;
    ''')
    op.execute('''
        INSERT INTO public."OperatingTeams"(
        name, description, type, isactive)
        VALUES ('MCM Ministry Team', 'MCM Ministry Team', 'ministry', true);commit;
    ''')
    op.execute('''
        INSERT INTO public."OperatingTeams"(
        name, description, type, isactive)
        VALUES ('ECS Ministry Team', 'ECS Ministry Team', 'ministry', true);commit;
    ''')

    # add MCM and ECS to Resource and Justice Team
    op.execute('''INSERT INTO public."FOIRequestTeams"(	requesttype, requeststatusid, teamid, programareaid, isactive, requeststatuslabel)
	select requesttype, requeststatusid, teamid, programareaid, isactive, statuslabel from
	(select 'General' as requesttype, (select teamid from public."OperatingTeams" where name = 'Resource and Justice Team') as teamid, requeststatusid, true as isactive, statuslabel
	 from public."FOIRequestStatuses" where name in (
        'Call For Records','Closed','Records Review','Fee Estimate','Consult','Ministry Sign Off','On Hold','Harms Assessment','Response'
    )) sq,
	(select programareaid from public."ProgramAreas" where iaocode in ('MCM', 'ECS')) sq2
    ''')

    op.execute('''INSERT INTO public."FOIRequestTeams"(	requesttype, requeststatusid, teamid, programareaid, isactive, requeststatuslabel)
	select requesttype, requeststatusid, teamid, programareaid, isactive, statuslabel from
	(select 'Personal' as requesttype, (select teamid from public."OperatingTeams" where name = 'Resource and Justice Team') as teamid, requeststatusid, true as isactive, statuslabel
	 from public."FOIRequestStatuses" where name in (
        'Call For Records','Closed','Records Review','Fee Estimate','Consult','Ministry Sign Off','On Hold','Harms Assessment','Response'
    )) sq,
	(select programareaid from public."ProgramAreas" where iaocode in ('MCM', 'ECS')) sq2
    ''')

    # add ECS to ECS Minsitry Team
    op.execute('''INSERT INTO public."FOIRequestTeams"(	requesttype, requeststatusid, teamid, programareaid, isactive, requeststatuslabel)
	select requesttype, requeststatusid, teamid, programareaid, isactive, statuslabel from
	(select 'General' as requesttype, (select teamid from public."OperatingTeams" where name = 'ECS Ministry Team') as teamid, requeststatusid, true as isactive, statuslabel
	 from public."FOIRequestStatuses" where name in (
        'Call For Records','Closed','Records Review','Fee Estimate','Consult','Ministry Sign Off','On Hold','Harms Assessment','Response'
    )) sq,
	(select programareaid from public."ProgramAreas" where iaocode in ('ECS')) sq2
    ''')

    op.execute('''INSERT INTO public."FOIRequestTeams"(	requesttype, requeststatusid, teamid, programareaid, isactive, requeststatuslabel)
	select requesttype, requeststatusid, teamid, programareaid, isactive, statuslabel from
	(select 'Personal' as requesttype, (select teamid from public."OperatingTeams" where name = 'ECS Ministry Team') as teamid, requeststatusid, true as isactive, statuslabel
	 from public."FOIRequestStatuses" where name in (
        'Call For Records','Closed','Records Review','Fee Estimate','Consult','Ministry Sign Off','On Hold','Harms Assessment','Response'
    )) sq,
	(select programareaid from public."ProgramAreas" where iaocode in ('ECS')) sq2
    ''')

    # add MCM to MCM Minsitry Team
    op.execute('''INSERT INTO public."FOIRequestTeams"(	requesttype, requeststatusid, teamid, programareaid, isactive, requeststatuslabel)
	select requesttype, requeststatusid, teamid, programareaid, isactive, statuslabel from
	(select 'General' as requesttype, (select teamid from public."OperatingTeams" where name = 'MCM Ministry Team') as teamid, requeststatusid, true as isactive, statuslabel
	 from public."FOIRequestStatuses" where name in (
        'Call For Records','Closed','Records Review','Fee Estimate','Consult','Ministry Sign Off','On Hold','Harms Assessment','Response'
    )) sq,
	(select programareaid from public."ProgramAreas" where iaocode in ('MCM')) sq2
    ''')

    op.execute('''INSERT INTO public."FOIRequestTeams"(	requesttype, requeststatusid, teamid, programareaid, isactive, requeststatuslabel)
	select requesttype, requeststatusid, teamid, programareaid, isactive, statuslabel from
	(select 'Personal' as requesttype, (select teamid from public."OperatingTeams" where name = 'MCM Ministry Team') as teamid, requeststatusid, true as isactive, statuslabel
	 from public."FOIRequestStatuses" where name in (
        'Call For Records','Closed','Records Review','Fee Estimate','Consult','Ministry Sign Off','On Hold','Harms Assessment','Response'
    )) sq,
	(select programareaid from public."ProgramAreas" where iaocode in ('MCM')) sq2
    ''')

    
    # add INF to Central and Economy Team
    op.execute('''INSERT INTO public."FOIRequestTeams"(	requesttype, requeststatusid, teamid, programareaid, isactive, requeststatuslabel)
	select requesttype, requeststatusid, teamid, programareaid, isactive, statuslabel from
	(select 'General' as requesttype, (select teamid from public."OperatingTeams" where name = 'Central and Economy Team') as teamid, requeststatusid, true as isactive, statuslabel
	 from public."FOIRequestStatuses" where name in (
        'Call For Records','Closed','Records Review','Fee Estimate','Consult','Ministry Sign Off','On Hold','Harms Assessment','Response'
    )) sq,
	(select programareaid from public."ProgramAreas" where iaocode in ('INF')) sq2
    ''')

    op.execute('''INSERT INTO public."FOIRequestTeams"(	requesttype, requeststatusid, teamid, programareaid, isactive, requeststatuslabel)
	select requesttype, requeststatusid, teamid, programareaid, isactive, statuslabel from
	(select 'Personal' as requesttype, (select teamid from public."OperatingTeams" where name = 'Central and Economy Team') as teamid, requeststatusid, true as isactive, statuslabel
	 from public."FOIRequestStatuses" where name in (
        'Call For Records','Closed','Records Review','Fee Estimate','Consult','Ministry Sign Off','On Hold','Harms Assessment','Response'
    )) sq,
	(select programareaid from public."ProgramAreas" where iaocode in ('INF')) sq2
    ''')

    # add INF to INF Minsitry Team
    op.execute('''INSERT INTO public."FOIRequestTeams"(	requesttype, requeststatusid, teamid, programareaid, isactive, requeststatuslabel)
	select requesttype, requeststatusid, teamid, programareaid, isactive, statuslabel from
	(select 'General' as requesttype, (select teamid from public."OperatingTeams" where name = 'INF Ministry Team') as teamid, requeststatusid, true as isactive, statuslabel
	 from public."FOIRequestStatuses" where name in (
        'Call For Records','Closed','Records Review','Fee Estimate','Consult','Ministry Sign Off','On Hold','Harms Assessment','Response'
    )) sq,
	(select programareaid from public."ProgramAreas" where iaocode in ('INF')) sq2
    ''')

    op.execute('''INSERT INTO public."FOIRequestTeams"(	requesttype, requeststatusid, teamid, programareaid, isactive, requeststatuslabel)
	select requesttype, requeststatusid, teamid, programareaid, isactive, statuslabel from
	(select 'Personal' as requesttype, (select teamid from public."OperatingTeams" where name = 'INF Ministry Team') as teamid, requeststatusid, true as isactive, statuslabel
	 from public."FOIRequestStatuses" where name in (
        'Call For Records','Closed','Records Review','Fee Estimate','Consult','Ministry Sign Off','On Hold','Harms Assessment','Response'
    )) sq,
	(select programareaid from public."ProgramAreas" where iaocode in ('INF')) sq2
    ''')

    op.execute('''
        INSERT INTO public."ProgramAreaDivisions"(
        programareaid, name, isactive, created_at, createdby, issection)
        VALUES ((select programareaid from public."ProgramAreas" where iaocode = 'MCM'), \'Minister’s Office\', true, now(), 'System', false);
    ''')

    op.execute('''
        INSERT INTO public."ProgramAreaDivisions"(
        programareaid, name, isactive, created_at, createdby, issection)
        VALUES ((select programareaid from public."ProgramAreas" where iaocode = 'ECS'), \'Minister’s Office\', true, now(), 'System', false);
    ''')

    op.execute('''
        INSERT INTO public."ProgramAreaDivisions"(
        programareaid, name, isactive, created_at, createdby, issection)
        VALUES ((select programareaid from public."ProgramAreas" where iaocode = 'INF'), \'Minister’s Office\', true, now(), 'System', false);
    ''')

    op.execute('''
        INSERT INTO public."ProgramAreaDivisions"(
        programareaid, name, isactive, created_at, createdby, issection)
        VALUES ((select programareaid from public."ProgramAreas" where iaocode = 'MCM'), \'Deputy Minister’s Office\', true, now(), 'System', false);
    ''')

    op.execute('''
        INSERT INTO public."ProgramAreaDivisions"(
        programareaid, name, isactive, created_at, createdby, issection)
        VALUES ((select programareaid from public."ProgramAreas" where iaocode = 'ECS'), \'Deputy Minister’s Office\', true, now(), 'System', false);
    ''')

    op.execute('''
        INSERT INTO public."ProgramAreaDivisions"(
        programareaid, name, isactive, created_at, createdby, issection)
        VALUES ((select programareaid from public."ProgramAreas" where iaocode = 'INF'), \'Deputy Minister’s Office\', true, now(), 'System', false);
    ''')


def downgrade():
    op.execute('''
        delete from public."FOIRequestTeams" where 
        programareaid in (select programareaid from public."ProgramAreas" where iaocode in ('MCM', 'ECS', 'INF'));commit;
    ''')

    op.execute('''
        delete from public."ProgramAreaDivisions" where 
        programareaid in (select programareaid from public."ProgramAreas" where iaocode in ('MCM', 'ECS', 'INF'));commit;
    ''')

    op.execute('''
        delete from public."ProgramAreas" where 
        iaocode in ('MCM', 'ECS', 'INF');commit;
    ''')

    op.execute('''
        delete from public."OperatingTeams" where 
        name in ('MCM Ministry Team', 'ECS Ministry Team', 'INF Ministry Team');commit;
    ''')

    op.execute('''
        UPDATE public."ProgramAreas"
        SET name='Ministry of Housing'
        WHERE iaocode='HSG';commit;
    ''')
    op.execute('''
        UPDATE public."ProgramAreas"
        SET name='Ministry of Environment and Climate Change Strategy'
        WHERE iaocode='MOE';commit;
    ''')
    op.execute('''
        UPDATE public."ProgramAreas"
        SET name='Ministry of Transportation and Infrastructure'
        WHERE bcgovcode='TRA';commit;
    ''')

    
