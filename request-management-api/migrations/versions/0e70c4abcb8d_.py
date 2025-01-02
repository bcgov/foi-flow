"""OpenInformation status master data

Revision ID: 0e70c4abcb8d
Revises: 83cfc8047acf
Create Date: 2024-08-15 16:48:01.934769

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0e70c4abcb8d'
down_revision = '83cfc8047acf'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('OpenInformationStatuses',
    sa.Column('oistatusid', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('isactive', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('oistatusid')
    )

    op.execute('''INSERT INTO public."OpenInformationStatuses" (name, isactive) 
               VALUES 
               ('First Review', True),
               ('Peer Review', True),
               ('Ready to Publish', True),
               ('Published', True),
               ('HOLD Publication', True),
               ('Unpublished', True),
               ('Do Not Publish', True),
               ('Exemption Request', True);''')

def downgrade():
    op.drop_table('OpenInformationStatuses')