"""empty message

Revision ID: be8612ebd00e
Revises: 7b9559122a3f
Create Date: 2023-02-15 17:36:28.357264

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'be8612ebd00e'
down_revision = '7b9559122a3f'
branch_labels = None
depends_on = None


def upgrade():
    # MAG
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby,sortorder) VALUES ((select programareaid from public."ProgramAreas" where isactive = true and iaocode=\'MAG\'), \'Minister’s Office\', true, now(), \'system\',1);commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby,sortorder) VALUES ((select programareaid from public."ProgramAreas" where isactive = true and iaocode=\'MAG\'), \'Deputy Attorney General\', true, now(), \'system\',2);commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby,sortorder) VALUES ((select programareaid from public."ProgramAreas" where isactive = true and iaocode=\'MAG\'), \'Corporate Management Services Branch\', true, now(), \'system\',3);commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby,sortorder) VALUES ((select programareaid from public."ProgramAreas" where isactive = true and iaocode=\'MAG\'), \'Information Systems Branch\', true, now(), \'system\',4);commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby,sortorder) VALUES ((select programareaid from public."ProgramAreas" where isactive = true and iaocode=\'MAG\'), \'Multiculturalism\', true, now(), \'system\',5);commit;')    
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby,sortorder) VALUES ((select programareaid from public."ProgramAreas" where isactive = true and iaocode=\'MAG\'), \'Court Services Branch\', true, now(), \'system\',6);commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby,sortorder) VALUES ((select programareaid from public."ProgramAreas" where isactive = true and iaocode=\'MAG\'), \'Legal Services Branch\', true, now(), \'system\',7);commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby,sortorder) VALUES ((select programareaid from public."ProgramAreas" where isactive = true and iaocode=\'MAG\'), \'Justice Services Branch\', true, now(), \'system\',8);commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby,sortorder) VALUES ((select programareaid from public."ProgramAreas" where isactive = true and iaocode=\'MAG\'), \'Investigation & Standards Office\', true, now(), \'system\',9);commit;')

    #PSS
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby,sortorder) VALUES ((select programareaid from public."ProgramAreas" where isactive = true and iaocode=\'PSS\'), \'Minister’s Office\', true, now(), \'system\',1);commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby,sortorder) VALUES ((select programareaid from public."ProgramAreas" where isactive = true and iaocode=\'PSS\'), \'Deputy Solicitor General\', true, now(), \'system\',2);commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby,sortorder) VALUES ((select programareaid from public."ProgramAreas" where isactive = true and iaocode=\'PSS\'), \'RoadSafety BC\', true, now(), \'system\',3);commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby,sortorder) VALUES ((select programareaid from public."ProgramAreas" where isactive = true and iaocode=\'PSS\'), \'Corporate Management Services Branch\', true, now(), \'system\',4);commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby,sortorder) VALUES ((select programareaid from public."ProgramAreas" where isactive = true and iaocode=\'PSS\'), \'Information Systems Branch\', true, now(), \'system\',5);commit;')    
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby,sortorder) VALUES ((select programareaid from public."ProgramAreas" where isactive = true and iaocode=\'PSS\'), \'Cannabis, Customer Protection and Corporate Policy\', true, now(), \'system\',6);commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby,sortorder) VALUES ((select programareaid from public."ProgramAreas" where isactive = true and iaocode=\'PSS\'), \'Community Safety and Crime Prevention\', true, now(), \'system\',7);commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby,sortorder) VALUES ((select programareaid from public."ProgramAreas" where isactive = true and iaocode=\'PSS\'), \'Victim Services and Crime Prevention\', true, now(), \'system\',8);commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby,sortorder) VALUES ((select programareaid from public."ProgramAreas" where isactive = true and iaocode=\'PSS\'), \'Civil Forfeiture Office\', true, now(), \'system\',9);commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby,sortorder) VALUES ((select programareaid from public."ProgramAreas" where isactive = true and iaocode=\'PSS\'), \'Liquor and Cannabis Regulation Branch\', true, now(), \'system\',10);commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby,sortorder) VALUES ((select programareaid from public."ProgramAreas" where isactive = true and iaocode=\'PSS\'), \'Policing and Security Branch\', true, now(), \'system\',11);commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby,sortorder) VALUES ((select programareaid from public."ProgramAreas" where isactive = true and iaocode=\'PSS\'), \'Gaming Enforcement and Policy Branch\', true, now(), \'system\',12);commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby,sortorder) VALUES ((select programareaid from public."ProgramAreas" where isactive = true and iaocode=\'PSS\'), \'Office of the Fire Commissioner\', true, now(), \'system\',13);commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby,sortorder) VALUES ((select programareaid from public."ProgramAreas" where isactive = true and iaocode=\'PSS\'), \'Corrections Branch\', true, now(), \'system\',14);commit;')

    # HSG
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby,sortorder) VALUES ((select programareaid from public."ProgramAreas" where isactive = true and iaocode=\'HSG\'), \'Minister’s Office\', true, now(), \'system\',1);commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby,sortorder) VALUES ((select programareaid from public."ProgramAreas" where isactive = true and iaocode=\'HSG\'), \'Deputy Minister’s Office\', true, now(), \'system\',2);commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby,sortorder) VALUES ((select programareaid from public."ProgramAreas" where isactive = true and iaocode=\'HSG\'), \'Housing and Land Use Policy\', true, now(), \'system\',3);commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby,sortorder) VALUES ((select programareaid from public."ProgramAreas" where isactive = true and iaocode=\'HSG\'), \'Strategy, Governance and Accountability\', true, now(), \'system\',4);commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby,sortorder) VALUES ((select programareaid from public."ProgramAreas" where isactive = true and iaocode=\'HSG\'), \'Homelessness, Partnership and Housing Support\', true, now(), \'system\',5);commit;')    
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby,sortorder) VALUES ((select programareaid from public."ProgramAreas" where isactive = true and iaocode=\'HSG\'), \'Residential Tenancy Branch\', true, now(), \'system\',6);commit;')

    #EMC
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby,sortorder) VALUES ((select programareaid from public."ProgramAreas" where isactive = true and iaocode=\'EMC\'), \'Minister’s Office\', true, now(), \'system\',1);commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby,sortorder) VALUES ((select programareaid from public."ProgramAreas" where isactive = true and iaocode=\'EMC\'), \'Deputy Minister’s Office\', true, now(), \'system\',2);commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby,sortorder) VALUES ((select programareaid from public."ProgramAreas" where isactive = true and iaocode=\'EMC\'), \'Associate Deputy Minister’s Office\', true, now(), \'system\',3);commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby,sortorder) VALUES ((select programareaid from public."ProgramAreas" where isactive = true and iaocode=\'EMC\'), \'Executive Operations\', true, now(), \'system\',4);commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby,sortorder) VALUES ((select programareaid from public."ProgramAreas" where isactive = true and iaocode=\'EMC\'), \'ADMO, Regional Operations\', true, now(), \'system\',5);commit;')    
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby,sortorder) VALUES ((select programareaid from public."ProgramAreas" where isactive = true and iaocode=\'EMC\'), \'ADMO, Disaster Risk Management\', true, now(), \'system\',6);commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby,sortorder) VALUES ((select programareaid from public."ProgramAreas" where isactive = true and iaocode=\'EMC\'), \'ADMO, Disaster Recovery\', true, now(), \'system\',7);commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby,sortorder) VALUES ((select programareaid from public."ProgramAreas" where isactive = true and iaocode=\'EMC\'), \'ADMO, Corporate Support Services\', true, now(), \'system\',8);commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby,sortorder) VALUES ((select programareaid from public."ProgramAreas" where isactive = true and iaocode=\'EMC\'), \'Regional Ops Regions\', true, now(), \'system\',9);commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby,sortorder) VALUES ((select programareaid from public."ProgramAreas" where isactive = true and iaocode=\'EMC\'), \'Regional Ops Programs\', true, now(), \'system\',10);commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby,sortorder) VALUES ((select programareaid from public."ProgramAreas" where isactive = true and iaocode=\'EMC\'), \'Strategic Partnerships\', true, now(), \'system\',11);commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby,sortorder) VALUES ((select programareaid from public."ProgramAreas" where isactive = true and iaocode=\'EMC\'), \'Policy, Leg, and Enforcement\', true, now(), \'system\',12);commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby,sortorder) VALUES ((select programareaid from public."ProgramAreas" where isactive = true and iaocode=\'EMC\'), \'Corp. Planning and Priorities\', true, now(), \'system\',13);commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby,sortorder) VALUES ((select programareaid from public."ProgramAreas" where isactive = true and iaocode=\'EMC\'), \'Recovery and Resiliency Sec.\', true, now(), \'system\',14);commit;')

    # COR
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby,sortorder) VALUES ((select programareaid from public."ProgramAreas" where isactive = true and iaocode=\'COR\'), \'Corrections\', true, now(), \'system\',1);commit;')


def downgrade():
    op.execute('delete from public."ProgramAreaDivisions" WHERE programareaid in (SELECT programareaid FROM "ProgramAreas" WHERE iaocode in(\'HSG\',\'EMC\',\'PSS\',\'MAG\',\'COR\') and isactive = true)')
