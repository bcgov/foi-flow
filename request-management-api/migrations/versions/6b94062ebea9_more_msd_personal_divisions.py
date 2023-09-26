"""More MSD Personal Divisions

Revision ID: 6b94062ebea9
Revises: 07a6d930b276
Create Date: 2023-09-15 16:15:44.118182

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6b94062ebea9'
down_revision = '07a6d930b276'
branch_labels = None
depends_on = None


def upgrade():
    divisons = ["FASB", "ELMSD", "PLMS", "ISD", "SHRC"]
    sortorder = 2

    for division in divisons:
        op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby, sortorder,  issection, specifictopersonalrequests)\
        VALUES ((SELECT programareaid FROM public."ProgramAreas" WHERE iaocode =\'MSD\'), \''+division+'\', TRUE, NOW(), \'system\', '+ str(sortorder) +',FALSE, TRUE );')
        sortorder = sortorder+1

def downgrade():
    op.execute('DELETE FROM public."ProgramAreaDivisions" WHERE programareaid in (SELECT programareaid FROM public."ProgramAreas" WHERE iaocode =\'MSD\') AND issection=FALSE and specifictopersonalrequests=TRUE and sortorder > 1')