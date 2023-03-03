"""empty message

Revision ID: 4a8a8487692c
Revises: be8612ebd00e
Create Date: 2023-02-15 22:36:04.847492

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4a8a8487692c'
down_revision = 'be8612ebd00e'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('UPDATE public."OperatingTeams" SET  name=\'WLR Ministry Team\', description=\'WLR Ministry Team\' WHERE name =\'LWR Ministry Team\';commit;')  
    op.execute('UPDATE public."OperatingTeams" SET  name=\'EMC Ministry Team\', description=\'EMC Ministry Team\' WHERE name =\'EMBC Ministry Team\';commit;')  
    op.execute('INSERT INTO public."OperatingTeams"(name, description, isactive, type) VALUES (\'HSG Ministry Team\', \'HSG Ministry Team\', True, \'ministry\');commit;')  
    op.execute('INSERT INTO public."OperatingTeams"(name, description, isactive, type) VALUES (\'COR Ministry Team\', \'COR Ministry Team\', True, \'ministry\');commit;')  


def downgrade():
    op.execute('UPDATE public."OperatingTeams" SET  name=\'LWR Ministry Team\', description=\'LWR Ministry Team\' WHERE name =\'WLR Ministry Team\';commit;')  
    op.execute('UPDATE public."OperatingTeams" SET  name=\'EMBC Ministry Team\', description=\'EMBC Ministry Team\' WHERE name =\'EMC Ministry Team\';commit;')  
    op.execute('DELETE FROM public."OperatingTeams" WHERE name in (\'HSG Ministry Team\',\'COR Ministry Team\');commit;')
