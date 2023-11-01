"""migration mapper for AXIS to FOIMOD states

Revision ID: 9ba0a7a4fe69
Revises: 2e43869513c2
Create Date: 2023-08-02 12:53:20.184435

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9ba0a7a4fe69'
down_revision = '2e43869513c2'
branch_labels = None
depends_on = None


def upgrade():
    axismigration = op.create_table('AXISMigrationMapper',    
    sa.Column('stateonAXIS', sa.String(length=255), nullable=False),
    sa.Column('stateonFOI', sa.String(length=255), nullable=True)        
    )

    op.bulk_insert(
        axismigration,
        [
            {'stateonAXIS':'DAddRvwLog','stateonFOI':'Records Review'},
            {'stateonAXIS':'ReqforDocs','stateonFOI':'Call For Records'},           
        ])


def downgrade():
    op.drop_table('AXISMigrationMapper')
