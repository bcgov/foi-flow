"""empty message

Revision ID: efd4e8f20384
Revises: 5a5705dc3915
Create Date: 2023-01-03 14:33:28.593654

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'efd4e8f20384'
down_revision = '5a5705dc3915'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby) VALUES ((select programareaid from public."ProgramAreas" where iaocode=\'PSA\'), \'Service Operations\', true, now(), \'system\');commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby) VALUES ((select programareaid from public."ProgramAreas" where iaocode=\'PSA\'), \'Employee Relations\', true, now(), \'system\');commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby) VALUES ((select programareaid from public."ProgramAreas" where iaocode=\'PSA\'), \'Business Performance Division\', true, now(), \'system\');commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby) VALUES ((select programareaid from public."ProgramAreas" where iaocode=\'PSA\'), \'Business Intelligence/Corporate Reporting\', true, now(), \'system\');commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby) VALUES ((select programareaid from public."ProgramAreas" where iaocode=\'PSA\'), \'Custom Research\', true, now(), \'system\');commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby) VALUES ((select programareaid from public."ProgramAreas" where iaocode=\'PSA\'), \'Financial Management Office\', true, now(), \'system\');commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby) VALUES ((select programareaid from public."ProgramAreas" where iaocode=\'PSA\'), \'Telus Sourcing Solutions\', true, now(), \'system\');commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby) VALUES ((select programareaid from public."ProgramAreas" where iaocode=\'PSA\'), \'Deputy Minister’s Office\', true, now(), \'system\');commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby) VALUES ((select programareaid from public."ProgramAreas" where iaocode=\'PSA\'), \'People and Organizational Development\', true, now(), \'system\');commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby) VALUES ((select programareaid from public."ProgramAreas" where iaocode=\'PSA\'), \'Total Compensation and Benefits\', true, now(), \'system\');commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby) VALUES ((select programareaid from public."ProgramAreas" where iaocode=\'PSA\'), \'Policy, Innovation & Engagement\', true, now(), \'system\');commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby) VALUES ((select programareaid from public."ProgramAreas" where iaocode=\'PSA\'), \'Integrated HR Branch\', true, now(), \'system\');commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby) VALUES ((select programareaid from public."ProgramAreas" where iaocode=\'PSA\'), \'Occupational Health & Rehab\', true, now(), \'system\');commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby) VALUES ((select programareaid from public."ProgramAreas" where iaocode=\'PSA\'), \'Disability Plan Performance\', true, now(), \'system\');commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby) VALUES ((select programareaid from public."ProgramAreas" where iaocode=\'PSA\'), \'Corporate Health Program\', true, now(), \'system\');commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby) VALUES ((select programareaid from public."ProgramAreas" where iaocode=\'PSA\'), \'Safety Advisory Services\', true, now(), \'system\');commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby) VALUES ((select programareaid from public."ProgramAreas" where iaocode=\'PSA\'), \'Workplace Health Planning\', true, now(), \'system\');commit;')


def downgrade():
    op.execute('delete from public."ProgramAreaDivisions" WHERE name in (\'Deputy Minister’s Office\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'PSA\');commit;')
    op.execute('delete from public."ProgramAreaDivisions" WHERE name in (\'Service Operations\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'PSA\');commit;')
    op.execute('delete from public."ProgramAreaDivisions" WHERE name in (\'Employee Relations\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'PSA\');commit;')
    op.execute('delete from public."ProgramAreaDivisions" WHERE name in (\'Business Performance Division\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'PSA\');commit;')
    op.execute('delete from public."ProgramAreaDivisions" WHERE name in (\'Business Intelligence/Corporate Reporting\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'PSA\');commit;')
    op.execute('delete from public."ProgramAreaDivisions" WHERE name in (\'Custom Research\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'PSA\');commit;')
    op.execute('delete from public."ProgramAreaDivisions" WHERE name in (\'Financial Management Office\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'PSA\');commit;')
    op.execute('delete from public."ProgramAreaDivisions" WHERE name in (\'Telus Sourcing Solutions\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'PSA\');commit;')
    op.execute('delete from public."ProgramAreaDivisions" WHERE name in (\'People and Organizational Development\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'PSA\');commit;')
    op.execute('delete from public."ProgramAreaDivisions" WHERE name in (\'Total Compensation and Benefits\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'PSA\');commit;')
    op.execute('delete from public."ProgramAreaDivisions" WHERE name in (\'Policy, Innovation & Engagement\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'PSA\');commit;')
    op.execute('delete from public."ProgramAreaDivisions" WHERE name in (\'Integrated HR Branch\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'PSA\');commit;')
    op.execute('delete from public."ProgramAreaDivisions" WHERE name in (\'Occupational Health & Rehab\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'PSA\');commit;')
    op.execute('delete from public."ProgramAreaDivisions" WHERE name in (\'Disability Plan Performance\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'PSA\');commit;')
    op.execute('delete from public."ProgramAreaDivisions" WHERE name in (\'Corporate Health Program\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'PSA\');commit;')
    op.execute('delete from public."ProgramAreaDivisions" WHERE name in (\'Safety Advisory Services\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'PSA\');commit;')
    op.execute('delete from public."ProgramAreaDivisions" WHERE name in (\'Workplace Health Planning\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'PSA\');commit;')
