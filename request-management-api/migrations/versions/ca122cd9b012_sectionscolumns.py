""" Adding 2 columns issection and parentid for capturing sections and its heirarchy under division - CFD, MSD
Task #4292

Revision ID: ca122cd9b012
Revises: d43db71d53e5
Create Date: 2023-08-30 13:26:20.287595

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ca122cd9b012'
down_revision = 'd43db71d53e5'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('ProgramAreaDivisions', sa.Column('issection', sa.Boolean(), nullable=True,default=False))
    op.add_column('ProgramAreaDivisions', sa.Column('parentid', sa.Integer(), nullable=True))
    

def downgrade():
    op.drop_column('ProgramAreaDivisions', 'issection')
    op.drop_column('ProgramAreaDivisions', 'parentid')
