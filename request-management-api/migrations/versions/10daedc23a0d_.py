"""empty message

Revision ID: 10daedc23a0d
Revises: c2b0e6e5352e
Create Date: 2022-11-14 15:22:36.661066

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '10daedc23a0d'
down_revision = 'c2b0e6e5352e'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('Insert into public."NotificationTypes" (name, description, isactive) values (\'Email Failure\', \'Email Failure\', true);commit;')
    op.execute('Insert into public."NotificationTypes" (name, description, isactive) values (\'Payment\', \'Payment\', true);commit;')


def downgrade():
    op.execute('delete from  public."NotificationTypes" where name in (\'Email Failure\');commit;')
    op.execute('delete from  public."NotificationTypes" where name in (\'Payment\');commit;')
