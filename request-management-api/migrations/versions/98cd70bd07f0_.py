"""OpenInformation FOIRequest transaction data

Revision ID: 98cd70bd07f0
Revises: 9564370c6c43
Create Date: 2024-08-22 10:54:16.545912

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '98cd70bd07f0'
down_revision = '9564370c6c43'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('FOIOpenInformationRequests',
    sa.Column('foiopeninforequestid', sa.Integer(), autoincrement=True, nullable=False),
    sa.PrimaryKeyConstraint('foiopeninforequestid'),
    sa.Column('foiministryrequest_id', sa.Integer(), nullable=False),
    sa.Column('foiministryrequestversion_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['foiministryrequest_id', 'foiministryrequestversion_id'], ['FOIMinistryRequests.foiministryrequestid', 'FOIMinistryRequests.version']),
    sa.Column('oiexemption_id', sa.Integer(), sa.ForeignKey('OpenInfoExemptions.oiexemptionid'), nullable=True),
    sa.Column('oipublicationstatus_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['oipublicationstatus_id'], ['OpenInfoPublicationStatuses.oipublicationstatusid']),

    sa.Column('oiassignedto', sa.String(), nullable=False),
    sa.Column('pagereference', sa.String), #json object or array or string?
    sa.Column('oiexemptionapproved', sa.Boolean()),
    sa.Column('iaorationale', sa.String()),
    sa.Column('oifeedback', sa.String()),
    sa.Column('publicationdate', sa.DateTime()),
    # sa.Column('version', sa.Integer(), nullabe=False), #NEEDED?
    # sa.Column('isactive', sa.Boolean()), # Needed??

    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('createdby', sa.String(length=120), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('updatedby', sa.String(length=120), nullable=True),
    )

    op.add_column('FOIMinistryRequests', sa.Column('oistatus_id', sa.Integer(), nullable=True, default=False))
    op.create_foreign_key(
    'fk_foiministryrequest_oistatus',
    'FOIMinistryRequests',
    'OpenInfoStatuses',
    ['oistatus_id'],
    ['oistatusid'],
    )

def downgrade():
    op.drop_table('FOIOpenInformationRequests')
    op.drop_constraint('fk_foirequest_oistatus', 'FOIMinistryRequests', type_='foreignkey') 
    op.drop_column('FOIMinistryRequests', 'oistatus_id' )