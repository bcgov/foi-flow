"""Migration script for setting issection default value for divisions - non CFD, MSD

Revision ID: 7341bc012ca9
Revises: ca122cd9b012
Create Date: 2023-08-30 13:57:08.435322

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7341bc012ca9'
down_revision = 'ca122cd9b012'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('UPDATE public."ProgramAreaDivisions" SET  issection=FALSE WHERE programareaid not in (SELECT programareaid FROM public."ProgramAreas" WHERE iaocode =\'CFD\' or  iaocode =\'MSD\');')


def downgrade():
    op.execute('UPDATE public."ProgramAreaDivisions" SET  issection=NULL WHERE programareaid not in (SELECT programareaid FROM public."ProgramAreas" WHERE iaocode =\'CFD\' or  iaocode =\'MSD\');')
