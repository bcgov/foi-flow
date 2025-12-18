"""empty message

Revision ID: 14d5d6646dcd
Revises: c2e2c5d4eb7a
Create Date: 2022-09-07 13:45:55.528065

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '14d5d6646dcd'
down_revision = 'c2e2c5d4eb7a'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('FOIApplicantCorrespondenceAttachments',
        sa.Column('applicantcorrespondenceattachmentid', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('applicantcorrespondenceid', sa.Integer(), nullable=False),    
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('attachmentfilename', sa.String(length=500),nullable=False),
        sa.Column('attachmentdocumenturipath', sa.Text,nullable=False),
        sa.Column('createdby', sa.String(length=120), nullable=True),
        sa.Column('updatedby', sa.String(length=120), nullable=True),    
        sa.ForeignKeyConstraint(['applicantcorrespondenceid'], ['FOIApplicantCorrespondences.applicantcorrespondenceid'] ,),
        sa.PrimaryKeyConstraint('applicantcorrespondenceattachmentid')
    )


def downgrade():
    op.drop_table('FOIApplicantCorrespondenceAttachments')
