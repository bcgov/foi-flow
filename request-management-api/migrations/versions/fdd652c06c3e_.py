"""empty message

Revision ID: fdd652c06c3e
Revises: c87f7d0b9606
Create Date: 2022-10-19 10:39:59.870187

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fdd652c06c3e'
down_revision = 'c87f7d0b9606'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('ALTER TABLE public."FOIApplicantCorrespondences" ALTER COLUMN correspondencemessagejson DROP NOT NULL;')


def downgrade():
    op.execute('ALTER TABLE public."FOIApplicantCorrespondences" ALTER COLUMN correspondencemessagejson SET NOT NULL;')
