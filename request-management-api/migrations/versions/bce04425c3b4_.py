"""empty message

Revision ID: bce04425c3b4
Revises: f61413c0517d
Create Date: 2021-09-21 13:05:24.175730

"""
from alembic import op
import sqlalchemy as sa

from sqlalchemy.sql import column, table
from sqlalchemy.sql.sqltypes import Boolean, String


# revision identifiers, used by Alembic.
revision = 'bce04425c3b4'
down_revision = 'c8b147681f8b'
branch_labels = None
depends_on = None


def upgrade():
    requeststatus_table = table('FOIRequestStatuses',
                                 column('name',String),
                                 column('description',String),
                                 column('isactive',Boolean),
                                   )
    op.execute('Truncate table public."FOIRequestStatuses" RESTART IDENTITY CASCADE;commit;')                               
    op.bulk_insert(
        requeststatus_table,
        [
            {'name':'Open','description':'Opened Request','isactive':True},
            {'name':'Call For Records','description':'Call For Records','isactive':True},
            {'name':'Closed','description':'Request closed','isactive':True},
            {'name':'Redirect','description':'Redirect','isactive':True},
            {'name':'Unopened','description':'Unopened','isactive':True},
            {'name':'Intake in Progress','description':'Intake in Progress','isactive':True},
        ]
    )


def downgrade():
    requeststatus_table = table('FOIRequestStatuses',
                                 column('name',String),
                                 column('description',String),
                                 column('isactive',Boolean),
                                   )
    op.execute('Truncate table public."FOIRequestStatuses" RESTART IDENTITY CASCADE;commit;')                               
    op.bulk_insert(
        requeststatus_table,
        [
            {'name':'Open','description':'Opened Request','isactive':True},
            {'name':'CFR','description':'Call For Records','isactive':True},
            {'name':'Closed','description':'Request closed','isactive':True}
            
        ])
