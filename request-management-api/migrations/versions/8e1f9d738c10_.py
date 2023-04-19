"""empty message

Revision ID: 8e1f9d738c10
Revises: 93566cbde728
Create Date: 2023-04-18 15:26:09.503739

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8e1f9d738c10'
down_revision = '93566cbde728'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('''UPDATE public."FOIRequestStatuses"
        SET isactive=false
        WHERE name='Deduplication';commit;''')


def downgrade():
    op.execute('''UPDATE public."FOIRequestStatuses"
        SET isactive=true
        WHERE name='Deduplication';commit;''')
