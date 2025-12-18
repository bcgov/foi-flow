"""empty message

Revision ID: 6fe1c7cef608
Revises: 2ccfbfe3a195
Create Date: 2022-09-09 11:02:49.213480

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6fe1c7cef608'
down_revision = '2ccfbfe3a195'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('ALTER TABLE public."FOIRequestPayments" ADD paidamount NUMERIC(10,2)')


def downgrade():
    op.execute('ALTER TABLE public."FOIRequestPayments" DROP paidamount')
