"""empty message

Revision ID: 6ffb804efde9
Revises: 596fb5cbb352
Create Date: 2022-01-05 16:35:31.158211

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '6ffb804efde9'
down_revision = '596fb5cbb352'
branch_labels = None
depends_on = None


def upgrade():
    extensionreason_stage_table = op.create_table('ExtensionReasons',
    sa.Column('extensionreasonid', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('reason', sa.String(length=100), nullable=False),
    sa.Column('isactive', sa.Boolean(), nullable=False),
    sa.Column('extensiontype', sa.String(length=25), nullable=False),
    sa.PrimaryKeyConstraint('extensionreasonid')
    )

    extensionstatus_stage_table =  op.create_table('ExtensionStatuses',
    sa.Column('extensionstatusid', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=25), nullable=False),
    sa.Column('description', sa.String(length=100), nullable=False),
    sa.Column('isactive', sa.Boolean(), nullable=False),  
    sa.PrimaryKeyConstraint('extensionstatusid')
    )

    op.create_table('FOIRequestExtensions',
    sa.Column('foirequestextensionid', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('extensionreasonid', sa.Integer(), nullable=False),
    sa.Column('extensionstatusid', sa.Integer(), nullable=False),
    sa.Column('foiministryrequest_id', sa.Integer(), nullable=False),
    sa.Column('foiministryrequestversion_id', sa.Integer(), nullable=False),
    sa.Column('extendedduedays', sa.Integer(), nullable=True),
    sa.Column('extendedduedate', sa.DateTime(), nullable=True),
    sa.Column('decisiondate', sa.DateTime(), nullable=True),
    sa.Column('approvednoofdays', sa.Integer(), nullable=True),    
    sa.Column('version', sa.Integer(), nullable=True),
    sa.Column('isactive', sa.Boolean(), nullable=True), 
    sa.Column('created_at', sa.DateTime(), nullable=False, default=datetime.now()),
    sa.Column('createdby', sa.String(length=120), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('updatedby', sa.String(length=120), nullable=True),

    sa.ForeignKeyConstraint(['foiministryrequest_id', 'foiministryrequestversion_id'], ['FOIMinistryRequests.foiministryrequestid', 'FOIMinistryRequests.version'], ),
    sa.ForeignKeyConstraint(['extensionreasonid'], ['ExtensionReasons.extensionreasonid'], ),
    # sa.ForeignKeyConstraint(['extensionstatusid'], ['ExtensionStatuses.extensionstatusid'], ),
    sa.PrimaryKeyConstraint('foirequestextensionid', 'version')
    )

    op.create_table('FOIRequestExtensionDocumentMapping',
    sa.Column('foirequestextensiondocumentid', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('foirequestextensionid', sa.Integer(), nullable=False),
    sa.Column('foiministrydocumentid', sa.Integer(), nullable=False),    
    sa.Column('extensionversion', sa.Integer(), nullable=False),    
    sa.Column('created_at', sa.DateTime(), nullable=False, default=datetime.now()),
    sa.Column('createdby', sa.String(length=120), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('updatedby', sa.String(length=120), nullable=True),

    sa.ForeignKeyConstraint(['foirequestextensionid', 'extensionversion'], ['FOIRequestExtensions.foirequestextensionid', 'FOIRequestExtensions.version'], ),    
    sa.PrimaryKeyConstraint('foirequestextensiondocumentid')
    )

    op.bulk_insert(
        extensionreason_stage_table,
        [
            {'reason':'Public Body - Consultation','isactive':True, 'extensiontype': 'Public Body'},
            {'reason':'Public Body - Further Detail from Applicant Required','isactive':True, 'extensiontype': 'Public Body'},
            {'reason':'Public Body - Large Volume and/or Volume of Search','isactive':True, 'extensiontype': 'Public Body'},
            {'reason':'Public Body - Large Volume and/or Volume of Search and Consultation','isactive':True, 'extensiontype': 'Public Body'},
            {'reason':'OIPC - Applicant Consent','isactive':True, 'extensiontype': 'OIPC'},
            {'reason':'OIPC - Consultation','isactive':True, 'extensiontype': 'OIPC'},
            {'reason':'OIPC - Further Detail from Applicant Required','isactive':True, 'extensiontype': 'OIPC'},
            {'reason':'OIPC - Large Volume and/or Volume of Search','isactive':True, 'extensiontype': 'OIPC'},
            {'reason':'OIPC - Large Volume and/or Volume of Search and Consultation','isactive':True, 'extensiontype': 'OIPC'},
            {'reason':'OIPC - Fair and Reasonable','isactive':True, 'extensiontype': 'OIPC'},
           
        ]
    )

    op.bulk_insert(
        extensionstatus_stage_table,
        [
            {'name':'Pending','isactive':True, 'description': 'Pending'},
            {'name':'Approved','isactive':True, 'description': 'Approved'},
            {'name':'Denied','isactive':True, 'description': 'Denied'}, 
        ]
    )

def downgrade():    
    op.drop_table('FOIRequestExtensionDocumentMapping')
    op.drop_table('FOIRequestExtensions')
    op.drop_table('ExtensionReasons')
    op.drop_table('ExtensionStatuses')
 
