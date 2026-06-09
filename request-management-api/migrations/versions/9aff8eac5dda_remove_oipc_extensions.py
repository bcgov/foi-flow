"""Remove OIPC extensions

Revision ID: 9aff8eac5dda
Revises: 8c4b76110854
Create Date: 2026-06-08 10:45:09.337484

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '9aff8eac5dda'
down_revision = '8c4b76110854'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""UPDATE public."ExtensionReasons" SET isactive = false WHERE reason = 'OIPC - Applicant Consent';""")
    op.execute("""UPDATE public."ExtensionReasons" SET defaultextendedduedays = 0 WHERE reason = 'Public Body - Applicant Consent';""")

def downgrade():
    op.execute("""UPDATE public."ExtensionReasons" SET isactive = true WHERE reason = 'OIPC - Applicant Consent';""")
    op.execute("""UPDATE public."ExtensionReasons" SET defaultextendedduedays = 30 WHERE reason = 'Public Body - Applicant Consent';""")