"""empty message

Revision ID: 79a9cf6f1aa9
Revises: 042ef5df9ca1
Create Date: 2023-01-05 16:00:00.900858

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '79a9cf6f1aa9'
down_revision = '042ef5df9ca1'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('Update public."ProgramAreas" SET name = \'Post-Secondary Education and Future Skills\' where iaocode = \'PSE\';')    


def downgrade():
    op.execute('Update public."ProgramAreas" SET name = \'Post-Secondary Education and Skills Training\' where iaocode = \'PSE\';')    
