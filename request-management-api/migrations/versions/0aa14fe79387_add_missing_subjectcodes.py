"""Add missing Subject Codes

Revision ID: 0aa14fe79387
Revises: b863a277c491
Create Date: 2023-06-02 12:31:21.787571

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import column, table
from sqlalchemy.sql.sqltypes import Boolean, String


# revision identifiers, used by Alembic.
revision = '0aa14fe79387'
down_revision = 'b863a277c491'
branch_labels = None
depends_on = None


def upgrade():
    subjectcodes_table = table('SubjectCodes',
                                 column('name',String),
                                 column('description',String),
                                 column('isaxissubjectcode',Boolean),
                                 column('isactive',Boolean),
                                )

    op.bulk_insert(
        subjectcodes_table,
        [
            {'name':'Child Services/Foster Care','description':'Child Services/Foster Care','isaxissubjectcode':True,'isactive':True},
            {'name':'MOU-Adoption','description':'MOU-Adoption','isaxissubjectcode':True,'isactive':True},
            {'name':'MOU-Child Protection','description':'MOU-Child Protection','isaxissubjectcode':True,'isactive':True},
            {'name':'MOU-Class Action','description':'MOU-Class Action','isaxissubjectcode':True,'isactive':True},
            {'name':'MOU-Foster/Resource','description':'MOU-Foster/Resource','isaxissubjectcode':True,'isactive':True},
            {'name':'MOU-Medical or Health Records','description':'MOU-Medical or Health Records','isaxissubjectcode':True,'isactive':True},
        ]
    )  


def downgrade():
    op.execute('DELETE FROM public."SubjectCodes" WHERE name =\'Child Services/Foster Care\';commit;')
    op.execute('DELETE FROM public."SubjectCodes" WHERE name =\'MOU-Adoption\';commit;')
    op.execute('DELETE FROM public."SubjectCodes" WHERE name =\'MOU-Child Protection\';commit;')
    op.execute('DELETE FROM public."SubjectCodes" WHERE name =\'MOU-Class Action\';commit;')
    op.execute('DELETE FROM public."SubjectCodes" WHERE name =\'MOU-Foster/Resource\';commit;')
    op.execute('DELETE FROM public."SubjectCodes" WHERE name =\'MOU-Medical or Health Records\';commit;')
