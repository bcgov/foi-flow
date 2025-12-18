"""empty message

Revision ID: 4366139834ac
Revises: 496b6f8ec82b
Create Date: 2022-12-30 11:33:56.535066

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4366139834ac'
down_revision = '496b6f8ec82b'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby) VALUES ((select programareaid from public."ProgramAreas" where iaocode=\'PSE\'), \'Deputy Minister’s Office\', true, now(), \'system\');commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby) VALUES ((select programareaid from public."ProgramAreas" where iaocode=\'PSE\'), \'Minister’s Office\', true, now(), \'system\');commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby) VALUES ((select programareaid from public."ProgramAreas" where iaocode=\'PSE\'), \'Finance, Technology & Management Services\', true, now(), \'system\');commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby) VALUES ((select programareaid from public."ProgramAreas" where iaocode=\'PSE\'), \'Governance & Corporate Planning\', true, now(), \'system\');commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby) VALUES ((select programareaid from public."ProgramAreas" where iaocode=\'PSE\'), \'Post-Secondary Policy & Programs\', true, now(), \'system\');commit;')    
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby) VALUES ((select programareaid from public."ProgramAreas" where iaocode=\'PSE\'), \'Workforce Development & Skills Training\', true, now(), \'system\');commit;')


def downgrade():
    op.execute('delete from public."ProgramAreaDivisions" WHERE name in (\'Deputy Minister’s Office\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'PSE\');commit;')
    op.execute('delete from public."ProgramAreaDivisions" WHERE name in (\'Minister’s Office\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'PSE\');commit;')
    op.execute('delete from public."ProgramAreaDivisions" WHERE name in (\'Finance, Technology & Management Services\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'PSE\');commit;')
    op.execute('delete from public."ProgramAreaDivisions" WHERE name in (\'Governance & Corporate Planning\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'PSE\');commit;')
    op.execute('delete from public."ProgramAreaDivisions" WHERE name in (\'Post-Secondary Policy & Programs\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'PSE\');commit;')
    op.execute('delete from public."ProgramAreaDivisions" WHERE name in (\'Workforce Development & Skills Training\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'PSE\');commit;')
