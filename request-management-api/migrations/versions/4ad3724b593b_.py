"""Delivery Mode update

Revision ID: 4ad3724b593b
Revises: cfe019598f8b
Create Date: 2025-09-08 16:25:46.895124

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import column, table
from sqlalchemy.sql.sqltypes import Boolean, String


# revision identifiers, used by Alembic.
revision = '4ad3724b593b'
down_revision = 'cfe019598f8b'
branch_labels = None
depends_on = None


def upgrade():
    delivery_mode_table = table('DeliveryModes',
                                 column('name',String),
                                 column('description',String),
                                 column('isactive',Boolean),
                                   )
    op.bulk_insert(
        delivery_mode_table,
        [
            {'name':'Post','description':'Post','isactive':True},
            {'name':'Courier','description':'Courier','isactive':True},
            {'name':'E-Mail','description':'E-Mail','isactive':True}
        ]
    )


def downgrade():
    op.execute('DELETE FROM public."DeliveryModes" WHERE name in (\'Post\', \'Courier\', \'E-Mail\')) and isactive=true);commit;')