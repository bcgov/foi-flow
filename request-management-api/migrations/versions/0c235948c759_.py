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
    op.execute('Update public."ProgramAreas" set bcgovcode = \'EDU\', name = \'Ministry of Education and Childcare\' where iaocode = \'EDU\';')
    op.execute('Update public."ProgramAreas" set bcgovcode = \'AGR\', name = \'Ministry of Agriculture and Food\' where iaocode = \'AGR\';')
    op.execute('Update public."ProgramAreas" set bcgovcode = \'FOR\', iaocode = \'FOR\', name = \'Ministry of Forests\' where iaocode = \'FNR\';')
    op.execute('INSERT INTO public."ProgramAreas"(name, type, isactive, bcgovcode, iaocode) VALUES (\'Ministry of Lands, Water and Resource Stewardship\', \'BC GOV Ministry\', True, \'LWR\', \'LWR\');commit;')
    op.execute('INSERT INTO public."ProgramAreas"(name, type, isactive, bcgovcode, iaocode)	VALUES (\'Ministry of Declaration Act Secretariat\', \'BC GOV Ministry\', True, \'DAS\', \'DAS\');commit;')
    
    op.execute('Update public."OperatingTeams" set name = \'EDU Ministry Team\', description = \'EDU Ministry Team\'  where name = \'EDUC Ministry Team\';')
    op.execute('Update public."OperatingTeams" set description = \'AGR Ministry Team\', name = \'AGR Ministry Team\' where name = \'AFF Ministry Team\';')
    op.execute('Update public."OperatingTeams" set description = \'FOR Ministry Team\', name = \'FOR Ministry Team\' where name = \'FLNR Ministry Team\';')
    op.execute('INSERT INTO public."OperatingTeams"(name, description, type, isactive) VALUES (\'LWR Ministry Team\', \'LWR Ministry Team\', \'ministry\', True);commit;')
    op.execute('INSERT INTO public."OperatingTeams"(name, description, type, isactive) VALUES (\'DAS Ministry Team\', \'DAS Ministry Team\', \'ministry\', True);commit;')

def downgrade():
    op.execute('Update public."ProgramAreas" set bcgovcode = \'EDUC\', name = \'Ministry of Education\' where iaocode = \'EDU\';')
    op.execute('Update public."ProgramAreas" set bcgovcode = \'AFF\', name = \'Ministry of Agriculture, Food and Fisheries\' where iaocode = \'AGR\';')
    op.execute('Update public."ProgramAreas" set bcgovcode = \'FLNR\', iaocode = \'FNR\', name = \'Ministry of Forests, Lands, Natural Resource Operations and Rural Development\' where iaocode = \'FOR\';')
    op.execute('DELETE FROM public."ProgramAreas" WHERE iaocode in (\'LWR\', \'DAS\');commit;')

    op.execute('Update public."OperatingTeams" set name = \'EDUC Ministry Team\', description = \'EDUC Ministry Team\'  where name = \'EDU Ministry Team\';')
    op.execute('Update public."OperatingTeams" set description = \'AFF Ministry Team\', name = \'AFF Ministry Team\' where name = \'AGR Ministry Team\';')
    op.execute('Update public."OperatingTeams" set description = \'FLNR Ministry Team\', name = \'FLNR Ministry Team\' where name = \'FOR Ministry Team\';')
    op.execute('DELETE FROM public."OperatingTeams" WHERE name in (\'LWR Ministry Team\', \'DAS Ministry Team\');commit;')