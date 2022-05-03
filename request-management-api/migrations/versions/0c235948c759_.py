"""empty message

Revision ID: 0c235948c759
Revises: 688bd7c77b01
Create Date: 2022-05-02 13:00:55.126582

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0c235948c759'
down_revision = '688bd7c77b01'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('Update public."ProgramAreas" set bcgovcode = \'EDU\', name = \'EDU Ministry Team\' where iaocode = \'EDU\';')
    op.execute('Update public."ProgramAreas" set bcgovcode = \'AGR\', name = \'AGR Ministry Team\' where iaocode = \'AGR\';')
    op.execute('Update public."ProgramAreas" set bcgovcode = \'FOR\', iaocode = \'FOR\', name = \'FOR Ministry Team\' where iaocode = \'FNR\';')
    op.execute('INSERT INTO public."ProgramAreas"(name, type, isactive, bcgovcode, iaocode) VALUES (\'Lands, Water and Resource Stewardship\', \'BC GOV Ministry\', True, \'LWR\', \'LWR\');commit;')
    op.execute('INSERT INTO public."ProgramAreas"(name, type, isactive, bcgovcode, iaocode)	VALUES (\'Declaration Act Secretariat\', \'Other\', True, \'DAS\', \'DAS\');commit;')
    
def downgrade():
    op.execute('Update public."ProgramAreas" set bcgovcode = \'EDUC\', name = \'EDUC Ministry Team\' where iaocode = \'EDU\';')
    op.execute('Update public."ProgramAreas" set bcgovcode = \'AFF\', name = \'AFF Ministry Team\' where iaocode = \'AGR\';')
    op.execute('Update public."ProgramAreas" set bcgovcode = \'FLNR\', iaocode = \'FNR\', name = \'FLNR Ministry Team\' where iaocode = \'FOR\';')
    op.execute('DELETE FROM public."ProgramAreas" WHERE iaocode in (\'LWR\', \'DAS\');commit;')