"""empty message

Revision ID: 5da11b0ca205
Revises: 5d9c4550d6d7
Create Date: 2021-11-02 16:40:09.253516

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import column, table
from sqlalchemy.sql.sqltypes import Boolean, String


# revision identifiers, used by Alembic.
revision = '5da11b0ca205'
down_revision = '5d9c4550d6d7'
branch_labels = None
depends_on = None


def upgrade():
    commenttype_table = table('CommentTypes',
                                 column('name',String),
                                 column('description',String),
                                 column('isactive',Boolean),
                                   )
    op.execute('Truncate table public."CommentTypes" RESTART IDENTITY CASCADE;commit;')                               
    op.bulk_insert(
        commenttype_table,
        [
            {'name':'User submitted','description':'comments input by FOI Flow users','isactive':True},
            {'name':'System generated','description':'auto generated comments by system as part of status updates etc','isactive':True},            
        ]
    )


def downgrade():
    op.execute('Truncate table public."CommentTypes" RESTART IDENTITY CASCADE;commit;')