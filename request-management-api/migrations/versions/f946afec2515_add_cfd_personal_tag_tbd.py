"""add cfd personal tag TBD

Revision ID: f946afec2515
Revises: d1d4f6cdfd68
Create Date: 2024-04-18 10:50:18.297693

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f946afec2515'
down_revision = 'd1d4f6cdfd68'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('INSERT INTO public."ProgramAreaDivisions" \
                (programareaid, name, isactive, created_at, createdby, sortorder, issection, specifictopersonalrequests, type) \
                VALUES ( \
                    (SELECT programareaid FROM public."ProgramAreas" WHERE iaocode =\'CFD\'), \
                    \'TBD\', TRUE, NOW(), \'system\', \
                    ( \
                        select max(sortorder) from public."ProgramAreaDivisions" \
                        where isactive=TRUE and issection=TRUE and specifictopersonalrequests=TRUE \
                            and programareaid=(SELECT programareaid FROM public."ProgramAreas" WHERE iaocode=\'CFD\') \
                    )+1, \
                    TRUE, TRUE, \'section\' );')


def downgrade():
    op.execute('DELETE FROM public."ProgramAreaDivisions" WHERE programareaid=(SELECT programareaid FROM public."ProgramAreas" WHERE iaocode =\'CFD\') and name=\'TBD\' and type=\'section\'')
