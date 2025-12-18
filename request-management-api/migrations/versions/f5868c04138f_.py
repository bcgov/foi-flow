"""empty message

Revision ID: f5868c04138f
Revises: 83ce6c30feec
Create Date: 2021-08-09 16:25:55.535544

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import column, table
from sqlalchemy.sql.sqltypes import Boolean, String


# revision identifiers, used by Alembic.
revision = 'f5868c04138f'
down_revision = '83ce6c30feec'
branch_labels = None
depends_on = None


def upgrade():
    personalattributes_table = table('PersonalInformationAttributes',
                                 column('name',String),
                                 column('description',String),
                                 column('isactive',Boolean),
                                   )
    op.execute('Truncate table public."PersonalInformationAttributes" RESTART IDENTITY CASCADE;commit;')                               
    op.bulk_insert(
        personalattributes_table,
        [
            {'name':'BC Public Service Employee Number','description':'BC Public Service Employee Number','isactive':True},
            {'name':'BC Correctional Service Number','description':'BC Correctional Service Number','isactive':True},
            {'name':'BC Personal Health Care Number','description':'BC Personal Health Care Number','isactive':True},
            {'name':'Adoptive Mother First Name','description':'Adoptive Mother First Name','isactive':True},
            {'name':'Adoptive Mother Last Name','description':'Adoptive Mother First Name','isactive':True},
            {'name':'Adoptive Father First Name','description':'Adoptive Mother First Name','isactive':True},
            {'name':'Adoptive Father Last Name','description':'Adoptive Mother First Name','isactive':True}
        ]
    )


def downgrade():
    op.execute('Truncate table public."PersonalInformationAttributes" RESTART IDENTITY CASCADE;commit;')
