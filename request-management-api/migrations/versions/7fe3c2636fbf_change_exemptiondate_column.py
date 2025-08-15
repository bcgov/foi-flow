"""empty message

Revision ID: 7fe3c2636fbf
Revises: 092981b8477d
Create Date: 2025-03-20 13:38:16.841376

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '7fe3c2636fbf'
down_revision = '092981b8477d'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('ALTER TABLE public."FOIOpenInformationRequests" RENAME COLUMN oiexemptiondate TO receiveddate;')

def downgrade():
    op.execute('ALTER TABLE public."FOIOpenInformationRequests" RENAME COLUMN receiveddate TO oiexemptiondate;')