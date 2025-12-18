"""empty message

Revision ID: 667466f947aa
Revises: d9e99bce0dde
Create Date: 2021-09-28 16:54:03.336049

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import column, table
from sqlalchemy.sql.sqltypes import Boolean, String


# revision identifiers, used by Alembic.
revision = '667466f947aa'
down_revision = 'd9e99bce0dde'
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
            {'name':'Review','description':'Review Request','isactive':True},
            {'name':'Fee Assessed','description':'Fee Assessed','isactive':True},
            {'name':'Consult','description':'Consult required on Request','isactive':True},
            {'name':'Sign Off','description':'Request Signed Off','isactive':True},
           
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
            {'name':'Call For Records','description':'Call For Records','isactive':True},
            {'name':'Closed','description':'Request closed','isactive':True},
            {'name':'Redirect','description':'Redirect','isactive':True},
            {'name':'Unopened','description':'Unopened','isactive':True},
            {'name':'Intake in Progress','description':'Intake in Progress','isactive':True},
        ]
    )
