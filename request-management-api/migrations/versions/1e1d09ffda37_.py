"""empty message

Revision ID: 1e1d09ffda37
Revises: 10daedc23a0d
Create Date: 2022-12-23 12:41:32.185214

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1e1d09ffda37'
down_revision = '10daedc23a0d'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('INSERT INTO public."ProgramAreas"(name, type, isactive, bcgovcode, iaocode)	VALUES (\'Ministry of Education\', \'BC GOV Ministry\', True, \'EDUC\', \'EDUC\');commit;')
    op.execute('INSERT INTO public."ProgramAreas"(name, type, isactive, bcgovcode, iaocode)	VALUES (\'Post-Secondary Education and Skills Training\', \'BC GOV Ministry\', True, \'PEST\', \'PEST\');commit;')
    
def downgrade():    
    op.execute('DELETE FROM public."ProgramAreas" WHERE iaocode in (\'PEST\',\'EDUC\');commit;')
    
