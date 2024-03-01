"""Add Records Ready for Review State

Revision ID: 6646acda32fe
Revises: 932d6dae5570
Create Date: 2024-01-23 10:16:22.141034

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6646acda32fe'
down_revision = '932d6dae5570'
branch_labels = None
depends_on = None


def upgrade():
    sql = '''INSERT INTO "FOIRequestStatuses" (name, description, isactive, statuslabel) VALUES ('Records Ready for Review', 'Records Ready for Review', true, 'recordsreadyforreview')'''
    op.execute(sql)

def downgrade():
    sql = '''DELETE FROM "FOIRequestStatuses" WHERE name = 'Records Ready for Review';'''
    op.execute(sql)
