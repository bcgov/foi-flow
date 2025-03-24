"""empty message

Revision ID: d93211421685
Revises: 7a554bfa243d
Create Date: 2025-02-10 10:45:54.921465

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd93211421685'
down_revision = '7a554bfa243d'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('Insert into public."OperatingTeams" (name, description, type, isactive) values (\'BCPS Team\', \'BCPS Team\', \'iao\', true);commit;')    

def downgrade():
    op.execute('Delete from public."OperatingTeams" where name in (\'BCPS Team\');commit;')