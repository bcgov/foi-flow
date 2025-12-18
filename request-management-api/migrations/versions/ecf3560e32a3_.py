"""empty message

Revision ID: ecf3560e32a3
Revises: 3084c5961187
Create Date: 2022-05-25 16:06:11.891009

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ecf3560e32a3'
down_revision = '3084c5961187'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('UPDATE public."ProgramAreaDivisions" SET isactive=false WHERE name in (\'Employers’ Advisor’s Office\', \'Employment Standards\', \'Policy and Legislation\', \'Workers’ Advisor’s Office\', \'Labour\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'LBR\');commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby) VALUES ((select programareaid from public."ProgramAreas" where iaocode=\'LBR\'), \'Assistant Deputy Minister’s Office\', true, now(), \'system\');commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby) VALUES ((select programareaid from public."ProgramAreas" where iaocode=\'EDU\'), \'Child Care\', true, now(), \'system\');commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby) VALUES ((select programareaid from public."ProgramAreas" where iaocode=\'EDU\'), \'Minister of State\', true, now(), \'system\');commit;')

def downgrade():
    op.execute('UPDATE public."ProgramAreaDivisions" SET isactive=true WHERE name in (\'Employers’ Advisor’s Office\', \'Employment Standards\', \'Policy and Legislation\', \'Workers’ Advisor’s Office\', \'Labour\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'LBR\');commit;')
    op.execute('delete from public."ProgramAreaDivisions" WHERE name in (\'Assistant Deputy Minister’s Office\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'LBR\');commit;')
    op.execute('delete from public."ProgramAreaDivisions" WHERE name in (\'Child Care\',\'Minister of State\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'EDU\');commit;')