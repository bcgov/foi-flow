"""empty message

Revision ID: 6d0085ebcf15
Revises: b23c56f40dff
Create Date: 2022-08-15 16:55:51.865113

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6d0085ebcf15'
down_revision = 'b23c56f40dff'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('insert into  public."DocumentTypes"(document_type_name, description) VALUES (\'cfr_fee_payment_receipt_half\', \'Cfr Fee Payment Receipt Half\');commit;')
    op.execute('insert into  public."DocumentTypes"(document_type_name, description) VALUES (\'cfr_fee_payment_receipt_full\', \'Cfr Fee Payment Receipt Full\');commit;')

    op.execute('insert into  public."DocumentTemplates"(extension, document_type_id) VALUES (\'docx\', (select document_type_id from public."DocumentTypes" where document_type_name=\'cfr_fee_payment_receipt_half\'));commit;')
    op.execute('insert into  public."DocumentTemplates"(extension, document_type_id) VALUES (\'docx\', (select document_type_id from public."DocumentTypes" where document_type_name=\'cfr_fee_payment_receipt_full\'));commit;')

def downgrade():
    op.execute('delete from public."DocumentTypes" where document_type_name = \'cfr_fee_payment_receipt_half\'')
    op.execute('delete from public."DocumentTypes" where document_type_name = \'cfr_fee_payment_receipt_ful\'')

    op.execute('delete from public."DocumentTemplates" where document_type_id = (select document_type_id from public."DocumentTypes" where document_type_name=\'cfr_fee_payment_receipt_half\')')
    op.execute('delete from public."DocumentTemplates" where document_type_id = (select document_type_id from public."DocumentTypes" where document_type_name=\'cfr_fee_payment_receipt_full\')')
