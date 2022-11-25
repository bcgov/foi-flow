"""empty message

Revision ID: 6ef3221d0678
Revises: 52fa2ae5aa88
Create Date: 2022-08-05 13:08:42.868780

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6ef3221d0678'
down_revision = '52fa2ae5aa88'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('FOIRequestPayments',
    sa.Column('paymentid', sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
    sa.Column('version', sa.Integer(), primary_key=True, nullable=False),
    sa.Column('foirequestid', sa.Integer(), nullable=False),
    sa.Column('ministryrequestid', sa.Integer(), nullable=False),
    sa.Column('ministryrequestversion', sa.Integer(), nullable=True),  
    sa.Column('paymenturl', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('createdby', sa.String(length=120), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('updatedby', sa.String(length=120), nullable=True),
    sa.ForeignKeyConstraint(['ministryrequestid', 'ministryrequestversion'], ['FOIMinistryRequests.foiministryrequestid', 'FOIMinistryRequests.version']),
    sa.PrimaryKeyConstraint('paymentid' , 'version')
    )
    pass


def downgrade():
    op.drop_table('FOIRequestPayments')
    pass
