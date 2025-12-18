"""empty message

Revision ID: 5a4ab3aa3520
Revises: 5c1426afacb8
Create Date: 2023-01-05 16:46:52.214428

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5a4ab3aa3520'
down_revision = '5c1426afacb8'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('INSERT INTO public."OperatingTeams"(name, description, isactive, type) VALUES (\'JED Ministry Team\', \'JED Ministry Team\', True, \'ministry\');commit;')  


def downgrade():
    op.execute('DELETE FROM public."OperatingTeams" WHERE name in (\'JED Ministry Team\');commit;')