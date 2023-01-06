"""empty message

Revision ID: dfc4fb8d79b9
Revises: efd4e8f20384
Create Date: 2023-01-04 16:27:59.864329

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dfc4fb8d79b9'
down_revision = 'efd4e8f20384'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('INSERT INTO public."ProgramAreas"(name, type, isactive, bcgovcode, iaocode)	VALUES (\'Education and Child Care\', \'BC GOV Ministry\', True, \'ECC\', \'ECC\');commit;')


def downgrade():
    op.execute('DELETE FROM public."ProgramAreas" WHERE iaocode in (\'ECC\');commit;')
