"""empty message

Revision ID: 40dae8cc58cb
Revises: 0c235948c759
Create Date: 2022-05-03 11:53:33.379225

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import column, table
from sqlalchemy.sql.sqltypes import Boolean, String


# revision identifiers, used by Alembic.
revision = '40dae8cc58cb'
down_revision = '0c235948c759'
branch_labels = None
depends_on = None


def upgrade():

    op.execute('Update public."OperatingTeams" set name = \'AGR Ministry Team\', description = \'AGR Ministry Team\' where name = \'AFF Ministry Team\';')
    op.execute('Update public."OperatingTeams" set name = \'EDU Ministry Team\', description = \'EDU Ministry Team\' where name = \'EDUC Ministry Team\';')
    op.execute('Update public."OperatingTeams" set name = \'FOR Ministry Team\', description = \'FOR Ministry Team\' where name = \'FLNR Ministry Team\';')
    op.execute('INSERT INTO public."OperatingTeams"(name, description, isactive, type) VALUES (\'DAS Ministry Team\', \'DAS Ministry Team\', True, \'ministry\');commit;')
    op.execute('INSERT INTO public."OperatingTeams"(name, description, isactive, type) VALUES (\'LWR Ministry Team\', \'LWR Ministry Team\', True, \'ministry\');commit;')  
    

def downgrade():

    op.execute('Update public."OperatingTeams" set name = \'AFF Ministry Team\', description = \'AFF Ministry Team\' where name = \'AGR Ministry Team\';')
    op.execute('Update public."OperatingTeams" set name = \'EDUC Ministry Team\', description = \'EDUC Ministry Team\' where name = \'EDU Ministry Team\';')
    op.execute('Update public."OperatingTeams" set name = \'FOR Ministry Team\', description = \'FOR Ministry Team\' where name = \'FLNR Ministry Team\';')
    op.execute('DELETE FROM public."OperatingTeams" WHERE name in (\'DAS Ministry Team\', \'LWR Ministry Team\');commit;')    