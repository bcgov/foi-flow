"""empty message

Revision ID: d42a1cf67c5c
Revises: ba218164248e
Create Date: 2024-02-08 12:40:33.968711

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'd42a1cf67c5c'
down_revision = 'ba218164248e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
        op.create_table('UnopenedReport',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
            sa.Column('rawrequestid', sa.Integer(), nullable=False),
            sa.Column('date', sa.DateTime(), nullable=True),
            sa.Column('rank', sa.Integer(), nullable=False),    
            sa.Column('potentialmatches', postgresql.JSON(astext_type=sa.Text()), nullable=True)
        )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
        op.execute('DROP TABLE IF EXISTS public."UnopenedReport";')

    # ### end Alembic commands ###