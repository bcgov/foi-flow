"""empty message

Revision ID: 79ad99148fa4
Revises: 08143691b340
Create Date: 2023-01-31 04:21:42.695267

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '79ad99148fa4'
down_revision = '08143691b340'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('Insert into public."NotificationTypes" (name, description, isactive) values (\'Records\', \'Records\', true);commit;')


def downgrade():
    op.execute('delete from  public."FOIRequestNotificationUsers" where notificationid in (select notificationid from  public."FOIRequestNotifications" where notificationtypeid in (select notificationtypeid from  public."NotificationTypes" where name in (\'Records\')));commit;')
    op.execute('delete from  public."FOIRequestNotifications" where notificationtypeid in (select notificationtypeid from  public."NotificationTypes" where name in (\'Records\'));commit;')
    op.execute('delete from  public."NotificationTypes" where name in (\'Records\');commit;')

