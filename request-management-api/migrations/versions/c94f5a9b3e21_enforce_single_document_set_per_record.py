"""Enforce single document set ownership per record

Revision ID: c94f5a9b3e21
Revises: 8253475faad7
Create Date: 2026-03-17 11:30:00.000000

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'c94f5a9b3e21'
down_revision = '8253475faad7'
branch_labels = None
depends_on = None


def upgrade():

    op.create_unique_constraint(
        "uq_foirequestrecordgroups_record_id",
        "FOIRequestRecordGroups",
        ["record_id"],
    )


def downgrade():
    op.drop_constraint(
        "uq_foirequestrecordgroups_record_id",
        "FOIRequestRecordGroups",
        type_="unique",
    )
