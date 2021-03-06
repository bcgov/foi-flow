"""empty message

Revision ID: d6cb86e76ea7
Revises: 
Create Date: 2021-06-02 15:53:11.575346

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'd6cb86e76ea7'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('FOIRawRequests',
    sa.Column('requestid', sa.Integer(), nullable=False),
    sa.Column('requestrawdata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
    sa.Column('status', sa.String(length=25), nullable=True),
    sa.Column('notes', sa.String(length=120), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('requestid')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('FOIRawRequests')
    # ### end Alembic commands ###
