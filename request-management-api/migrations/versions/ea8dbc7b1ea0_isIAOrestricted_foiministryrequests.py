"""empty message

Revision ID: ea8dbc7b1ea0
Revises: b9411d30daac
Create Date: 2022-12-08 16:22:14.134901

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ea8dbc7b1ea0'
down_revision = 'b9411d30daac'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('FOIRestrictedMinistryRequests',
        sa.Column('restrictionid', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('ministryrequestid', sa.Integer(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('isrestricted', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('createdby', sa.String(length=120), nullable=False),        
        sa.Column('isactive', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['ministryrequestid', 'version'], ['FOIMinistryRequests.foiministryrequestid', 'FOIMinistryRequests.version'], ),
        sa.PrimaryKeyConstraint('restrictionid')
    )


def downgrade():
    op.drop_table('FOIRestrictedMinistryRequests')
