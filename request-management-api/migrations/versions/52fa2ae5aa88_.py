"""empty message

Revision ID: 52fa2ae5aa88
Revises: ca17d3f81205
Create Date: 2022-07-15 16:59:58.498488

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '52fa2ae5aa88'
down_revision = 'ca17d3f81205'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('update  public."FeeCodes" set description=\'Freedom of Information Application Fee\' where code=\'FOI0001\';commit;')
    op.execute('insert into  public."FeeCodes"(code, description, start_date, end_date, fee, revenue_account_id) VALUES (\'FOI0002\', \'Freedom of Information Processing Fee\', now()::Date, null, 0, 1);commit;')


def downgrade():
    op.execute('update  public."FeeCodes" set description=\'Freedom of Information Fee\' where code=\'FOI0001\';commit;')
    op.execute('delete from public."FeeCodes" where code=\'FOI0002\';commit;')
