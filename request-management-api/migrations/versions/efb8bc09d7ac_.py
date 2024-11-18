"""ADD NEW PROGRAM AREA (LSB)

Revision ID: efb8bc09d7ac
Revises: ec27defe9178
Create Date: 2024-10-28 13:54:56.964072

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'efb8bc09d7ac'
down_revision = 'ec27defe9178'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('''INSERT INTO public."ProgramAreas" (name, type, isactive, bcgovcode, iaocode) VALUES ('Legal Services Branch', 'Other', True, 'LSB', 'LSB'); commit;''')


def downgrade():
    op.execute('''DELETE FROM public."ProgramAreas" WHERE bcgovcode = 'LSB'; commit;''')
