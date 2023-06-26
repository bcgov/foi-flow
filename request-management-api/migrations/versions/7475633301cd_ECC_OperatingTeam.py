"""empty message

Revision ID: 7475633301cd
Revises: a9bc29e088d2
Create Date: 2023-01-04 17:23:47.802701

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7475633301cd'
down_revision = 'a9bc29e088d2'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('INSERT INTO public."OperatingTeams"(name, description, isactive, type) VALUES (\'ECC Ministry Team\', \'ECC Ministry Team\', True, \'ministry\');commit;')  


def downgrade():
    op.execute('DELETE FROM public."OperatingTeams" WHERE name in (\'ECC Ministry Team\');commit;')
