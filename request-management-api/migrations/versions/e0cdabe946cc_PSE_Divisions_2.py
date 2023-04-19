"""PSE additional 2 divisions

Revision ID: e0cdabe946cc
Revises: 93566cbde728
Create Date: 2023-03-13 12:14:05.550786

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e0cdabe946cc'
down_revision = '93566cbde728'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby) VALUES ((select programareaid from public."ProgramAreas" where iaocode=\'PSE\'), \'Final Sign-Off\', true, now(), \'system\');commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby) VALUES ((select programareaid from public."ProgramAreas" where iaocode=\'PSE\'), \'Corporate Planning & Projects - Director\', true, now(), \'system\');commit;')


def downgrade():op.execute('delete from public."ProgramAreaDivisions" WHERE name in (\'Final Sign-Off\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'PSE\');commit;')
def downgrade():op.execute('delete from public."ProgramAreaDivisions" WHERE name in (\'Corporate Planning & Projects - Director\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'PSE\');commit;')