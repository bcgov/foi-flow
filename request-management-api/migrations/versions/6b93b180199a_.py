"""empty message

Revision ID: 6b93b180199a
Revises: 5f6cccd86344
Create Date: 2021-12-23 14:58:07.731592

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6b93b180199a'
down_revision = '5f6cccd86344'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('FOIRawRequestNotifications',
    sa.Column('notificationid', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('notification', sa.TEXT(), nullable=True),    
    sa.Column('notificationtypeid', sa.Integer(), nullable=False),
    sa.Column('requestid', sa.Integer(), nullable=True),
    sa.Column('version', sa.Integer(), nullable=True),
    sa.Column('idnumber', sa.String(length=50), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('createdby', sa.String(length=120), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('updatedby', sa.String(length=120), nullable=True),
    sa.ForeignKeyConstraint(['requestid', 'version'], ['FOIRawRequests.requestid', 'FOIRawRequests.version'] ),
    sa.ForeignKeyConstraint(['notificationtypeid'], ['NotificationTypes.notificationtypeid']),
    sa.PrimaryKeyConstraint('notificationid')
    ) 
    op.create_table('FOIRawRequestNotificationUsers',
    sa.Column('notificationuserid', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('notificationid', sa.Integer(), nullable=False),
    sa.Column('userid', sa.String(length=100), nullable=False),
    sa.Column('notificationusertypeid', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('createdby', sa.String(length=120), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('updatedby', sa.String(length=120), nullable=True),
    sa.ForeignKeyConstraint(['notificationid'], ['FOIRawRequestNotifications.notificationid']),
    sa.ForeignKeyConstraint(['notificationusertypeid'], ['NotificationUserTypes.notificationusertypeid']),
    sa.PrimaryKeyConstraint('notificationuserid')
    ) 
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('FOIRawRequestNotifications')
    op.drop_table('FOIRawRequestNotificationUsers')
    # ### end Alembic commands ###
