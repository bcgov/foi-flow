"""empty message

Revision ID: bf8a28cb0063
Revises: a0a19680f300
Create Date: 2021-11-30 03:22:54.337771

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bf8a28cb0063'
down_revision = 'a0a19680f300'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Payments', 'status',
               existing_type=sa.String(length=20),
               type_=sa.String(),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Payments', 'status',
               existing_type=sa.String(),
               type_=sa.String(length=20),
               existing_nullable=False)
    # ### end Alembic commands ###
