"""empty message

Revision ID: 5a5705dc3915
Revises: 898ea7d002de
Create Date: 2023-01-03 14:03:44.065811

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5a5705dc3915'
down_revision = '898ea7d002de'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby) VALUES ((select programareaid from public."ProgramAreas" where iaocode=\'TRA\'), \'Deputy Minister’s Office\', true, now(), \'system\');commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby) VALUES ((select programareaid from public."ProgramAreas" where iaocode=\'TRA\'), \'Minister’s Office\', true, now(), \'system\');commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby) VALUES ((select programareaid from public."ProgramAreas" where iaocode=\'TRA\'), \'Minister of State\', true, now(), \'system\');commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby) VALUES ((select programareaid from public."ProgramAreas" where iaocode=\'TRA\'), \'Corporate Writing Services\', true, now(), \'system\');commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby) VALUES ((select programareaid from public."ProgramAreas" where iaocode=\'TRA\'), \'Finance & Risk Management Division\', true, now(), \'system\');commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby) VALUES ((select programareaid from public."ProgramAreas" where iaocode=\'TRA\'), \'Highways & Regional Services Division\', true, now(), \'system\');commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby) VALUES ((select programareaid from public."ProgramAreas" where iaocode=\'TRA\'), \'Northern Region\', true, now(), \'system\');commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby) VALUES ((select programareaid from public."ProgramAreas" where iaocode=\'TRA\'), \'South Coast Region\', true, now(), \'system\');commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby) VALUES ((select programareaid from public."ProgramAreas" where iaocode=\'TRA\'), \'Southern Interior Region\', true, now(), \'system\');commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby) VALUES ((select programareaid from public."ProgramAreas" where iaocode=\'TRA\'), \'Integrated Transportation & Infrastructure Services Division\', true, now(), \'system\');commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby) VALUES ((select programareaid from public."ProgramAreas" where iaocode=\'TRA\'), \'Policy, Programs, & Partnerships Division\', true, now(), \'system\');commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby) VALUES ((select programareaid from public."ProgramAreas" where iaocode=\'TRA\'), \'Strategic & Corporate Priorities Division\', true, now(), \'system\');commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby) VALUES ((select programareaid from public."ProgramAreas" where iaocode=\'TRA\'), \'BC Railway Company\', true, now(), \'system\');commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby) VALUES ((select programareaid from public."ProgramAreas" where iaocode=\'TRA\'), \'BC Transit\', true, now(), \'system\');commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby) VALUES ((select programareaid from public."ProgramAreas" where iaocode=\'TRA\'), \'BC Transportation Finance Authority\', true, now(), \'system\');commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby) VALUES ((select programareaid from public."ProgramAreas" where iaocode=\'TRA\'), \'Transportation Investment Company\', true, now(), \'system\');commit;')
    


def downgrade():
    op.execute('delete from public."ProgramAreaDivisions" WHERE name in (\'Deputy Minister’s Office\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'TRA\');commit;')
    op.execute('delete from public."ProgramAreaDivisions" WHERE name in (\'Minister’s Office\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'TRA\');commit;')
    op.execute('delete from public."ProgramAreaDivisions" WHERE name in (\'Minister of State\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'TRA\');commit;')
    op.execute('delete from public."ProgramAreaDivisions" WHERE name in (\'Corporate Writing Services\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'TRA\');commit;')
    op.execute('delete from public."ProgramAreaDivisions" WHERE name in (\'Finance & Risk Management Division\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'TRA\');commit;')
    op.execute('delete from public."ProgramAreaDivisions" WHERE name in (\'Highways & Regional Services Division\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'TRA\');commit;')
    op.execute('delete from public."ProgramAreaDivisions" WHERE name in (\'Northern Region\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'TRA\');commit;')
    op.execute('delete from public."ProgramAreaDivisions" WHERE name in (\'South Coast Region\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'TRA\');commit;')
    op.execute('delete from public."ProgramAreaDivisions" WHERE name in (\'Southern Interior Region\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'TRA\');commit;')
    op.execute('delete from public."ProgramAreaDivisions" WHERE name in (\'Integrated Transportation & Infrastructure Services Division\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'TRA\');commit;')
    op.execute('delete from public."ProgramAreaDivisions" WHERE name in (\'Policy, Programs, & Partnerships Division\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'TRA\');commit;')
    op.execute('delete from public."ProgramAreaDivisions" WHERE name in (\'Strategic & Corporate Priorities Division\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'TRA\');commit;')
    op.execute('delete from public."ProgramAreaDivisions" WHERE name in (\'BC Railway Company\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'TRA\');commit;')
    op.execute('delete from public."ProgramAreaDivisions" WHERE name in (\'BC Transit\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'TRA\');commit;')
    op.execute('delete from public."ProgramAreaDivisions" WHERE name in (\'BC Transportation Finance Authority\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'TRA\');commit;')
    op.execute('delete from public."ProgramAreaDivisions" WHERE name in (\'Transportation Investment Company\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'TRA\');commit;')
