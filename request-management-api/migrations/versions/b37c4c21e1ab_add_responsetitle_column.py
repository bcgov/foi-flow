"""add respones title column to FOIApplicantCorrespondences and FOIApplicantCorrespondencesRawRequests

Revision ID: b37c4c21e1ab
Revises: 7a3f1c9e2bd4
Create Date: 2025-06-30 16:29:04.522380

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b37c4c21e1ab'
down_revision = '7a3f1c9e2bd4'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('FOIApplicantCorrespondences', sa.Column('correspondencesubject', sa.String(length=255), nullable=True))
    op.add_column('FOIApplicantCorrespondencesRawRequests', sa.Column('correspondencesubject', sa.String(length=255), nullable=True))


def downgrade():
    op.drop_column('FOIApplicantCorrespondences', 'correspondencesubject')
    op.drop_column('FOIApplicantCorrespondencesRawRequests', 'correspondencesubject')