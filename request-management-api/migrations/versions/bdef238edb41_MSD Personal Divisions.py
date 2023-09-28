"""MSD Personals SDD DOcument Division

Revision ID: bdef238edb41
Revises: 1e9a62e22f88
Create Date: 2023-09-12 15:23:54.743381

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bdef238edb41'
down_revision = '1e9a62e22f88'
branch_labels = None
depends_on = None


def upgrade():
    divisons = ["SDD Document Tracking"]
    sortorder = 1

    for division in divisons:
        op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby, sortorder,  issection, specifictopersonalrequests)\
        VALUES ((SELECT programareaid FROM public."ProgramAreas" WHERE iaocode =\'MSD\'), \''+division+'\', TRUE, NOW(), \'system\', '+ str(sortorder) +',FALSE, TRUE );')
        sortorder = sortorder+1

def downgrade():
    op.execute('DELETE FROM public."ProgramAreaDivisions" WHERE programareaid in (SELECT programareaid FROM public."ProgramAreas" WHERE iaocode =\'MSD\') AND issection=FALSE and specifictopersonalrequests=TRUE')