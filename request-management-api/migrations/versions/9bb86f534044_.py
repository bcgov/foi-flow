"""empty message

Revision ID: 9bb86f534044
Revises: 6fe1c7cef608
Create Date: 2022-09-12 11:41:35.595235

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9bb86f534044'
down_revision = '6fe1c7cef608'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('ALTER TABLE public."DocumentTypes" ALTER COLUMN document_type_name TYPE VARCHAR(50)')
    op.execute('insert into  public."DocumentTypes"(document_type_name, description) VALUES (\'outstanding_fee_payment_receipt\', \'Cfr Outstanding Fee Payment Receipt\');commit;')
    op.execute('insert into  public."DocumentTemplates"(extension, document_type_id) VALUES (\'docx\', (select document_type_id from public."DocumentTypes" where document_type_name=\'outstanding_fee_payment_receipt\'));commit;')

def downgrade():
    op.execute('ALTER TABLE public."DocumentTypes" ALTER COLUMN document_type_name TYPE VARCHAR(30)')
    op.execute('delete from public."DocumentTypes" where document_type_name = \'outstanding_fee_payment_receipt\'')
    op.execute('delete from public."DocumentTemplates" where document_type_id = (select document_type_id from public."DocumentTypes" where document_type_name=\'outstanding_fee_payment_receipt\')')
