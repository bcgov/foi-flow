"""empty message

Revision ID: 0f31e19d3672
Revises: 79a9cf6f1aa9
Create Date: 2023-01-05 16:06:41.673762

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0f31e19d3672'
down_revision = '79a9cf6f1aa9'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('INSERT INTO public."ProgramAreas"(name, type, isactive, bcgovcode, iaocode)	VALUES (\'Jobs, Economic Development and Innovation\', \'BC GOV Ministry\', True, \'JED\', \'JED\');commit;')


def downgrade():
    op.execute('DELETE FROM public."ProgramAreas" WHERE iaocode in (\'JED\');commit;')
