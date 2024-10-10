"""update type for cfd personal sections

Revision ID: bd20ff56d1b1
Revises: f946afec2515
Create Date: 2024-04-18 22:09:45.416382

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bd20ff56d1b1'
down_revision = 'f946afec2515'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('Update public."ProgramAreaDivisions" set type=\'section\' where issection=TRUE;')

def downgrade():
    op.execute('Update public."ProgramAreaDivisions" set type=NULL where issection=TRUE;')
