"""update active templates

Revision ID: 1bda7f7bae57
Revises: 516fbf1b13d9
Create Date: 2024-12-27 10:08:42.751365

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '1bda7f7bae57'
down_revision = '516fbf1b13d9'
branch_labels = None
depends_on = None

def upgrade():
    op.execute('UPDATE public."ApplicantCorrespondenceTemplates" SET display = FALSE, active = FALSE WHERE name IN (\'OIPCAPPLICANTCONSENTEXTENSION\',\'OIPCFIRSTTIMEEXTENSION\',\'OIPCSUBSEQUENTTIMEEXTENSION\',\'EXTENSIONS-PB\',\'GENERICCOVEREMAILTEMPLATE\',\'ACKNOWLEDGEMENTLETTER\');')

def downgrade():
    op.execute('UPDATE public."ApplicantCorrespondenceTemplates" SET display = TRUE, active = TRUE WHERE name IN (\'OIPCAPPLICANTCONSENTEXTENSION\',\'OIPCFIRSTTIMEEXTENSION\',\'OIPCSUBSEQUENTTIMEEXTENSION\',\'EXTENSIONS-PB\',\'GENERICCOVEREMAILTEMPLATE\',\'ACKNOWLEDGEMENTLETTER\');')