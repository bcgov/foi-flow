"""empty message

Revision ID: 0b551f4a8cce
Revises: b863a277c491
Create Date: 2023-06-01 22:31:24.595281

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0b551f4a8cce'
down_revision = 'beb310568ee4'

branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute('ALTER TABLE public."FOIRequestNotifications" ALTER COLUMN notification TYPE jsonb USING notification::jsonb;')
    op.execute('ALTER TABLE public."FOIRawRequestNotifications" ALTER COLUMN notification TYPE jsonb USING notification::jsonb;')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute('ALTER TABLE public."FOIRequestNotifications" ALTER COLUMN notification TYPE json USING notification::json;')
    op.execute('ALTER TABLE public."FOIRawRequestNotifications" ALTER COLUMN notification TYPE json USING notification::json;')
    # ### end Alembic commands ###
