"""empty message

Revision ID: 46e5ecb5339e
Revises: 4d97fe0e4979
Create Date: 2022-09-26 17:45:45.633683

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '46e5ecb5339e'
down_revision = '4d97fe0e4979'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    
    cfrformreason_stage_table =  op.create_table('CFRFormReasons',
    sa.Column('cfrformreasonid', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=25), nullable=False),
    sa.Column('description', sa.String(length=100), nullable=False),
    sa.Column('isactive', sa.Boolean(), nullable=False),  
    sa.PrimaryKeyConstraint('cfrformreasonid')
    )

    # ### end Alembic commands ###

    op.bulk_insert(
        cfrformreason_stage_table,
        [
            {'name':'narrowedrequest','isactive':True, 'description': 'Narrowed Request'},
            {'name':'revisedfeeestimate','isactive':True, 'description': 'Revised Fee Estimate'},
        ]
    )

    op.add_column('FOIRequestCFRFees', sa.Column('cfrformreasonid', sa.Integer(), nullable=True,))
    op.create_foreign_key(None, 'FOIRequestCFRFees', 'CFRFormReasons', ['cfrformreasonid'], ['cfrformreasonid'])


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint("cfrformreasonid", 'FOIRequestCFRFees', type_='foreignkey')
    op.drop_column('FOIRequestCFRFees', 'cfrformreasonid')
    op.drop_table('CFRFormReasons')
    # ### end Alembic commands ###

