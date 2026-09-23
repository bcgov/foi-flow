"""Add selectable flag to program area divisions

Revision ID: a4e9c7d2f1b6
Revises: 5a7ce876a293
Create Date: 2026-09-16

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a4e9c7d2f1b6"
down_revision = "5a7ce876a293"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "ProgramAreaDivisions",
        sa.Column(
            "isselectable",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )


def downgrade():
    op.drop_column("ProgramAreaDivisions", "isselectable")
