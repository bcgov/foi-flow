"""empty message

Revision ID: b659546dc7e4
Revises: e74deec1b00b
Create Date: 2021-08-09 14:31:20.896721

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import column, table
from sqlalchemy.sql.sqltypes import Boolean, String

# revision identifiers, used by Alembic.
revision = 'b659546dc7e4'
down_revision = 'e74deec1b00b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###

    contacttype_table = table('ContactTypes',
                                 column('name',String),
                                 column('description',String),
                                 column('isactive',Boolean),
                                   )
    op.execute('Truncate table public."ContactTypes" RESTART IDENTITY CASCADE;commit;')                               
    op.bulk_insert(
        contacttype_table,
        [
            {'name':'Email','description':'Email','isactive':True},
            {'name':'Street Address','description':'Street Address','isactive':True},
            {'name':'Home Phone','description':'Home Phone','isactive':True},
            {'name':'Work Phone','description':'Work Phone','isactive':True},
            {'name':'Work Phone 2','description':'second work phone 2','isactive':True},
            {'name':'Mobile Phone','description':'Mobile Phone','isactive':True},
            {'name':'Other','description':'Other Contact information, if any','isactive':True},
        ]
    )

    op.create_table('FOIRequestContactInformation',
    sa.Column('foirequestcontactid', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('contactinformation', sa.String(length=500), nullable=False),
    sa.Column('dataformat', sa.String(length=40), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('createdby', sa.String(length=120), nullable=True),
    sa.Column('updatedby', sa.String(length=120), nullable=True),
    sa.Column('contacttypeid', sa.Integer(), nullable=True),
    sa.Column('foirequest_id', sa.Integer(), nullable=True),
    sa.Column('foirequestversion_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['contacttypeid'], ['ContactTypes.contacttypeid'], ),
    sa.ForeignKeyConstraint(['foirequest_id', 'foirequestversion_id'], ['FOIRequests.foirequestid', 'FOIRequests.version'], ),
    sa.PrimaryKeyConstraint('foirequestcontactid')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute('Truncate table public."ContactTypes" RESTART IDENTITY CASCADE;commit;')
    op.drop_table('FOIRequestContactInformation')
    # ### end Alembic commands ###
