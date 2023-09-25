"""Adding Section 5 Pending FOI Status to FOIRequestStatuses Table

Revision ID: a79cd809e85e
Revises: b51a0f2635c1
Create Date: 2023-09-25 14:37:29.208839

"""
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a79cd809e85e'
down_revision = 'b51a0f2635c1'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('INSERT INTO public."FOIRequestStatuses"(requeststatusid, name, description, isactive) VALUES (19, \'Section 5 Pending\', \'Section 5 Pending (Personal)\', true);commit;')
    


def downgrade():
    op.execute('DELETE FROM public."FOIRequestStatuses" WHERE requeststatusid = 19;commit;')
