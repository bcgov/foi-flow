"""Create OIPC tables

Revision ID: 3b399ca506fe
Revises: 7fa7236d06fb
Create Date: 2023-11-14 22:29:58.451320

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import Table, Column, Integer, String, MetaData
meta = MetaData()


# revision identifiers, used by Alembic.
revision = '3b399ca506fe'
down_revision = '7fa7236d06fb'
branch_labels = None
depends_on = None


def upgrade():
    subjectcodestable = op.create_table('OIPCReviewTypes',
    sa.Column('reviewtypeid', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('createdby', sa.String(length=120), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('updatedby', sa.String(length=120), nullable=True),
    sa.Column('isactive', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('reviewtypeid')
    )

    reasonstable = op.create_table('OIPCReasons',
    sa.Column('reasonid', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('createdby', sa.String(length=120), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('updatedby', sa.String(length=120), nullable=True),
    sa.Column('isactive', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('reasonid')
    )

    statusestable = op.create_table('OIPCStatuses',
    sa.Column('statusid', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('createdby', sa.String(length=120), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('updatedby', sa.String(length=120), nullable=True),
    sa.Column('isactive', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('statusid')
    )

    outcomestable = op.create_table('OIPCOutcomes',
    sa.Column('outcomeid', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('createdby', sa.String(length=120), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('updatedby', sa.String(length=120), nullable=True),
    sa.Column('isactive', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('outcomeid')
    )
    # op.execute('''CREATE TABLE OIPCReviewTypes (
    #            reviewtypeid integer PRIMARY KEY,
    #            created_at datetime,
    #            created_by varchar(120),
    #            updated_at datetime,
    #            updated_by varchar(120),
    #            isactive boolean NOT NULL
    # )''')

def downgrade():
    op.drop_table('OIPCReviewTypes')
    op.drop_table('OIPCReasons')
    op.drop_table('OIPCStatuses')
    op.drop_table('OIPCOutcomes')
