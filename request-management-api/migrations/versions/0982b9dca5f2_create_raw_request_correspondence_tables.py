"""Create raw request correspondence tables

Revision ID: 0982b9dca5f2
Revises: 5b9b19213803
Create Date: 2024-07-18 16:40:06.002653

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0982b9dca5f2'
down_revision = '5b9b19213803'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('FOIApplicantCorrespondences', sa.Column('response_at', sa.DateTime(), nullable=True))

    op.create_table('FOIApplicantCorrespondencesRawRequests',
    sa.Column('applicantcorrespondenceid', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('parentapplicantcorrespondenceid', sa.Integer()),
    sa.Column('templateid', sa.Integer()),
    sa.Column('correspondencemessagejson', sa.Text,nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('response_at', sa.DateTime(), nullable=True),
    sa.Column('createdby', sa.String(length=120), nullable=True),
    sa.Column('updatedby', sa.String(length=120), nullable=True),
    sa.Column('foirawrequest_id', sa.Integer(), nullable=True),
    sa.Column('foirawrequestversion_id', sa.Integer(), nullable=True),
    sa.Column('sentcorrespondencemessage', sa.Text,nullable=True),
    sa.Column('sent_at', sa.DateTime(), nullable=True),
    sa.Column('sentby', sa.String(length=120), nullable=True),
    sa.Column('version', sa.Integer(), nullable=False),
    sa.Column('isdraft', sa.Boolean(), nullable=True),  
    sa.Column('isdeleted', sa.Boolean(), nullable=True),  
    sa.Column('isresponse', sa.Boolean(), nullable=True),  
    sa.Column('israwrequest', sa.Boolean(), nullable=True, server_default=sa.true()),

    sa.ForeignKeyConstraint(['foirawrequest_id', 'foirawrequestversion_id'], ['FOIRawRequests.requestid', 'FOIRawRequests.version']),
    sa.PrimaryKeyConstraint('applicantcorrespondenceid', 'version'),
    )

    op.create_table('FOIApplicantCorrespondenceAttachmentsRawRequests',
        sa.Column('applicantcorrespondenceattachmentid', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('applicantcorrespondenceid', sa.Integer(), nullable=False),
        sa.Column('applicantcorrespondence_version', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('attachmentfilename', sa.String(length=500),nullable=False),
        sa.Column('attachmentdocumenturipath', sa.Text,nullable=False),
        sa.Column('createdby', sa.String(length=120), nullable=True),
        sa.Column('updatedby', sa.String(length=120), nullable=True),    
        sa.ForeignKeyConstraint(['applicantcorrespondenceid', 'applicantcorrespondence_version'], ['FOIApplicantCorrespondencesRawRequests.applicantcorrespondenceid', 'FOIApplicantCorrespondencesRawRequests.version'] ,),
        sa.PrimaryKeyConstraint('applicantcorrespondenceattachmentid', 'version')
    )

    op.create_table('FOIApplicantCorrespondenceEmailsRawRequests',
    sa.Column('applicantcorrespondenceemailid', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('applicantcorrespondence_id', sa.Integer(), nullable=False),
    sa.Column('applicantcorrespondence_version', sa.Integer(), nullable=False),
    sa.Column('correspondence_to', sa.Text(), nullable=False), 
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('createdby', sa.String(length=120), nullable=True),
    sa.Column('updatedby', sa.String(length=120), nullable=True),    
    sa.ForeignKeyConstraint(['applicantcorrespondence_id','applicantcorrespondence_version'], ['FOIApplicantCorrespondencesRawRequests.applicantcorrespondenceid','FOIApplicantCorrespondencesRawRequests.version'] ,),
    sa.PrimaryKeyConstraint('applicantcorrespondenceemailid')
    )

    op.create_table('FOICorrespondenceEmailsRawRequests',
    sa.Column('correspondenceemailid', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('email', sa.TEXT(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('createdby', sa.String(length=120), nullable=True),
    sa.Column('updatedby', sa.String(length=120), nullable=True),
    sa.Column('foirawrequest_id', sa.Integer(), nullable=True),
    sa.Column('foirawrequestversion_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['foirawrequest_id', 'foirawrequestversion_id'], ['FOIRawRequests.requestid', 'FOIRawRequests.version'], ),
    sa.PrimaryKeyConstraint('correspondenceemailid')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('FOIApplicantCorrespondences', 'response_at')
    op.drop_table('FOIApplicantCorrespondenceAttachmentsRawRequests')
    op.drop_table('FOIApplicantCorrespondenceEmailsRawRequests')
    op.drop_table('FOIApplicantCorrespondencesRawRequests')
    op.drop_table('FOICorrespondenceEmailsRawRequests')
    # ### end Alembic commands ###
