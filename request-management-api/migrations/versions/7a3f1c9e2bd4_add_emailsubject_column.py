"""add email subject column to FOIApplicantCorrespondences and FOIApplicantCorrespondencesRawRequests

Revision ID: 7a3f1c9e2bd4
Revises: 6e539b6b9ff5
Create Date: 2025-02-28 14:29:04.522380

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7a3f1c9e2bd4'
down_revision = '6e539b6b9ff5'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('FOIApplicantCorrespondences', sa.Column('emailsubject', sa.String(length=255), nullable=True))
    op.add_column('FOIApplicantCorrespondencesRawRequests', sa.Column('emailsubject', sa.String(length=255), nullable=True))


def downgrade():
    op.drop_column('FOIApplicantCorrespondences', 'emailsubject')
    op.drop_column('FOIApplicantCorrespondencesRawRequests', 'emailsubject')
