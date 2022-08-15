"""empty message

Revision ID: 2ccfbfe3a195
Revises: b23c56f40dff
Create Date: 2022-08-15 11:05:48.013459

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2ccfbfe3a195'
down_revision = 'b23c56f40dff'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('ALTER TABLE public."FOIRequestPayments" ADD paymentexpirydate timestamp') 


def downgrade():
    op.execute('ALTER TABLE public."FOIRequestPayments" DROP paymentexpirydate') 
