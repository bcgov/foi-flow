"""Columns for migrations

Revision ID: 2e43869513c2
Revises: eea7ea4d60ac
Create Date: 2023-07-26 13:27:04.441402

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2e43869513c2'
down_revision = 'eea7ea4d60ac'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('FOIRequestApplicants', sa.Column('migrationreference', sa.Text, nullable=True))
    op.add_column('FOIRequests', sa.Column('migrationreference', sa.Text, nullable=True))
    op.add_column('FOIMinistryRequests', sa.Column('migrationreference', sa.Text, nullable=True))
    op.add_column('FOIRequestApplicantMappings', sa.Column('migrationreference', sa.Text, nullable=True))
    op.add_column('FOIRequestContactInformation', sa.Column('migrationreference', sa.Text, nullable=True))    
    

def downgrade():
    op.drop_column('FOIRequestApplicants', 'migrationreference')
    op.drop_column('FOIRequests', 'migrationreference')
    op.drop_column('FOIMinistryRequests', 'migrationreference')
    op.drop_column('FOIRequestApplicantMappings', 'migrationreference')
    op.drop_column('FOIRequestContactInformation', 'migrationreference')
