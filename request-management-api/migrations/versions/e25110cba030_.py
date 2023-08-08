"""Updating ministry codes for MSD,GCP,OOP,CTZ

Revision ID: e25110cba030
Revises: 9ba0a7a4fe69
Create Date: 2023-08-08 14:19:03.966363

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e25110cba030'
down_revision = '9ba0a7a4fe69'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('Update public."ProgramAreas" set bcgovcode = \'MSD\' where iaocode = \'MSD\';commit;')
    op.execute('Update public."ProgramAreas" set bcgovcode = \'GCP\' where iaocode = \'GCP\';commit;')
    op.execute('Update public."ProgramAreas" set bcgovcode = \'OOP\' where iaocode = \'OOP\';commit;')
    

    op.execute('UPDATE public."OperatingTeams" SET  name=\'MSD Ministry Team\', description=\'MSD Ministry Team\' WHERE name =\'SDPR Ministry Team\';commit;')  
    op.execute('UPDATE public."OperatingTeams" SET  name=\'GCP Ministry Team\', description=\'GCP Ministry Team\' WHERE name =\'GCPE Ministry Team\';commit;') 
    op.execute('UPDATE public."OperatingTeams" SET  name=\'OOP Ministry Team\', description=\'OOP Ministry Team\' WHERE name =\'PREM Ministry Team\';commit;') 
   


def downgrade():
    op.execute('Update public."ProgramAreas" set bcgovcode = \'SDPR\' where iaocode = \'MSD\';commit;')
    op.execute('Update public."ProgramAreas" set bcgovcode = \'GCPE\' where iaocode = \'GCP\';commit;')
    op.execute('Update public."ProgramAreas" set bcgovcode = \'PREM\' where iaocode = \'OOP\';commit;')
    

    op.execute('UPDATE public."OperatingTeams" SET  name=\'SDPR Ministry Team\', description=\'SDPR Ministry Team\' WHERE name =\'SDPR Ministry Team\';commit;')  
    op.execute('UPDATE public."OperatingTeams" SET  name=\'GCPE Ministry Team\', description=\'GCPE Ministry Team\' WHERE name =\'GCPE Ministry Team\';commit;') 
    op.execute('UPDATE public."OperatingTeams" SET  name=\'PREM Ministry Team\', description=\'PREM Ministry Team\' WHERE name =\'PREM Ministry Team\';commit;') 
   
