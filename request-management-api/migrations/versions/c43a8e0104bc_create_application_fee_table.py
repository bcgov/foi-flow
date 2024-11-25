"""Create Application Fee Table

Revision ID: c43a8e0104bc
Revises: bbee01df3e8d
Create Date: 2024-11-05 10:58:11.256163

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c43a8e0104bc'
down_revision = 'bbee01df3e8d'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('FOIRequestApplicationFees',
    sa.Column('applicationfeeid', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('version', sa.Integer(), nullable=False),
    sa.Column('requestid', sa.Integer(), nullable=False),
    sa.Column('applicationfeestatus', sa.String(length=50), nullable=True),
    sa.Column('amountpaid', sa.Float(), nullable=True),
    sa.Column('paymentsource', sa.String(length=50), nullable=True),
    sa.Column('paymentdate', sa.DateTime(), nullable=True),
    sa.Column('orderid', sa.String(length=50), nullable=True),
    sa.Column('transactionnumber', sa.String(length=50), nullable=True),
    sa.Column('refundamount', sa.Float(), nullable=True),
    sa.Column('refunddate', sa.DateTime(), nullable=True),
    sa.Column('reasonforrefund', sa.Text, nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('createdby', sa.String(length=120), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('updatedby', sa.String(length=120), nullable=True),
    sa.PrimaryKeyConstraint('applicationfeeid', 'version'))

    op.create_table('FOIRequestApplicationFeeReceipts',
    sa.Column('receiptid', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('applicationfeeid', sa.Integer(), nullable=False),
    sa.Column('applicationfeeid_version', sa.Integer(), nullable=False),
    sa.Column('receiptfilename', sa.String(length=500), nullable=True),
    sa.Column('receiptfilepath', sa.Text, nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('createdby', sa.String(length=120), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('updatedby', sa.String(length=120), nullable=True),
    sa.Column('isactive', sa.Boolean(), server_default=sa.sql.expression.true()),
    sa.ForeignKeyConstraint(['applicationfeeid', 'applicationfeeid_version'], ['FOIRequestApplicationFees.applicationfeeid', 'FOIRequestApplicationFees.version']),
    sa.PrimaryKeyConstraint('receiptid'))

def downgrade():
    op.drop_table('FOIRequestApplicationFeeReceipts')
    op.drop_table('FOIRequestApplicationFees')