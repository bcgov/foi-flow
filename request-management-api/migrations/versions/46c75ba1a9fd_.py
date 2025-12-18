"""empty message

Revision ID: 46c75ba1a9fd
Revises: bab145529239
Create Date: 2021-08-09 15:19:34.737783

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import column, table
from sqlalchemy.sql.sqltypes import Boolean, String


# revision identifiers, used by Alembic.
revision = '46c75ba1a9fd'
down_revision = 'bab145529239'
branch_labels = None
depends_on = None


def upgrade():
    requestortype_table = table('RequestorTypes',
                                 column('name',String),
                                 column('description',String),
                                 column('isactive',Boolean),
                                   )
    op.execute('Truncate table public."RequestorTypes" RESTART IDENTITY CASCADE;commit;')                               
    op.bulk_insert(
        requestortype_table,
        [
            {'name':'Self','description':'Self-applying FOI request','isactive':True},
            {'name':'Applying for other person','description':'Applying FOI request on behalf of other person','isactive':True},
            {'name':'Applying for a child under 12','description':'Applying FOI request for a child under 12','isactive':True},
        ]
    )

def downgrade():
    op.execute('Truncate table public."RequestorTypes" RESTART IDENTITY CASCADE;commit;')
