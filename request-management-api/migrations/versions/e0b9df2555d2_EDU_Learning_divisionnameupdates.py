"""empty message

Revision ID: e0b9df2555d2
Revises: ddc762eacb84
Create Date: 2023-01-12 10:05:50.218433

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e0b9df2555d2'
down_revision = 'ddc762eacb84'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('update public."ProgramAreaDivisions" set name = \'System Liaison and Supports\' where name=\'Learning\' and programareaid \
    in (SELECT programareaid FROM public."ProgramAreas" WHERE iaocode in  (\'EDU\',\'ECC\'));')

    op.execute('update public."ProgramAreaDivisions" set name = \'Learning and Education Programs\' where name=\'Education Programs\' and programareaid \
    in (SELECT programareaid FROM public."ProgramAreas" WHERE iaocode in  (\'EDU\',\'ECC\'));')


def downgrade():
    op.execute('update public."ProgramAreaDivisions" set name = \'Learning\' where name=\'System Liaison and Supports\' and programareaid \
    in (SELECT programareaid FROM public."ProgramAreas" WHERE iaocode in  (\'EDU\',\'ECC\'));')

    op.execute('update public."ProgramAreaDivisions" set name = \'Education Programs\' where name=\'Learning and Education Programs\' and programareaid \
    in (SELECT programareaid FROM public."ProgramAreas" WHERE iaocode in  (\'EDU\',\'ECC\'));')
