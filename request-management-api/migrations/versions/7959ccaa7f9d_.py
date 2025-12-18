"""empty message

Revision ID: 7959ccaa7f9d
Revises: e8ddfca50e57
Create Date: 2022-08-02 12:11:49.864516

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import column, table
from sqlalchemy.sql.sqltypes import Boolean, String

# revision identifiers, used by Alembic.
revision = '7959ccaa7f9d'
down_revision = 'e8ddfca50e57'
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
            {'name':'Divisional Tracking','description':'comments posted by ‘Divisional Tracking’ process','isactive':True}                      
        ])

def downgrade():
    op.execute('DELETE FROM public."CommentTypes" WHERE name =\'Divisional Tracking\';commit;')
