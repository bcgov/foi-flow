"""empty message

Revision ID: 719e5289e6f8
Revises: bbee01df3e8d
Create Date: 2024-08-13 08:37:41.321684

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import column, table
from sqlalchemy.sql.sqltypes import Boolean, String

# revision identifiers, used by Alembic.
revision = '719e5289e6f8'
down_revision = 'bbee01df3e8d'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('ALTER TABLE public."CommentTypes" ADD COLUMN label VARCHAR(100)')
    commenttype_table = table('CommentTypes',
                                 column('name',String),
                                 column('label',String),
                                 column('description',String),
                                 column('isactive',Boolean),
                                   )
    op.bulk_insert(
        commenttype_table,
        [
            {'name':'IAO Internal','label': 'Internal','description':'internal comments input by IAO users','isactive':True},
            {'name':'Ministry Internal','label':'Internal','description':'internal comments input by Ministry users','isactive':True},
            {'name':'IAO Peer Review','label':'Peer Review','description':'peer review comments input by IAO users','isactive':True},
            {'name':'Ministry Peer Review','label':'Peer Review','description':'peer review comments input by Ministry users','isactive':True}                      
        ])
    
    
    op.execute('Update public."CommentTypes" set label = \'General\' where name = \'User submitted\';') 
    op.execute('Update public."CommentTypes" set label = \'System Generated\' where name = \'System generated\';')  
    op.execute('Update public."CommentTypes" set label = \'Divisional Tracking\' where name = \'Divisional Tracking\';')  


def downgrade():
    op.execute('delete from public."FOIRequestStatuses" where name in (\'IAO Internal\',\'Ministry Internal\',\'IAO Peer Review\',\'Ministry Peer Review\');')
    op.execute('ALTER TABLE public."CommentTypes" DROP label')
    # ### end Alembic commands ###
