"""empty message

Revision ID: ee6a05e2f5be
Revises: 7d58a339ff56
Create Date: 2023-01-12 16:40:03.550881

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ee6a05e2f5be'
down_revision = '7d58a339ff56'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby,sortorder) VALUES ((select programareaid from public."ProgramAreas" where iaocode=\'TRA\'), \'Headquarters\', true, now(), \'system\',7);commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby,sortorder) VALUES ((select programareaid from public."ProgramAreas" where iaocode=\'TRA\'), \'Commercial Vehicle Safety & Enforcement\', true, now(), \'system\',11);commit;')
    op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby,sortorder) VALUES ((select programareaid from public."ProgramAreas" where iaocode=\'TRA\'), \'Passenger Transportation Branch\', true, now(), \'system\',12);commit;')

    op.execute('UPDATE public."ProgramAreaDivisions" set SORTORDER = 1 WHERE name in (\'Deputy Minister’s Office\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'TRA\');commit;')
    op.execute('UPDATE public."ProgramAreaDivisions" set SORTORDER = 2 WHERE name in (\'Minister’s Office\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'TRA\');commit;')
    op.execute('UPDATE public."ProgramAreaDivisions" set SORTORDER = 3 WHERE name in (\'Minister of State\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'TRA\');commit;')
    op.execute('UPDATE public."ProgramAreaDivisions" set SORTORDER = 4 WHERE name in (\'Corporate Writing Services\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'TRA\');commit;')
    op.execute('UPDATE public."ProgramAreaDivisions" set SORTORDER = 5 WHERE name in (\'Finance & Risk Management Division\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'TRA\');commit;')
    op.execute('UPDATE public."ProgramAreaDivisions" set SORTORDER = 6 WHERE name in (\'Highways & Regional Services Division\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'TRA\');commit;')
    op.execute('UPDATE public."ProgramAreaDivisions" set SORTORDER = 8 WHERE name in (\'Northern Region\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'TRA\');commit;')
    op.execute('UPDATE public."ProgramAreaDivisions" set SORTORDER = 9 WHERE name in (\'South Coast Region\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'TRA\');commit;')
    op.execute('UPDATE public."ProgramAreaDivisions" set SORTORDER = 10 WHERE name in (\'Southern Interior Region\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'TRA\');commit;')
    op.execute('UPDATE public."ProgramAreaDivisions" set SORTORDER = 13 WHERE name in (\'Integrated Transportation & Infrastructure Services Division\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'TRA\');commit;')
    op.execute('UPDATE public."ProgramAreaDivisions" set SORTORDER = 14 WHERE name in (\'Policy, Programs, & Partnerships Division\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'TRA\');commit;')
    op.execute('UPDATE public."ProgramAreaDivisions" set SORTORDER = 15 WHERE name in (\'Strategic & Corporate Priorities Division\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'TRA\');commit;')
    op.execute('UPDATE public."ProgramAreaDivisions" set SORTORDER = 16 WHERE name in (\'BC Railway Company\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'TRA\');commit;')
    op.execute('UPDATE public."ProgramAreaDivisions" set SORTORDER = 17 WHERE name in (\'BC Transit\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'TRA\');commit;')
    op.execute('UPDATE public."ProgramAreaDivisions" set SORTORDER = 18 WHERE name in (\'BC Transportation Finance Authority\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'TRA\');commit;')
    op.execute('UPDATE public."ProgramAreaDivisions" set SORTORDER = 19 WHERE name in (\'Transportation Investment Company\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'TRA\');commit;')



def downgrade():
    op.execute('delete from public."ProgramAreaDivisions" WHERE name in (\'Headquarters\',\'Commercial Vehicle Safety & Enforcement\',\'Passenger Transportation Branch\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'TRA\');commit;')
    
    op.execute('UPDATE public."ProgramAreaDivisions" set SORTORDER = NULL WHERE name in (\'Deputy Minister’s Office\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'TRA\');commit;')
    op.execute('UPDATE public."ProgramAreaDivisions" set SORTORDER = NULL WHERE name in (\'Minister’s Office\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'TRA\');commit;')
    op.execute('UPDATE public."ProgramAreaDivisions" set SORTORDER = NULL WHERE name in (\'Minister of State\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'TRA\');commit;')
    op.execute('UPDATE public."ProgramAreaDivisions" set SORTORDER = NULL WHERE name in (\'Corporate Writing Services\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'TRA\');commit;')
    op.execute('UPDATE public."ProgramAreaDivisions" set SORTORDER = NULL WHERE name in (\'Finance & Risk Management Division\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'TRA\');commit;')
    op.execute('UPDATE public."ProgramAreaDivisions" set SORTORDER = NULL WHERE name in (\'Highways & Regional Services Division\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'TRA\');commit;')
    op.execute('UPDATE public."ProgramAreaDivisions" set SORTORDER = NULL WHERE name in (\'Northern Region\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'TRA\');commit;')
    op.execute('UPDATE public."ProgramAreaDivisions" set SORTORDER = NULL WHERE name in (\'South Coast Region\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'TRA\');commit;')
    op.execute('UPDATE public."ProgramAreaDivisions" set SORTORDER = NULL WHERE name in (\'Southern Interior Region\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'TRA\');commit;')
    op.execute('UPDATE public."ProgramAreaDivisions" set SORTORDER = NULL WHERE name in (\'Integrated Transportation & Infrastructure Services Division\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'TRA\');commit;')
    op.execute('UPDATE public."ProgramAreaDivisions" set SORTORDER = NULL WHERE name in (\'Policy, Programs, & Partnerships Division\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'TRA\');commit;')
    op.execute('UPDATE public."ProgramAreaDivisions" set SORTORDER = NULL WHERE name in (\'Strategic & Corporate Priorities Division\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'TRA\');commit;')
    op.execute('UPDATE public."ProgramAreaDivisions" set SORTORDER = NULL WHERE name in (\'BC Railway Company\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'TRA\');commit;')
    op.execute('UPDATE public."ProgramAreaDivisions" set SORTORDER = NULL WHERE name in (\'BC Transit\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'TRA\');commit;')
    op.execute('UPDATE public."ProgramAreaDivisions" set SORTORDER = NULL WHERE name in (\'BC Transportation Finance Authority\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'TRA\');commit;')
    op.execute('UPDATE public."ProgramAreaDivisions" set SORTORDER = NULL WHERE name in (\'Transportation Investment Company\') and programareaid = (select programareaid from public."ProgramAreas" where iaocode=\'TRA\');commit;')