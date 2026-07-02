"""Add new CloseReasons (Intake Redirect & Outside Scope s.3)

Revision ID: 5a7ce876a293
Revises: f7c3b1d2e9f4
Create Date: 2026-06-19 21:15:06.873290

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '5a7ce876a293'
down_revision = 'f7c3b1d2e9f4'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""INSERT INTO public."CloseReasons" (name, isactive, created_at, createdby) VALUES ('Intake - Redirect Sec 4/5', true, now(), 'System');""")
    op.execute("""INSERT INTO public."CloseReasons" (name, isactive, created_at, createdby) VALUES ('Outside Scope of Act - s. 3 (5)', true, now(), 'System');""")


def downgrade():
    op.execute("""DELETE FROM public."CloseReasons" WHERE name = 'Intake - Redirect Sec 4/5';""")
    op.execute("""DELETE FROM public."CloseReasons" WHERE name = 'Outside Scope of Act - s. 3 (5)';""")
