"""empty message

Revision ID: 8e4be6862181
Revises: ee6a05e2f5be
Create Date: 2023-02-01 11:56:49.540766

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8e4be6862181'
down_revision = 'ee6a05e2f5be'
branch_labels = None
depends_on = None

#Indigenous Governing Entity
def upgrade():
    op.execute('INSERT INTO public."ApplicantCategories"(name, description, isactive) VALUES (\'Indigenous Governing Entity\', \'Indigenous Governing Entity\', True);commit;')


def downgrade():
    op.execute('DELETE FROM public."ApplicantCategories" WHERE name in (\'Indigenous Governing Entity\');commit;')
