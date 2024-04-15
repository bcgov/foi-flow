"""Add RTT tag

Revision ID: e698b39da6bd
Revises: 6646acda32fe
Create Date: 2024-04-15 08:17:20.554269

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e698b39da6bd'
down_revision = '6646acda32fe'
branch_labels = None
depends_on = None

def upgrade():
    op.execute('INSERT INTO public."NotificationTypes"(name, description, isactive,notificationtypelabel ) VALUES (\'Attachment Upload Event\', \'Attachment Upload Event\', true, \'attachmentuploadevent\');')

def downgrade():
    op.execute('DELETE FROM public."NotificationTypes" WHERE name = \'Attachment Upload Event\';')