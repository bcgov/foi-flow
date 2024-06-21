"""empty message

Revision ID: 7583b5428c87
Revises: c3e447d3d94d
Create Date: 2024-06-19 15:29:08.420315

"""
from alembic import op
from datetime import datetime
import sqlalchemy as sa
from sqlalchemy.sql import column, table
from sqlalchemy.sql.sqltypes import Boolean, String,Text,Integer,DateTime


# revision identifiers, used by Alembic.
revision = '7583b5428c87'
down_revision = 'c3e447d3d94d'
branch_labels = None
depends_on = None


def upgrade():
    applicant_correspondence_templates = table('ApplicantCorrespondenceTemplates',
                                 column('name',String),
                                 column('documenturipath',Text),
                                 column('description',String),
                                 column('active',Boolean),
                                 column('display',Boolean),
                                 column('version',Integer),
                                 column('created_at',DateTime),
                                 column('createdby',String),
                                   )
    op.bulk_insert(
        applicant_correspondence_templates,
        {'name': 'OIPCAPPLICANTCONSENTEXTENSION',
             'description': 'OIPC Applicant Consent Time Extension',
             'active': True,
             'display': True,
             'version': 1,
             'documenturipath': '/TEMPLATES/EMAILS/oipc_applicant_consent_time_extension.html',
             'created_at': datetime.now(),
             'createdby': 'system'},
             {'name': 'OIPCFIRSTTIMEEXTENSION',
             'description': 'OIPC Applicant First Time Extension',
             'active': True,
             'display': True,
             'version': 1,
             'documenturipath': '/TEMPLATES/EMAILS/oipc_first_time_extension.html',
             'created_at': datetime.now(),
             'createdby': 'system'},
             {'name': 'OIPCSUBSEQUENTTIMEEXTENSION',
             'description': 'OIPC Subsequent Time Extension',
             'active': True,
             'display': True,
             'version': 1,
             'documenturipath': '/TEMPLATES/EMAILS/oipc_subsequent_time_extension.html',
             'created_at': datetime.now(),
             'createdby': 'system'},
    )


def downgrade():
    op.execute(
        "DELETE FROM ApplicantCorrespondenceTemplates WHERE name = 'OIPCAPPLICANTCONSENTEXTENSION'"
    )
