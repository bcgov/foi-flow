"""empty message

Revision ID: 8cfd06cc6336
Revises: f5868c04138f
Create Date: 2021-08-09 16:40:46.683549

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import column, table
from sqlalchemy.sql.sqltypes import Boolean, String


# revision identifiers, used by Alembic.
revision = '8cfd06cc6336'
down_revision = 'f5868c04138f'
branch_labels = None
depends_on = None


def upgrade():
   ##Received Mode Data Insertion
    received_mode_table = table('ReceivedModes',
                                 column('name',String),
                                 column('description',String),
                                 column('isactive',Boolean),
                                   )
    op.execute('Truncate table public."ReceivedModes" RESTART IDENTITY CASCADE;commit;')                               
    op.bulk_insert(
        received_mode_table,
        [
            {'name':'Email','description':'Email','isactive':True},
            {'name':'Fax','description':'Fax','isactive':True},
            {'name':'Mail','description':'Mail','isactive':True},
            {'name':'Online Form','description':'Online Form','isactive':True},
        ]
    )


def downgrade():
    op.execute('Truncate table public."ReceivedModes" RESTART IDENTITY CASCADE;commit;')
