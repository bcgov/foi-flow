"""empty message

Revision ID: 7b9559122a3f
Revises: ef2787700a08
Create Date: 2023-02-13 14:25:37.102077

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7b9559122a3f'
down_revision = 'ef2787700a08'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('UPDATE public."ProgramAreas" set isactive=false where "ProgramAreas".iaocode =\'LWR\';commit;')
    op.execute('UPDATE public."ProgramAreas" set isactive=false where "ProgramAreas".iaocode =\'EMB\';commit;')
    op.execute('INSERT INTO public."ProgramAreas"(name, type, isactive, bcgovcode, iaocode)	VALUES (\'Ministry of Water, Land and Resource Stewardship\', \'BC GOV Ministry\', True, \'WLR\', \'WLR\');commit;')
    op.execute('INSERT INTO public."ProgramAreas"(name, type, isactive, bcgovcode, iaocode)	VALUES (\'Ministry of Emergency Management and Climate Readiness\', \'BC GOV Ministry\', True, \'EMC\', \'EMC\');commit;')
    op.execute('INSERT INTO public."ProgramAreas"(name, type, isactive, bcgovcode, iaocode)	VALUES (\'Corrections Branch\', \'BC GOV Ministry\', True, \'COR\', \'COR\');commit;')


def downgrade():
    op.execute('UPDATE public."ProgramAreas" set isactive=true where "ProgramAreas".iaocode =\'LWR\';commit;')
    op.execute('UPDATE public."ProgramAreas" set isactive=true where "ProgramAreas".iaocode =\'EMB\';commit;')
    op.execute('DELETE FROM public."ProgramAreas" WHERE iaocode in (\'WLR\',\'COR\',\'EMC\');commit;')