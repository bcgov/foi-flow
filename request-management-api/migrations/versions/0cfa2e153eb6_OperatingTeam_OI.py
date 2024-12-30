"""empty message

Revision ID: 0cfa2e153eb6
Revises: 83cfc8047acf
Create Date: 2024-12-30 14:57:11.572686

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0cfa2e153eb6'
down_revision = '83cfc8047acf'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('INSERT INTO public."OperatingTeams"(name, description, isactive, type) VALUES (\'OI Team\', \'OI Team\', True, \'iao\');commit;')  
def downgrade():
    op.execute(    op.execute('DELETE FROM public."OperatingTeams" WHERE name in (\'OI Team\');commit;'))