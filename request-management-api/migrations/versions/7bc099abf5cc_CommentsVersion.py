"""empty message

Revision ID: 7bc099abf5cc
Revises: 67e0b98b63ea
Create Date: 2024-04-03 10:40:00.641551

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7bc099abf5cc'
down_revision = '67e0b98b63ea'
branch_labels = None
depends_on = None


def upgrade():
    
    op.add_column('FOIRawRequestComments', sa.Column('commentsversion', sa.Integer(), nullable=True))
    op.add_column('FOIRequestComments', sa.Column('commentsversion', sa.Integer(), nullable=True))

    op.execute('Update public."FOIRawRequestComments" set commentsversion = 1;')
    op.execute('Update public."FOIRequestComments" set commentsversion = 1;')

    op.alter_column('FOIRawRequestComments', 'commentsversion', nullable=False)
    op.alter_column('FOIRequestComments', 'commentsversion', nullable=False)

    op.drop_constraint('FOIRawRequestComments_pkey', 'FOIRawRequestComments', type_='primary')
    op.create_primary_key('FOIRawRequestComments_version_pkey', 'FOIRawRequestComments', ['commentid','commentsversion'])

    op.drop_constraint('FOIRequestComments_pkey', 'FOIRequestComments', type_='primary')
    op.create_primary_key('FOIRequestComments_version_pkey', 'FOIRequestComments', ['commentid','commentsversion'])

def downgrade():
    op.drop_constraint('FOIRawRequestComments_version_pkey', 'FOIRawRequestComments', type_='primary')
    op.create_primary_key('FOIRawRequestComments_pkey', 'FOIRawRequestComments', ['commentid'])
    
    op.drop_constraint('FOIRequestComments_version_pkey', 'FOIRequestComments', type_='primary')
    op.create_primary_key('FOIRequestComments_pkey', 'FOIRequestComments', ['commentid'])
    
    op.drop_column('FOIRequestComments', 'commentsversion')
    op.drop_column('FOIRawRequestComments', 'commentsversion')
