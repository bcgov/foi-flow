"""OpenInformation publication status master data

Revision ID: 9564370c6c43
Revises: bf7e7298d642
Create Date: 2024-08-21 15:16:09.185802

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '9564370c6c43'
down_revision = 'bf7e7298d642'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('OpenInfoPublicationStatuses',
    sa.Column('oipublicationstatusid', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('isactive', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('oipublicationstatusid')
    )

    op.execute('''INSERT INTO public."OpenInfoPublicationStatuses" (name, isactive)
               VALUES
               ('Do Not Publish', True),
               ('Publish', True),
               ('Unpublish Request', True);''')

def downgrade():
    op.drop_table('OpenInfoPublicationStatuses')