"""empty message

Revision ID: 496b6f8ec82b
Revises: 10daedc23a0d
Create Date: 2022-12-30 10:31:32.974211

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '496b6f8ec82b'
down_revision = '10daedc23a0d'
branch_labels = None
depends_on = None


def upgrade():    
    op.execute('INSERT INTO public."ProgramAreas"(name, type, isactive, bcgovcode, iaocode)	VALUES (\'Post-Secondary Education and Skills Training\', \'BC GOV Ministry\', True, \'PSE\', \'PSE\');commit;')


def downgrade():
    op.execute('DELETE FROM public."ProgramAreas" WHERE iaocode in (\'PSE\');commit;')
