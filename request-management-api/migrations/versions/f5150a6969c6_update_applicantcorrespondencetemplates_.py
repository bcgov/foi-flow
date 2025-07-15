"""Update ApplicantCorrespondenceTemplates uripath

Revision ID: f5150a6969c6
Revises: b37c4c21e1ab
Create Date: 2025-07-15 10:31:55.948739

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'f5150a6969c6'
down_revision = 'b37c4c21e1ab'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('UPDATE public."ApplicantCorrespondenceTemplates" SET documenturipath = \'/TEMPLATES/EMAILS/SYNCFUSION/fee_estimate_notification_sf.html\' WHERE documenturipath = \'/TEMPLATES/EMAILS/fee_estimate_notification.html\';commit;')
    op.execute('UPDATE public."ApplicantCorrespondenceTemplates" SET documenturipath = \'/TEMPLATES/EMAILS/SYNCFUSION/fee_estimate_notification_outstanding_sf.html\' WHERE documenturipath = \'/TEMPLATES/EMAILS/fee_estimate_notification_outstanding.html\';commit;')
    op.execute('UPDATE public."ApplicantCorrespondenceTemplates" SET documenturipath = \'/TEMPLATES/EMAILS/SYNCFUSION/fee_payment_confirmation_full_sf.html\' WHERE documenturipath = \'/TEMPLATES/EMAILS/fee_payment_confirmation_full.html\';commit;')
    op.execute('UPDATE public."ApplicantCorrespondenceTemplates" SET documenturipath = \'/TEMPLATES/EMAILS/SYNCFUSION/fee_payment_confirmation_half_sf.html\' WHERE documenturipath = \'/TEMPLATES/EMAILS/fee_payment_confirmation_half.html\';commit;')
    op.execute('UPDATE public."ApplicantCorrespondenceTemplates" SET documenturipath = \'/TEMPLATES/EMAILS/SYNCFUSION/fee_payment_confirmation_outstanding_sf.html\' WHERE documenturipath = \'/TEMPLATES/EMAILS/fee_payment_confirmation_outstanding.html\';commit;')
    op.execute('UPDATE public."ApplicantCorrespondenceTemplates" SET documenturipath = \'/TEMPLATES/EMAILS/SYNCFUSION/oipc_applicant_consent_time_extension_sf.html\' WHERE documenturipath = \'/TEMPLATES/EMAILS/oipc_applicant_consent_time_extension.html\';commit;')
    op.execute('UPDATE public."ApplicantCorrespondenceTemplates" SET documenturipath = \'/TEMPLATES/EMAILS/SYNCFUSION/oipc_first_time_extension_sf.html\' WHERE documenturipath = \'/TEMPLATES/EMAILS/oipc_first_time_extension.html\';commit;')
    op.execute('UPDATE public."ApplicantCorrespondenceTemplates" SET documenturipath = \'/TEMPLATES/EMAILS/SYNCFUSION/oipc_subsequent_time_extension_sf.html\' WHERE documenturipath = \'/TEMPLATES/EMAILS/oipc_subsequent_time_extension.html\';commit;')
    op.execute('UPDATE public."ApplicantCorrespondenceTemplates" SET documenturipath = \'/TEMPLATES/EMAILS/SYNCFUSION/extension_pb_sf.html\' WHERE documenturipath = \'/TEMPLATES/EMAILS/extension_pb.html\';commit;')
    op.execute('UPDATE public."ApplicantCorrespondenceTemplates" SET documenturipath = \'/TEMPLATES/EMAILS/SYNCFUSION/generic_cover_email_template_sf.html\' WHERE documenturipath = \'/TEMPLATES/EMAILS/generic_cover_email_template.html\';commit;')
    op.execute('UPDATE public."ApplicantCorrespondenceTemplates" SET documenturipath = \'/TEMPLATES/EMAILS/SYNCFUSION/acknowledgement_letter_sf.html\' WHERE documenturipath = \'/TEMPLATES/EMAILS/acknowledgement_letter.html\';commit;')

def downgrade():
    op.execute('UPDATE public."ApplicantCorrespondenceTemplates" SET documenturipath = \'/TEMPLATES/EMAILS/fee_estimate_notification.html\' WHERE documenturipath = \'/TEMPLATES/EMAILS/SYNCFUSION/fee_estimate_notification_sf.html\';commit;')
    op.execute('UPDATE public."ApplicantCorrespondenceTemplates" SET documenturipath = \'/TEMPLATES/EMAILS/fee_estimate_notification_outstanding.html\' WHERE documenturipath = \'/TEMPLATES/EMAILS/SYNCFUSION/fee_estimate_notification_outstanding_sf.html\';commit;')
    op.execute('UPDATE public."ApplicantCorrespondenceTemplates" SET documenturipath = \'/TEMPLATES/EMAILS/fee_payment_confirmation_full.html\' WHERE documenturipath = \'/TEMPLATES/EMAILS/SYNCFUSION/fee_payment_confirmation_full_sf.html\';commit;')
    op.execute('UPDATE public."ApplicantCorrespondenceTemplates" SET documenturipath = \'/TEMPLATES/EMAILS/fee_payment_confirmation_half.html\' WHERE documenturipath = \'/TEMPLATES/EMAILS/SYNCFUSION/fee_payment_confirmation_half_sf.html\';commit;')
    op.execute('UPDATE public."ApplicantCorrespondenceTemplates" SET documenturipath = \'/TEMPLATES/EMAILS/fee_payment_confirmation_outstanding.html\' WHERE documenturipath = \'/TEMPLATES/EMAILS/SYNCFUSION/fee_payment_confirmation_outstanding_sf.html\';commit;')
    op.execute('UPDATE public."ApplicantCorrespondenceTemplates" SET documenturipath = \'/TEMPLATES/EMAILS/oipc_applicant_consent_time_extension.html\' WHERE documenturipath = \'/TEMPLATES/EMAILS/SYNCFUSION/oipc_applicant_consent_time_extension_sf.html\';commit;')
    op.execute('UPDATE public."ApplicantCorrespondenceTemplates" SET documenturipath = \'/TEMPLATES/EMAILS/oipc_first_time_extension.html\' WHERE documenturipath = \'/TEMPLATES/EMAILS/SYNCFUSION/oipc_first_time_extension_sf.html\';commit;')
    op.execute('UPDATE public."ApplicantCorrespondenceTemplates" SET documenturipath = \'/TEMPLATES/EMAILS/oipc_subsequent_time_extension.html\' WHERE documenturipath = \'/TEMPLATES/EMAILS/SYNCFUSION/oipc_subsequent_time_extension_sf.html\';commit;')
    op.execute('UPDATE public."ApplicantCorrespondenceTemplates" SET documenturipath = \'/TEMPLATES/EMAILS/extension_pb.html\' WHERE documenturipath = \'/TEMPLATES/EMAILS/SYNCFUSION/extension_pb_sf.html\';commit;')
    op.execute('UPDATE public."ApplicantCorrespondenceTemplates" SET documenturipath = \'/TEMPLATES/EMAILS/generic_cover_email_template.html\' WHERE documenturipath = \'/TEMPLATES/EMAILS/SYNCFUSION/generic_cover_email_template_sf.html\';commit;')
    op.execute('UPDATE public."ApplicantCorrespondenceTemplates" SET documenturipath = \'/TEMPLATES/EMAILS/acknowledgement_letter.html\' WHERE documenturipath = \'/TEMPLATES/EMAILS/SYNCFUSION/acknowledgement_letter_sf.html\';commit;')