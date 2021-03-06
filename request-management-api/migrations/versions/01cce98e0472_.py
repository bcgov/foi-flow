"""empty message

Revision ID: 01cce98e0472
Revises: 789c89c4306c
Create Date: 2022-03-22 15:51:52.343472

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '01cce98e0472'
down_revision = '789c89c4306c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###  
    op.execute('create index rawcomment_idx on  public."FOIRawRequestComments" (requestid, version);')      
    op.execute('create index reqcomment_idx on  public."FOIRequestComments" (ministryrequestid, version);')
    
    op.execute('create index rawdocument_idx on  public."FOIRawRequestDocuments" (foirequest_id, foirequestversion_id);')      
    
    op.execute('create index rawwatcher_idx on  public."FOIRawRequestWatchers" (requestid, version);')      
    op.execute('create index reqwatcher_idx on  public."FOIRequestWatchers" (ministryrequestid, version);')         
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###    
    op.execute('drop index rawcomment_idx;') 
    op.execute('drop index reqcomment_idx;')
    
    op.execute('drop index rawdocument_idx;') 
    
    op.execute('drop index rawwatcher_idx;') 
    op.execute('drop index reqwatcher_idx;') 
    # ### end Alembic commands ###
