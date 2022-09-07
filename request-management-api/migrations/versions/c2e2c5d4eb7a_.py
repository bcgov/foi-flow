"""empty message

Revision ID: c2e2c5d4eb7a
Revises: 30c5b9c88d33
Create Date: 2022-09-07 11:01:20.879504

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c2e2c5d4eb7a'
down_revision = '30c5b9c88d33'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('FOIApplicantCorrespondences',
    sa.Column('applicantcorrespondenceid', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('parentapplicantcorrespondenceid', sa.Integer()),
    sa.Column('templateid', sa.Integer()),
    sa.Column('correspondencemessagejson', sa.Text,nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('createdby', sa.String(length=120), nullable=True),
    sa.Column('updatedby', sa.String(length=120), nullable=True),
    sa.Column('foiministryrequest_id', sa.Integer(), nullable=True),
    sa.Column('foiministryrequestversion_id', sa.Integer(), nullable=True),
 
    sa.ForeignKeyConstraint(['foiministryrequest_id', 'foiministryrequestversion_id'], ['FOIMinistryRequests.foiministryrequestid', 'FOIMinistryRequests.version'], ),
    sa.PrimaryKeyConstraint('applicantcorrespondenceid')
    )


def downgrade():
    op.drop_table('FOIApplicantCorrespondences')
