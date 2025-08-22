"""Add cc column to applicant correspondence emails

Revision ID: 6e539b6b9ff5
Revises: a193e5b37d9c
Create Date: 2025-05-27 15:46:09.565898

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6e539b6b9ff5'
down_revision = 'a193e5b37d9c'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('ALTER TABLE public."FOIApplicantCorrespondenceEmails" ADD iscarboncopy boolean DEFAULT(False)')
    op.execute('ALTER TABLE public."FOIApplicantCorrespondenceEmailsRawRequests" ADD iscarboncopy boolean DEFAULT(False)')

def downgrade():
    op.execute('ALTER TABLE public."FOIApplicantCorrespondenceEmailsRawRequests" DROP COLUMN iscarboncopy')
    op.execute('ALTER TABLE public."FOIApplicantCorrespondenceEmails" DROP COLUMN iscarboncopy')
