"""OpenInformation FOIRequest transaction data

Revision ID: f1865771195f
Revises: 98cd70bd07f0
Create Date: 2024-08-22 10:54:16.545912

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'f1865771195f'
down_revision = '98cd70bd07f0'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('FOIOpenInfoAdditionalFiles',
        sa.Column('additionalfileid', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('s3uripath', sa.Text,nullable=False),
        sa.Column('ministryrequestid', sa.Integer(), nullable=False),
        sa.Column('filename', sa.String(length=500),nullable=False),
        sa.Column('createdby', sa.String(length=120), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updatedby', sa.String(length=120), nullable=True), 
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('attributes', sa.Text,nullable=True),
        sa.PrimaryKeyConstraint('additionalfileid' )
    )

def downgrade():
    op.drop_table('FOIOpenInfoAdditionalFiles')