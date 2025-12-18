"""empty message

Revision ID: 4f6729690cec
Revises: 4366139834ac
Create Date: 2022-12-30 12:04:03.241910

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4f6729690cec'
down_revision = '4366139834ac'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('INSERT INTO public."OperatingTeams"(name, description, isactive, type) VALUES (\'PSE Ministry Team\', \'PSE Ministry Team\', True, \'ministry\');commit;')  


def downgrade():
    op.execute('DELETE FROM public."OperatingTeams" WHERE name in (\'PSE Ministry Team\');commit;')
