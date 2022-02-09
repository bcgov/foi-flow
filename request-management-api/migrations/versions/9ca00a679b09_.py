"""empty message

Revision ID: 9ca00a679b09
Revises: 6ffb804efde9
Create Date: 2022-02-04 16:00:08.156512

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '9ca00a679b09'
down_revision = '6ffb804efde9'
branch_labels = None
depends_on = None

# columnname_username = 'FOIAssignees.username'

def upgrade():
    op.create_table(
        'FOIAssignees',
        sa.Column('foiassigneeid', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('username', sa.String(length=120), nullable=False, unique=True),
        sa.Column('firstname', sa.String(length=100), nullable=False),
        sa.Column('middlename', sa.String(length=100), nullable=True),
        sa.Column('lastname', sa.String(length=100), nullable=False),
        sa.Column('isactive', sa.Boolean(), nullable=False, default=True),
        sa.PrimaryKeyConstraint('foiassigneeid'),
    )

    op.create_foreign_key(
        'FOIRawRequests_assignedto_fkey',
        'FOIRawRequests',
        'FOIAssignees',
        ['assignedto'],
        ['username'],
    )

    op.create_foreign_key(
        'FOIMinistryRequests_assignedto_fkey',
        'FOIMinistryRequests',
        'FOIAssignees',
        ['assignedto'],
        ['username'],
    )

    op.create_foreign_key(
        'FOIMinistryRequests_assignedministryperson_fkey',
        'FOIMinistryRequests',
        'FOIAssignees',
        ['assignedministryperson'],
        ['username'],
    )

def downgrade():
    op.drop_constraint('FOIRawRequests_assignedto_fkey', 'FOIRawRequests', type_='foreignkey')
    op.drop_constraint('FOIMinistryRequests_assignedto_fkey', 'FOIMinistryRequests', type_='foreignkey')
    op.drop_constraint('FOIMinistryRequests_assignedministryperson_fkey', 'FOIMinistryRequests', type_='foreignkey')
    op.drop_table('FOIAssignees')
