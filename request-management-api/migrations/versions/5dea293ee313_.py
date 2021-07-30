"""empty message

Revision ID: 5dea293ee313
Revises: 84f11a2b5659
Create Date: 2021-07-29 14:45:35.873685

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import column, table
from sqlalchemy.sql.sqltypes import Boolean, String


# revision identifiers, used by Alembic.
revision = '5dea293ee313'
down_revision = '84f11a2b5659'
branch_labels = None
depends_on = None


def upgrade():
    delivery_mode_table = table('DeliveryModes',
                                 column('name',String),
                                 column('description',String),
                                 column('isactive',Boolean),
                                   )
    op.execute('Truncate table public."DeliveryModes" RESTART IDENTITY CASCADE;commit;')                               
    op.bulk_insert(
        delivery_mode_table,
        [
            {'name':'Secure File Transfer','description':'Secure File Transfer','isactive':True},
            {'name':'In Person Pick up','description':'In Person Pick up','isactive':True}
        ]
    )

    


def downgrade():
    op.execute('Truncate table public."DeliveryModes" RESTART IDENTITY CASCADE;commit;')
    
