"""OpenInformation exemptions master data

Revision ID: bf7e7298d642
Revises: 0e70c4abcb8d
Create Date: 2024-08-21 11:59:07.999420

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'bf7e7298d642'
down_revision = '0e70c4abcb8d'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('OpenInfoExemptions',
    sa.Column('oiexemptionid', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('isactive', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('oiexemptionid')
    )

    op.execute('''INSERT INTO public."OpenInfoExemptions" (name, isactive) 
               VALUES
               ('Another Government''s Information', True),
               ('Business Information', True),
               ('Federal Copyright', True),
               ('First Nations Information', True),
               ('Outside Scope of Publication Policy', True),
               ('Personal Information', True),
               ('Public Body Decision', True),
               ('Security Information', True);''')

def downgrade():
    op.drop_table('OpenInfoExemptions')