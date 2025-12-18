"""empty message

Revision ID: 30c5b9c88d33
Revises: 9bb86f534044
Create Date: 2022-09-06 15:36:45.347950

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '30c5b9c88d33'
down_revision = '9bb86f534044'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('ApplicantCorrespondenceTemplates',
    sa.Column('templateid', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('documenturipath', sa.Text, nullable=False),
    sa.Column('name', sa.String(length=500), nullable=False),
    sa.Column('description', sa.String(length=1000) ),
    sa.Column('active', sa.Boolean, nullable=False),
    sa.Column('version', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True, default=datetime.now()),
    sa.Column('createdby', sa.String(length=120), nullable=True),       
    sa.PrimaryKeyConstraint('templateid')
    )


def downgrade():
    op.drop_table('ApplicantCorrespondenceTemplates')
