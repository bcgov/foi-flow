"""empty message

Revision ID: 937254d7e8ff
Revises: fa3bece1d1bd
Create Date: 2023-03-27 15:31:43.465599

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '937254d7e8ff'
down_revision = 'fa3bece1d1bd'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('Insert into public."NotificationTypes" (name, description, isactive) values (\'PDFStitch\', \'PDFStitch\', true);commit;')


def downgrade():
    op.execute('delete from  public."FOIRequestNotificationUsers" where notificationid in (select notificationid from  public."FOIRequestNotifications" where notificationtypeid in (select notificationtypeid from  public."NotificationTypes" where name in (\'PDFStitch\')));commit;')
    op.execute('delete from  public."FOIRequestNotifications" where notificationtypeid in (select notificationtypeid from  public."NotificationTypes" where name in (\'PDFStitch\'));commit;')
    op.execute('delete from  public."NotificationTypes" where name in (\'PDFStitch\');commit;')
