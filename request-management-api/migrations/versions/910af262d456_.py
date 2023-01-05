"""empty message

Revision ID: 910af262d456
Revises: 10daedc23a0d
Create Date: 2023-01-03 13:22:56.352319

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '910af262d456'
down_revision = '10daedc23a0d'
branch_labels = None
depends_on = None


def upgrade():
    subjectcodes = op.create_table('SubjectCodes',
    sa.Column('subjectcodeid', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.Column('isaxissubjectcode', sa.Boolean(), nullable=False),
    sa.Column('isactive', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('subjectcodeid')
    )
    # Bulk insert SubjectCodes records.
    op.bulk_insert(
        subjectcodes,
        [
            {'name':'Adoption','description':'Adoption','isaxissubjectcode':True,'isactive':True},
            {'name':'BC Prosecution Service','description':'BC Prosecution Service','isaxissubjectcode':True,'isactive':True},
            {'name':'BC Services Card','description':'BC Services Card','isaxissubjectcode':True,'isactive':True},
            {'name':'BC Tech','description':'BC Tech','isaxissubjectcode':True,'isactive':True},
            {'name':'Birth Alerts','description':'Birth Alerts','isaxissubjectcode':True,'isactive':True},
            {'name':'Calendar','description':'Calendar','isaxissubjectcode':True,'isactive':True},
            {'name':'Child Protection','description':'Child Protection','isaxissubjectcode':True,'isactive':True},
            {'name':'Class Action','description':'Class Action','isaxissubjectcode':True,'isactive':True},
            {'name':'CLBC Records','description':'CLBC Records','isaxissubjectcode':True,'isactive':True},
            {'name':'Complaint or Investigation Records','description':'Complaint or Investigation Records','isaxissubjectcode':True,'isactive':True},
            {'name':'Core Review','description':'Core Review','isaxissubjectcode':True,'isactive':True},
            {'name':'Coroners Service','description':'Coroners Service','isaxissubjectcode':True,'isactive':True},
            {'name':'Corrections Branch','description':'Corrections Branch','isaxissubjectcode':True,'isactive':True},
            {'name':'Court Services Branch','description':'Court Services Branch','isaxissubjectcode':True,'isactive':True},
            {'name':'COVID 19','description':'COVID 19','isaxissubjectcode':True,'isactive':True},
            {'name':'Crime Victim Services Program','description':'Crime Victim Services Program','isaxissubjectcode':True,'isactive':True},
            {'name':'Criminal Justice Branch','description':'Criminal Justice Branch','isaxissubjectcode':True,'isactive':True},
            {'name':'CYSN','description':'CYSN','isaxissubjectcode':True,'isactive':True},
            {'name':'Daycare Subsidy','description':'Daycare Subsidy','isaxissubjectcode':True,'isactive':True},
            {'name':'Email Correspondence','description':'Email Correspondence','isaxissubjectcode':True,'isactive':True},
            {'name':'Employment Records','description':'Employment Records','isaxissubjectcode':True,'isactive':True},
            {'name':'Estimates Notes','description':'Estimates Notes','isaxissubjectcode':True,'isactive':True},
            {'name':'F15-03','description':'F15-03','isaxissubjectcode':True,'isactive':True},
            {'name':'Family Maintenance Program','description':'Family Maintenance Program','isaxissubjectcode':True,'isactive':True},
            {'name':'FIFA','description':'FIFA','isaxissubjectcode':True,'isactive':True},
            {'name':'Foster/Resource','description':'Foster/Resource','isaxissubjectcode':True,'isactive':True},
            {'name':'Gaming','description':'Gaming','isaxissubjectcode':True,'isactive':True},
            {'name':'Housing','description':'Housing','isaxissubjectcode':True,'isactive':True},
            {'name':'Income Assistance','description':'Income Assistance','isaxissubjectcode':True,'isactive':True},
            {'name':'Integrated Case Management','description':'Integrated Case Management','isaxissubjectcode':True,'isactive':True},
            {'name':'Investigations and Standards Office','description':'Investigations and Standards Office','isaxissubjectcode':True,'isactive':True},
            {'name':'LEAN','description':'LEAN','isaxissubjectcode':True,'isactive':True},
            {'name':'Legal Services Branch','description':'Legal Services Branch','isaxissubjectcode':True,'isactive':True},
            {'name':'Liquefied Natural Gas','description':'Liquefied Natural Gas','isaxissubjectcode':True,'isactive':True},
            {'name':'Liquor','description':'Liquor','isaxissubjectcode':True,'isactive':True},
            {'name':'Medical or Health Records','description':'Medical or Health Records','isaxissubjectcode':True,'isactive':True},
            {'name':'Message Tracking Logs','description':'Message Tracking Logs','isaxissubjectcode':True,'isactive':True},
            {'name':'Mount Polley','description':'Mount Polley','isaxissubjectcode':True,'isactive':True},
            {'name':'Northern Gateway (Enbridge)','description':'Northern Gateway (Enbridge)','isaxissubjectcode':True,'isactive':True},
            {'name':'Outreach and Investigation','description':'Outreach and Investigation','isaxissubjectcode':True,'isactive':True},
            {'name':'Personal Email','description':'Personal Email','isaxissubjectcode':True,'isactive':True},
            {'name':'Personal Information','description':'Personal Information','isaxissubjectcode':True,'isactive':True},
            {'name':'Personnel','description':'Personnel','isaxissubjectcode':True,'isactive':True},
            {'name':'PHSA Medical','description':'PHSA Medical','isaxissubjectcode':True,'isactive':True},
            {'name':'Police Services','description':'Police Services','isaxissubjectcode':True,'isactive':True},
            {'name':'Processing File','description':'Processing File','isaxissubjectcode':True,'isactive':True},
            {'name':'Project - Adoption','description':'Project - Adoption','isaxissubjectcode':True,'isactive':True},
            {'name':'Project - Child Protection','description':'Project - Child Protection','isaxissubjectcode':True,'isactive':True},
            {'name':'Project - Class Action','description':'Project - Class Action','isaxissubjectcode':True,'isactive':True},
            {'name':'Project - Foster/Resource','description':'Project - Foster/Resource','isaxissubjectcode':True,'isactive':True},
            {'name':'Project - Medical or Health Records','description':'Project - Medical or Health Records','isaxissubjectcode':True,'isactive':True},
            {'name':'Project - Personal Information','description':'Project - Personal Information','isaxissubjectcode':True,'isactive':True},
            {'name':'Property Transfer Tax','description':'Property Transfer Tax','isaxissubjectcode':True,'isactive':True},
            {'name':'Property/Asset Sales','description':'Property/Asset Sales','isaxissubjectcode':True,'isactive':True},
            {'name':'Prosecutions','description':'Prosecutions','isaxissubjectcode':True,'isactive':True},
            {'name':'Provincial Nominee Program','description':'Provincial Nominee Program','isaxissubjectcode':True,'isactive':True},
            {'name':'PSD Investigation','description':'PSD Investigation','isaxissubjectcode':True,'isactive':True},
            {'name':'Redirect','description':'Redirect','isaxissubjectcode':True,'isactive':True},
            {'name':'Residential Schools','description':'Residential Schools','isaxissubjectcode':True,'isactive':True},
            {'name':'Residential Tenancy Branch','description':'Residential Tenancy Branch','isaxissubjectcode':True,'isactive':True},
            {'name':'Resignation','description':'Resignation','isaxissubjectcode':True,'isactive':True},
            {'name':'Response Package','description':'Response Package','isaxissubjectcode':True,'isactive':True},
            {'name':'RoadSafetyBC','description':'RoadSafetyBC','isaxissubjectcode':True,'isactive':True},
            {'name':'Royal BC Museum','description':'Royal BC Museum','isaxissubjectcode':True,'isactive':True},
            {'name':'Security Programs','description':'Security Programs','isaxissubjectcode':True,'isactive':True},
            {'name':'Site C','description':'Site C','isaxissubjectcode':True,'isactive':True},
            {'name':'Speculation Tax','description':'Speculation Tax','isaxissubjectcode':True,'isactive':True},
            {'name':'Student Loan or Educational Records','description':'Student Loan or Educational Records','isaxissubjectcode':True,'isactive':True},
            {'name':'Trans Mountain (Kinder Morgan)','description':'Trans Mountain (Kinder Morgan)','isaxissubjectcode':True,'isactive':True},
            {'name':'Transition Binders','description':'Transition Binders','isaxissubjectcode':True,'isactive':True},
            {'name':'Undetermined','description':'Undetermined','isaxissubjectcode':True,'isactive':True},
            {'name':'Wildfires','description':'Wildfires','isaxissubjectcode':True,'isactive':True},
        ]
    )

    op.create_table('FOIMinistryRequestSubjectCodes',
    sa.Column('foiministrysubjectcodeid', sa.Integer(), autoincrement=True, nullable=False),    
    sa.Column('subjectcodeid',  sa.Integer(), nullable=False),
    sa.Column('foiministryrequestid', sa.Integer(), nullable=False),
    sa.Column('foiministryrequestversion', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('createdby', sa.String(length=120), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('updatedby', sa.String(length=120), nullable=True), 
    sa.ForeignKeyConstraint(['subjectcodeid'], ['SubjectCodes.subjectcodeid'], ),
    sa.ForeignKeyConstraint(['foiministryrequestid','foiministryrequestversion'], ['FOIMinistryRequests.foiministryrequestid', 'FOIMinistryRequests.version'], ),
    sa.PrimaryKeyConstraint('foiministrysubjectcodeid')
    )

def downgrade():
    op.drop_table('FOIMinistryRequestSubjectCodes')
    op.drop_table('SubjectCodes')
