"""Update template name

Revision ID: 8c4b76110854
Revises: 4ac689489532
Create Date: 2026-05-25 10:36:58.435825

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '8c4b76110854'
down_revision = '4ac689489532'
branch_labels = None
depends_on = None


def upgrade():
    # Template
    op.execute("""UPDATE "Template" 
            SET templatename = 'P - Request for Location under s27(1)(e) and s33(2)(k)', 
                documentpath = '/TEMPLATES/EMAILS/SYNCFUSION/P - Request for Location under s27(1)(e) and s33(2)(k).docx' 
            WHERE templatename = 'P - Request for Location under s27(1)(e) and s33 2(d)';""")
    
    # TemplateFieldMappings
    op.execute('INSERT INTO "public"."TemplateFieldMapping" ("fieldname", "fieldtype", "fieldmapping", "isactive", "createdby", "createdat", "updatedby", "updatedat") VALUES (\'[REQUESTSTARTDATE]\', \'String\', \'[REQUESTSTARTDATE]\', \'True\', \'-1\', NOW(), NULL, NULL);commit;')
    op.execute('INSERT INTO "public"."TemplateFieldMapping" ("fieldname", "fieldtype", "fieldmapping", "isactive", "createdby", "createdat", "updatedby", "updatedat") VALUES (\'[PUBLICATIONSTATUS]\', \'String\', \'[PUBLICATIONSTATUS]\', \'True\', \'-1\', NOW(), NULL, NULL);commit;')
    op.execute('INSERT INTO "public"."TemplateFieldMapping" ("fieldname", "fieldtype", "fieldmapping", "isactive", "createdby", "createdat", "updatedby", "updatedat") VALUES (\'[DONOTPUBLISHREASON]\', \'String\', \'[DONOTPUBLISHREASON]\', \'True\', \'-1\', NOW(), NULL, NULL);commit;')
    op.execute('INSERT INTO "public"."TemplateFieldMapping" ("fieldname", "fieldtype", "fieldmapping", "isactive", "createdby", "createdat", "updatedby", "updatedat") VALUES (\'[BRANCH]\', \'String\', \'[BRANCH]\', \'True\', \'-1\', NOW(), NULL, NULL);commit;')


def downgrade():
    # Template
    op.execute("""
        UPDATE "Template" 
        SET templatename = 'P - Request for Location under s27(1)(e) and s33 2(d)', 
            documentpath = '/TEMPLATES/EMAILS/SYNCFUSION/P - Request for Location under s27(1)(e) and s33 2(d).docx'
        WHERE templatename = 'P - Request for Location under s27(1)(e) and s33(2)(k)';""")
    
    # TemplateFieldMappings
    op.execute('DELETE FROM "public"."TemplateFieldMapping" WHERE fieldname = \'[REQUESTSTARTDATE]\';commit;')
    op.execute('DELETE FROM "public"."TemplateFieldMapping" WHERE fieldname = \'[PUBLICATIONSTATUS]\';commit;')
    op.execute('DELETE FROM "public"."TemplateFieldMapping" WHERE fieldname = \'[DONOTPUBLISHREASON]\';commit;')
    op.execute('DELETE FROM "public"."TemplateFieldMapping" WHERE fieldname = \'[BRANCH]\';commit;')