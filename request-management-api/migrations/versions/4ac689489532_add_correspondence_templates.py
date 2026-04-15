"""Add correspondence templates

Revision ID: 4ac689489532
Revises: 5ba80deacf94
Create Date: 2026-04-14 15:39:49.996483

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '4ac689489532'
down_revision = '5ba80deacf94'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('INSERT INTO "public"."Template" ("templatetype", "filename", "templatename", "extension", "isactive", "requesttype", "documentpath", "encodedcontent", "createdby", "createdat", "updatedby", "updatedat") VALUES (\'letter\', \'PAckIndividualOutofProvinceorCountry\', \'P - Ack - Individual - Out of Province or Country\', \'.docx\', TRUE, \'Both\', \'/TEMPLATES/EMAILS/SYNCFUSION/P - Ack - Individual - Out of Province or Country.docx\', \'\', -1, NOW(), NULL, NULL);commit;')
    op.execute('INSERT INTO "public"."Template" ("templatetype", "filename", "templatename", "extension", "isactive", "requesttype", "documentpath", "encodedcontent", "createdby", "createdat", "updatedby", "updatedat") VALUES (\'letter\', \'PMSDCFR\', \'P - MSD CFR\', \'.docx\', TRUE, \'Both\', \'/TEMPLATES/EMAILS/SYNCFUSION/P - MSD CFR.docx\', \'\', -1, NOW(), NULL, NULL);commit;')


def downgrade():
    op.execute('DELETE FROM "public"."Template" WHERE "templatename" = \'P - Ack - Individual - Out of Province or Country\';')
    op.execute('DELETE FROM "public"."Template" WHERE "templatename" = \'P - MSD CFR\';')