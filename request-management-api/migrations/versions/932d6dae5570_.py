"""empty message

Revision ID: 932d6dae5570
Revises: b4da31675bd0
Create Date: 2024-02-05 14:00:56.263099

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '932d6dae5570'
down_revision = 'd42a1cf67c5c'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('insert into  public."DocumentTypes"(document_type_name, description) VALUES (\'redline_redaction_summary\', \'Word template for redline redaction summary pdf\');commit;')
    op.execute('insert into  public."DocumentTypes"(document_type_name, description) VALUES (\'responsepackage_redaction_summary\', \'Word template for response package redaction summary pdf\');commit;')
    
    op.execute('insert into  public."DocumentTemplates"(extension, document_type_id) VALUES (\'docx\', (select document_type_id from public."DocumentTypes" where document_type_name=\'redline_redaction_summary\'));commit;')
    op.execute('insert into  public."DocumentTemplates"(extension, document_type_id) VALUES (\'docx\', (select document_type_id from public."DocumentTypes" where document_type_name=\'responsepackage_redaction_summary\'));commit;')

def downgrade():
    op.execute('delete from public."DocumentTypes" where document_type_name = \'redline_redaction_summary\'')
    op.execute('delete from public."DocumentTypes" where document_type_name = \'responsepackage_redaction_summary\'')

    op.execute('delete from public."DocumentTemplates" where document_type_id = (select document_type_id from public."DocumentTypes" where document_type_name=\'redline_redaction_summary\')')
    op.execute('delete from public."DocumentTemplates" where document_type_id = (select document_type_id from public."DocumentTypes" where document_type_name=\'responsepackage_redaction_summary\')')

