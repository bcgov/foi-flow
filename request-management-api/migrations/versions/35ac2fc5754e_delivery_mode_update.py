"""Delivery Mode update

Revision ID: 35ac2fc5754e
Revises: 8f16afbd3bae
Create Date: 2025-12-10 07:08:00.057558

"""
from alembic import op
from sqlalchemy.sql import column, table
from sqlalchemy.sql.sqltypes import Boolean, String



# revision identifiers, used by Alembic.
revision = '35ac2fc5754e'
down_revision = '8f16afbd3bae'
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