"""empty message

Revision ID: c41c901861a0
Revises: 639312d3816c
Create Date: 2021-08-09 13:05:36.054995

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import column, table
from sqlalchemy.sql.sqltypes import Boolean, String


# revision identifiers, used by Alembic.
revision = 'c41c901861a0'
down_revision = '639312d3816c'
branch_labels = None
depends_on = None


def upgrade():
    ##Received Mode Data Insertion
    requeststatus_table = table('FOIRequestStatuses',
                                 column('name',String),
                                 column('description',String),
                                 column('isactive',Boolean),
                                   )
    op.execute('Truncate table public."ReceivedModes" RESTART IDENTITY CASCADE;commit;')                               
    op.bulk_insert(
        requeststatus_table,
        [
            {'name':'Open','description':'Opened Request','isactive':True},
            {'name':'CFR','description':'Call For Records','isactive':True},
            {'name':'Closed','description':'Request closed','isactive':True}
            
        ]
    )


def downgrade():
    op.execute('Truncate table public."ReceivedModes" RESTART IDENTITY CASCADE;commit;') 
