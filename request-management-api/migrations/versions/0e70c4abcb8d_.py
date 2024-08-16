"""Adding open info status master data

Revision ID: 0e70c4abcb8d
Revises: aa2691fa6c3c
Create Date: 2024-08-15 16:48:01.934769

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0e70c4abcb8d'
down_revision = 'aa2691fa6c3c'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('OpenInfoStatus',
    sa.Column('oistatusid', sa.Integer(), autoincrement=True, nullable=False),
    sa.column('name', sa.String(), nullable=False),
    sa.Column('isactive', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('oistatusid')
    )

    op.execeut('''INSERT INTO public."OpenInfoStatus" (name, isactive) 
               VALUES 
               ('OI Review', True),
               ('Exemption Request', True),
               ('Do Not Publish', True),
               ('Publication Review', True),
               ('Peer Review', True),
               ('Ready For Publishing', True),
               ('Published', True),
               ('Unpublish Request', True);''')

def downgrade():
    op.drop_table('OpenInfoStatus')