"""
Add Records in Transit Status

Revision ID: 3a4f7b2c6d9e
Revises: 7fe3c2636fbf
Create Date: 2025-08-27 8:50:55.126582

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '3a4f7b2c6d9e'
down_revision = '7fe3c2636fbf'
branch_labels = None
depends_on = None

def upgrade():
    op.execute('INSERT INTO public."FOIRequestStatuses"(name, description, isactive, statuslabel) VALUES (\'Records in Transit\', \'Records in Transit\', True, \'recordsintransit\');commit;')


def downgrade():
    op.execute('DELETE FROM public."FOIRequestStatuses" WHERE name = \'Records in Transit\';commit;')