"""New Table: FOIRequestInvoices

Revision ID: 8253475faad7
Revises: 05dee3d60a8c
Create Date: 2025-12-19 14:28:29.852354

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '8253475faad7'
down_revision = '05dee3d60a8c'
branch_labels = None
depends_on = None


def upgrade():
    # Create foirequestinvoice table
    op.create_table(
        'FOIRequestInvoices',
        sa.Column('invoiceid', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('foirequestcfrfee_id', sa.Integer(), nullable=False),
        sa.Column('foirequestcfrfeeversion_id', sa.Integer(), nullable=False),
        sa.Column('documentpath', sa.Text(), nullable=False),
        sa.Column('filename', sa.String(length=500),nullable=False),
        sa.Column('applicant_name', sa.String(length=120),nullable=False),
        sa.Column('applicant_address', sa.String(length=200),nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.String(length=120), nullable=False),
        sa.ForeignKeyConstraint(['foirequestcfrfee_id','foirequestcfrfeeversion_id'], ['FOIRequestCFRFees.cfrfeeid', 'FOIRequestCFRFees.version']),
        sa.PrimaryKeyConstraint('invoiceid')
    )

    #Create foirequestinvoice template
    op.execute('''INSERT INTO public."DocumentTypes" (document_type_name, description) VALUES ('cfr_fee_invoice', 'CFR Fee Invoice'); ''')
    op.execute('''INSERT INTO public."DocumentTemplates" (extension, document_type_id) SELECT 'docx', document_type_id FROM public."DocumentTypes" WHERE document_type_name = 'cfr_fee_invoice';''')


def downgrade():
    op.execute('''DELETE FROM public."DocumentTemplates" WHERE document_type_id IN (SELECT document_type_id FROM public."DocumentTypes" WHERE document_type_name = 'cfr_fee_invoice');''')
    op.execute('''DELETE FROM public."DocumentTypes" WHERE document_type_name = 'cfr_fee_invoice';''')
    op.drop_table("FOIRequestInvoices")