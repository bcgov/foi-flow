"""empty message

Revision ID: e8ddfca50e57
Revises: 5254ab336fec
Create Date: 2022-07-05 15:50:24.332145

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e8ddfca50e57'
down_revision = '5254ab336fec'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('update  public."ProgramAreaDivisionStages" set name=\'Awaiting Fee Estimate\' where name=\'Awaiting Fees\';commit;')
    op.execute('update  public."ProgramAreaDivisionStages" set name=\'Fee Estimate Received\' where name=\'Fees Received\';commit;')


def downgrade():
    op.execute('update  public."ProgramAreaDivisionStages" set name=\'Awaiting Fees\' where name=\'Awaiting Fee Estimate\';commit;')
    op.execute('update  public."ProgramAreaDivisionStages" set name=\'Fees Received\' where name=\'Fee Estimate Received\';commit;')
