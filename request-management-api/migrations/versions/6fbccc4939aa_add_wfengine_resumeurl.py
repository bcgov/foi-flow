"""empty message

Revision ID: 6fbccc4939aa
Revises: 5a7ce876a293
Create Date: 2026-08-17 18:19:22.619782

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "6fbccc4939aa"
down_revision = "5a7ce876a293"
branch_labels = None
depends_on = None


def upgrade():
    # FOIRawRequests
    op.add_column(
        "FOIRawRequests",
        sa.Column(
            "wfengine",
            sa.String(length=50),
            nullable=True,
            server_default="camunda",
        ),
    )
    op.add_column(
        "FOIRawRequests",
        sa.Column("wfmetadata", postgresql.JSON(astext_type=sa.Text()), nullable=True),
    )

    # FOIRequests
    op.add_column(
        "FOIRequests",
        sa.Column(
            "wfengine",
            sa.String(length=50),
            nullable=True,
            server_default="camunda",
        ),
    )
    op.add_column(
        "FOIRequests",
        sa.Column("wfmetadata", postgresql.JSON(astext_type=sa.Text()), nullable=True),
    )

    # Remove the default after existing rows are populated
    op.alter_column("FOIRawRequests", "wfengine", server_default=None)
    op.alter_column("FOIRequests", "wfengine", server_default=None)


def downgrade():
    op.drop_column("FOIRawRequests", "wfengine")
    op.drop_column("FOIRawRequests", "wfmetadata")
    op.drop_column("FOIRequests", "wfengine")
    op.drop_column("FOIRequests", "wfmetadata")
