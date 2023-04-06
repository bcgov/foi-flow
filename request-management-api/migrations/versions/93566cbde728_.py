"""empty message

Revision ID: 93566cbde728
Revises: 937254d7e8ff
Create Date: 2023-04-04 12:59:05.717415

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '93566cbde728'
down_revision = '937254d7e8ff'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('Insert into public."NotificationUserTypes" (name, description, isactive) values (\'Triggered User\', \'Triggered User\', true);commit;')  


def downgrade():
    op.execute('Delete from public."NotificationUserTypes" where name in (\'Triggered User\', \'Triggered User\');commit;')
