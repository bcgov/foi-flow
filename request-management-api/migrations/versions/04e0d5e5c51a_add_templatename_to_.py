"""add templatename to FOIApplicantCorrespondences

Revision ID: 04e0d5e5c51a
Revises: 7a554bfa243d
Create Date: 2025-02-28 11:29:04.522380

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '04e0d5e5c51a'
down_revision = '7a554bfa243d'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('FOIApplicantCorrespondences', sa.Column('templatename', sa.String(length=255), nullable=True))
    op.add_column('FOIApplicantCorrespondences', sa.Column('templatetype', sa.String(length=120), nullable=True))
    op.add_column('FOIApplicantCorrespondencesRawRequests', sa.Column('templatename', sa.String(length=255), nullable=True))
    op.add_column('FOIApplicantCorrespondencesRawRequests', sa.Column('templatetype', sa.String(length=120), nullable=True))


def downgrade():
    op.drop_column('FOIApplicantCorrespondences', 'templatename')
    op.drop_column('FOIApplicantCorrespondences', 'templatetype')
    op.drop_column('FOIApplicantCorrespondencesRawRequests', 'templatename')
    op.drop_column('FOIApplicantCorrespondencesRawRequests', 'templatetype')
