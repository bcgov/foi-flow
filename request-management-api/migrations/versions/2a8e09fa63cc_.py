"""empty message

Revision ID: 2a8e09fa63cc
Revises: 6523dfc49ad0
Create Date: 2022-04-01 11:50:57.938328

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2a8e09fa63cc'
down_revision = '6523dfc49ad0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('FOIRequestNotifications', sa.Column('axisnumber', sa.String(length=50), nullable=True))
    op.add_column('FOIRawRequestNotifications', sa.Column('axisnumber', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('FOIRequestNotifications', 'axisnumber')
    op.drop_column('FOIRawRequestNotifications', 'axisnumber')
    # ### end Alembic commands ###
