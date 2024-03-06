"""add axisapplicantid to applicant table

Revision ID: c590239f1b2f
Revises: d42a1cf67c5c
Create Date: 2024-02-29 22:51:55.709923

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c590239f1b2f'
down_revision = 'd42a1cf67c5c'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('FOIRequestApplicants', sa.Column('axisapplicantid', sa.Integer(), nullable=True))


def downgrade():
    op.drop_column('FOIRequestApplicants', 'axisapplicantid')
