"""empty message

Revision ID: a9bc29e088d2
Revises: dfc4fb8d79b9
Create Date: 2023-01-04 16:33:12.773767

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a9bc29e088d2'
down_revision = 'dfc4fb8d79b9'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby) VALUES ((select programareaid from public."ProgramAreas" where iaocode=\'ECC\'), \'Deputy Minister’s Office\', true, now(), \'system\');commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby) VALUES ((select programareaid from public."ProgramAreas" where iaocode=\'ECC\'), \'Minister’s Office\', true, now(), \'system\');commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby) VALUES ((select programareaid from public."ProgramAreas" where iaocode=\'ECC\'), \'Education Programs\', true, now(), \'system\');commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby) VALUES ((select programareaid from public."ProgramAreas" where iaocode=\'ECC\'), \'Learning\', true, now(), \'system\');commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby) VALUES ((select programareaid from public."ProgramAreas" where iaocode=\'ECC\'), \'Governance & Analytics\', true, now(), \'system\');commit;')    
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby) VALUES ((select programareaid from public."ProgramAreas" where iaocode=\'ECC\'), \'Resource Management\', true, now(), \'system\');commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby) VALUES ((select programareaid from public."ProgramAreas" where iaocode=\'ECC\'), \'Services & Technology\', true, now(), \'system\');commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby) VALUES ((select programareaid from public."ProgramAreas" where iaocode=\'ECC\'), \'Child Care\', true, now(), \'system\');commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby) VALUES ((select programareaid from public."ProgramAreas" where iaocode=\'ECC\'), \'Minister of State\', true, now(), \'system\');commit;')


def downgrade():
    op.execute('delete from public."ProgramAreaDivisions" WHERE name in (\'Deputy Minister’s Office\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'ECC\');commit;')
    op.execute('delete from public."ProgramAreaDivisions" WHERE name in (\'Minister’s Office\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'ECC\');commit;')
    op.execute('delete from public."ProgramAreaDivisions" WHERE name in (\'Education Programs\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'ECC\');commit;')
    op.execute('delete from public."ProgramAreaDivisions" WHERE name in (\'Learning\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'ECC\');commit;')
    op.execute('delete from public."ProgramAreaDivisions" WHERE name in (\'Governance & Analytics\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'ECC\');commit;')
    op.execute('delete from public."ProgramAreaDivisions" WHERE name in (\'Resource Management\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'ECC\');commit;')
    op.execute('delete from public."ProgramAreaDivisions" WHERE name in (\'Services & Technology\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'ECC\');commit;')
    op.execute('delete from public."ProgramAreaDivisions" WHERE name in (\'Child Care\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'ECC\');commit;')
    op.execute('delete from public."ProgramAreaDivisions" WHERE name in (\'Minister of State\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'ECC\');commit;')
