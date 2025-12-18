"""empty message

Revision ID: 4d97fe0e4979
Revises: 39989f4c2178
Create Date: 2022-09-12 11:52:32.067782

"""
from datetime import datetime
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import column, table
from sqlalchemy.sql.sqltypes import Boolean, String,Text,Integer,DateTime

# revision identifiers, used by Alembic.
revision = '4d97fe0e4979'
down_revision = '39989f4c2178'
branch_labels = None
depends_on = None

def upgrade():
    op.execute('Truncate table public."ApplicantCorrespondenceTemplates" RESTART IDENTITY CASCADE;commit;')
    op.execute('ALTER TABLE public."ApplicantCorrespondenceTemplates" ADD display Boolean')
    applicant_correspondence_templates = table('ApplicantCorrespondenceTemplates',
                                 column('name',String),
                                 column('documenturipath',Text),
                                 column('description',String),
                                 column('active',Boolean),
                                 column('display',Boolean),
                                 column('version',Integer),
                                 column('created_at',DateTime),
                                 column('createdby',String),
                                   )
    op.bulk_insert(
        applicant_correspondence_templates,
        [
            {'name':'PAYONLINE','description':'Fee Estimate','active':True,'display':True,'version':1 ,'documenturipath':'/TEMPLATES/EMAILS/fee_estimate_notification.html','created_at':datetime.now(),'createdby':'system'},
            {'name':'PAYOUTSTANDING','description':'Outstanding Fee','active':True,'display':True,'version':1 ,'documenturipath':'/TEMPLATES/EMAILS/fee_estimate_notification_outstanding.html','created_at':datetime.now(),'createdby':'system'},
            {'name':'FULLPAYMENT','description':'Fee Estimate Payment Received','active':True,'display':False,'version':1 ,'documenturipath':'/TEMPLATES/EMAILS/fee_payment_confirmation_full.html','created_at':datetime.now(),'createdby':'system'},
            {'name':'HALFPAYMENT','description':'Fee Estimate Deposit Received','active':True,'display':False,'version':1 ,'documenturipath':'/TEMPLATES/EMAILS/fee_payment_confirmation_half.html','created_at':datetime.now(),'createdby':'system'},
            {'name':'PAYOUTSTANDINGFULLPAYMENT','description':'Outstanding Fee Payment Received','active':True,'display':False,'version':1 ,'documenturipath':'/TEMPLATES/EMAILS/fee_payment_confirmation_outstanding.html','created_at':datetime.now(),'createdby':'system'},

        ]
    )


def downgrade():
    op.execute('Truncate table public."ApplicantCorrespondenceTemplates" RESTART IDENTITY CASCADE;commit;')
    op.execute('ALTER TABLE public."ApplicantCorrespondenceTemplates" DROP display')
