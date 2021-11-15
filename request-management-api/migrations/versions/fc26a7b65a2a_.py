"""empty message

Revision ID: fc26a7b65a2a
Revises: 1347453b75e6
Create Date: 2021-11-10 19:07:40.807103

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fc26a7b65a2a'
down_revision = '1347453b75e6'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint('FOIMinistryRequestDocuments_pkey', 'FOIMinistryRequestDocuments', type_='primary')    
    op.create_primary_key(
            "FOIMinistryRequestDocuments_pkey", "FOIMinistryRequestDocuments",
            ["foiministrydocumentid", "version"]
        )


def downgrade():
    op.drop_constraint('FOIMinistryRequestDocuments_pkey', 'FOIMinistryRequestDocuments', type_='primary')  
    op.create_primary_key(
            "FOIMinistryRequestDocuments_pkey", "FOIMinistryRequestDocuments",
            ["foiministrydocumentid"]
        )
