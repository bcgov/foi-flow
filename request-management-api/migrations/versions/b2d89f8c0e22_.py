"""empty message

Revision ID: b2d89f8c0e22
Revises: 6ef3221d0678
Create Date: 2022-08-11 10:56:22.987932

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b2d89f8c0e22'
down_revision = '6ef3221d0678'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('Select setval(pg_get_serial_sequence(\'public."DocumentTypes"\', \'document_type_id\'), 1) ;')
    op.execute('insert into  public."DocumentTypes"(document_type_name, description) VALUES (\'cfr_fee_payment_receipt\', \'Cfr Fee Payment Receipt\');commit;')


def downgrade():
    op.execute('delete from public."DocumentTypes" where document_type_name = \'cfr_fee_payment_receipt\'')
