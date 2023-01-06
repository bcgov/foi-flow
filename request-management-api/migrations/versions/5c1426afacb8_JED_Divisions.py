"""empty message

Revision ID: 5c1426afacb8
Revises: 0f31e19d3672
Create Date: 2023-01-05 16:27:38.658906

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5c1426afacb8'
down_revision = '0f31e19d3672'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby) VALUES ((select programareaid from public."ProgramAreas" where iaocode=\'JED\'), \'Deputy Minister’s Office\', true, now(), \'system\');commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby) VALUES ((select programareaid from public."ProgramAreas" where iaocode=\'JED\'), \'Minister’s Office\', true, now(), \'system\');commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby) VALUES ((select programareaid from public."ProgramAreas" where iaocode=\'JED\'), \'Management Services\', true, now(), \'system\');commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby) VALUES ((select programareaid from public."ProgramAreas" where iaocode=\'JED\'), \'Trade & Industry Development\', true, now(), \'system\');commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby) VALUES ((select programareaid from public."ProgramAreas" where iaocode=\'JED\'), \'Mass Timber Implementation\', true, now(), \'system\');commit;')    
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby) VALUES ((select programareaid from public."ProgramAreas" where iaocode=\'JED\'), \'Innovation, Technology & Investment Capital\', true, now(), \'system\');commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby) VALUES ((select programareaid from public."ProgramAreas" where iaocode=\'JED\'), \'Investment & Innovation\', true, now(), \'system\');commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby) VALUES ((select programareaid from public."ProgramAreas" where iaocode=\'JED\'), \'Small Business & Economic Development\', true, now(), \'system\');commit;')


def downgrade():
    op.execute('delete from public."ProgramAreaDivisions" WHERE name in (\'Deputy Minister’s Office\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'JED\');commit;')
    op.execute('delete from public."ProgramAreaDivisions" WHERE name in (\'Minister’s Office\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'JED\');commit;')
    op.execute('delete from public."ProgramAreaDivisions" WHERE name in (\'Management Services\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'JED\');commit;')
    op.execute('delete from public."ProgramAreaDivisions" WHERE name in (\'Trade & Industry Development\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'JED\');commit;')
    op.execute('delete from public."ProgramAreaDivisions" WHERE name in (\'Mass Timber Implementation\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'JED\');commit;')
    op.execute('delete from public."ProgramAreaDivisions" WHERE name in (\'Innovation, Technology & Investment Capital\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'JED\');commit;')
    op.execute('delete from public."ProgramAreaDivisions" WHERE name in (\'Investment & Innovation\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'JED\');commit;')
    op.execute('delete from public."ProgramAreaDivisions" WHERE name in (\'Small Business & Economic Development\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'JED\');commit;')
