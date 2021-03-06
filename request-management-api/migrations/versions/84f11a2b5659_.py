"""empty message

Revision ID: 84f11a2b5659
Revises: 1aadec56e7f2
Create Date: 2021-07-23 15:28:53.653101

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '84f11a2b5659'
down_revision = '1aadec56e7f2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('FOIRawRequests_pkey', 'FOIRawRequests', type_='primary')
    op.create_primary_key('FOIRawRequests_version_pkey', 'FOIRawRequests', ['requestid','version'])
    op.create_table('DeliveryModes',
    sa.Column('deliverymodeid', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.Column('isactive', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('deliverymodeid')
    )
    op.create_table('ReceivedModes',
    sa.Column('receivedmodeid', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.Column('isactive', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('receivedmodeid')
    )
    # ### end Alembic commands ###


def downgrade():
    op.drop_constraint('FOIRawRequests_version_pkey', 'FOIRawRequests', type_='primary')
    op.create_primary_key('FOIRawRequests_pkey', 'FOIRawRequests', ['requestid'])
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('ReceivedModes')
    op.drop_table('DeliveryModes')
    # ### end Alembic commands ###
