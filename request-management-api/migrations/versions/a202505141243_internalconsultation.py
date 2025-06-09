"""empty message

Revision ID: a202505141243
Revises: 3afc864e6815
Create Date: 2025-05-14 12:22:08.177238

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a202505141243'
down_revision = '3afc864e6815'
branch_labels = None
depends_on = None


def upgrade():
    # Create FOIConsultTypes table
    foiconsulttype_table = op.create_table(
        'FOIMinistryRequestConsultTypes',
        sa.Column('consulttypeid', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('isactive', sa.Boolean())
    )

    # Insert initial types
    op.bulk_insert(
        foiconsulttype_table,
        [
            {'consulttypeid': 1, 'name': 'Internal'},
            {'consulttypeid': 2, 'name': 'External'}
        ]
    )

    # Create FOIMinistryRequestConsults table
    op.create_table('FOIMinistryRequestConsults',
    sa.Column('foiministryrequestconsultid', sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
    sa.Column('version', sa.Integer(), primary_key=True, nullable=False),
    sa.Column('foiministryrequest_id', sa.Integer(), nullable=False),
    sa.Column('foiministryrequestversion_id', sa.Integer(), nullable=False),
    sa.Column('filenumber', sa.String(length=50), nullable=False),
    sa.Column('consultassignedto', sa.String(length=120), nullable=True),
    sa.Column('assignedgroup', sa.String(length=120), nullable=True),
    sa.Column('assignedministryperson', sa.String(length=120), nullable=True),
    sa.Column('assignedministrygroup', sa.String(length=120), nullable=True),
    sa.Column('requeststatusid', sa.Integer(), nullable=True),
    sa.Column('consulttypeid', sa.Integer(), nullable=False),
    sa.Column('programareaid', sa.Integer(), nullable=False),
    sa.Column('consultsubjectcode', sa.String(length=50), nullable=True),
    sa.Column('consultduedate', sa.Date(), nullable=False),
    sa.Column('closedate', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('createdby', sa.String(length=120), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('updatedby', sa.String(length=120), nullable=True),
    sa.Column('isactive', sa.Boolean()),
    sa.ForeignKeyConstraint(['foiministryrequest_id', 'foiministryrequestversion_id'], ['FOIMinistryRequests.foiministryrequestid', 'FOIMinistryRequests.version']),
    sa.ForeignKeyConstraint(['programareaid'], ['ProgramAreas.programareaid']),
    sa.ForeignKeyConstraint(['requeststatusid'], ['FOIRequestStatuses.requeststatusid'], ),
    sa.ForeignKeyConstraint(['consulttypeid'], ['FOIMinistryRequestConsultTypes.consulttypeid']),
    sa.PrimaryKeyConstraint('foiministryrequestconsultid')
    ) 


def downgrade():
    op.drop_table('FOIMinistryRequestConsults')
    op.drop_table('FOIMinistryRequestConsultTypes')

