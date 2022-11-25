"""empty message

Revision ID: 3939b9fa5e3b
Revises: 14d5d6646dcd
Create Date: 2022-09-07 14:10:39.602325

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3939b9fa5e3b'
down_revision = '14d5d6646dcd'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('ApplicantCorrespondenceTags',
    sa.Column('tagid', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.Column('isactive', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('tagid')
    )


def downgrade():
    op.drop_table('ApplicantCorrespondenceTags')
