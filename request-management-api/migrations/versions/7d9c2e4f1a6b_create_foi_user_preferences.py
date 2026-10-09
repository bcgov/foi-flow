"""create FOI user preferences

Revision ID: 7d9c2e4f1a6b
Revises: a4e9c7d2f1b6
Create Date: 2026-09-02

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "7d9c2e4f1a6b"
down_revision = "a4e9c7d2f1b6"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "FOIUserPreferences",
        sa.Column(
            "userpreferenceid",
            sa.Integer(),
            autoincrement=True,
            nullable=False
        ),
        sa.Column(
            "userid",
            sa.String(length=255),
            nullable=False
        ),
        sa.Column(
            "preferences",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False
        ),
        sa.Column(
            "schema_version",
            sa.Integer(),
            server_default=sa.text("1"),
            nullable=False
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=True
        ),
        sa.PrimaryKeyConstraint("userpreferenceid"),
        sa.UniqueConstraint(
            "userid",
            name="uq_foi_user_preferences_userid"
        )
    )

def downgrade():
    op.drop_table("FOIUserPreferences")
