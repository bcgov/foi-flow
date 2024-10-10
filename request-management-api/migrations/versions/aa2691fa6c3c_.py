"""empty message

Revision ID: aa2691fa6c3c
Revises: 9638286dc851
Create Date: 2024-05-30 17:07:19.236044

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'aa2691fa6c3c'
down_revision = '9638286dc851'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('insert into  public."DocumentTypes"(document_type_name, description) VALUES (\'CFD_responsepackage_redaction_summary\', \'Word template for CFD response package redaction summary pdf\');commit;')
    
    op.execute('insert into  public."DocumentTemplates"(extension, document_type_id) VALUES (\'docx\', (select document_type_id from public."DocumentTypes" where document_type_name=\'CFD_responsepackage_redaction_summary\'));commit;')

def downgrade():
    op.execute('delete from public."DocumentTypes" where document_type_name = \'CFD_responsepackage_redaction_summary\'')

    op.execute('delete from public."DocumentTemplates" where document_type_id = (select document_type_id from public."DocumentTypes" where document_type_name=\'CFD_responsepackage_redaction_summary\')')