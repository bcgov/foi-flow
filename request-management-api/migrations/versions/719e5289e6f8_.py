"""empty message

Revision ID: 719e5289e6f8
Revises: 5fdd5df3d642
Create Date: 2024-08-13 08:37:41.321684

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import column, table
from sqlalchemy.sql.sqltypes import Boolean, String

# revision identifiers, used by Alembic.
revision = '719e5289e6f8'
down_revision = '5fdd5df3d642'
branch_labels = None
depends_on = None


def upgrade():
    commenttype_table = table('CommentTypes',
                                 column('name',String),
                                 column('description',String),
                                 column('isactive',Boolean),
                                   )
    op.bulk_insert(
        commenttype_table,
        [
            {'name':'IAO Internal','description':'internal comments input by IAO users','isactive':True},
            {'name':'Ministry Internal','description':'internal comments input by Ministry users','isactive':True},
            {'name':'IAO Peer Review','description':'peer review comments input by IAO users','isactive':True},
            {'name':'Ministry Peer Review','description':'peer review comments input by Ministry users','isactive':True}                      
        ])

def downgrade():
    op.execute('delete from public."FOIRequestStatuses" where name in (\'IAO Internal\',\'Ministry Internal\',\'IAO Peer Review\',\'Ministry Peer Review\');')
    # ### end Alembic commands ###
