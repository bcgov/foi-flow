"""create AXISCorrespondence

Revision ID: 48f0a96fe2a1
Revises: 3a4f7b2c6d9e
Create Date: 2026-02-01 23:30:22.853214

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '48f0a96fe2a1'
down_revision = '3a4f7b2c6d9e'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('AXISCorrespondence',
    sa.Column('foiministrydocumentid', sa.Integer(), nullable=False),
    sa.Column('axiscorrespondenceid', sa.Integer(), nullable=False),
    sa.Column('type', sa.String(length=120), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('createdby', sa.String(length=120), nullable=True)
    )

def downgrade():
    op.drop_table('AXISCorrespondence')