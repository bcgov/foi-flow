"""empty message

Revision ID: b23c56f40dff
Revises: b2d89f8c0e22
Create Date: 2022-08-11 12:00:57.806959

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b23c56f40dff'
down_revision = 'b2d89f8c0e22'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('Select setval(pg_get_serial_sequence(\'public."DocumentTemplates"\', \'template_id\'), 2) ;')
    op.execute('insert into  public."DocumentTemplates"(extension, document_type_id) VALUES (\'docx\', (select document_type_id from public."DocumentTypes" where document_type_name=\'cfr_fee_payment_receipt\'));commit;')


def downgrade():
    op.execute('delete from public."DocumentTemplates" where document_type_id = (select document_type_id from public."DocumentTypes" where document_type_name=\'cfr_fee_payment_receipt\')')
