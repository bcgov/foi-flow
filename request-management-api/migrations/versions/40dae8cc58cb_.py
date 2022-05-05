"""empty message

Revision ID: 40dae8cc58cb
Revises: 0c235948c759
Create Date: 2022-05-03 11:53:33.379225

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import column, table
from sqlalchemy.sql.sqltypes import Boolean, String


# revision identifiers, used by Alembic.
revision = '40dae8cc58cb'
down_revision = '0c235948c759'
branch_labels = None
depends_on = None


def upgrade():
   
    operatingteams_table = table('OperatingTeams',
                                 column('name',String),
                                 column('description',String),
                                 column('isactive',Boolean),
                                 column('type',String),
                                   )
    op.execute('Truncate table public."OperatingTeams" RESTART IDENTITY CASCADE;commit;')                               
    op.bulk_insert(
        operatingteams_table,
        [
            {'name':'AEST Ministry Team','description':'AEST Ministry Team','type':'ministry','isactive':True},
            {'name':'AGR Ministry Team','description':'AGR Ministry Team','type':'ministry','isactive':True},
            {'name':'AG Ministry Team','description':'AG Ministry Team','type':'ministry','isactive':True},
            {'name':'MCF Ministry Team','description':'MCF Ministry Team','type':'ministry','isactive':True},
            {'name':'CITZ Ministry Team','description':'CITZ Ministry Team','type':'ministry','isactive':True},
            {'name':'EDU Ministry Team','description':'EDU Ministry Team','type':'ministry','isactive':True},
            {'name':'EMLI Ministry Team','description':'EMLI Ministry Team','type':'ministry','isactive':True},
            {'name':'ENV Ministry Team','description':'ENV Ministry Team','type':'ministry','isactive':True},
            {'name':'FIN Ministry Team','description':'FIN Ministry Team','type':'ministry','isactive':True},
            {'name':'FOR Ministry Team','description':'FOR Ministry Team','type':'ministry','isactive':True},
            {'name':'HLTH Ministry Team','description':'HLTH Ministry Team','type':'ministry','isactive':True},
            {'name':'IRR Ministry Team','description':'IRR Ministry Team','type':'ministry','isactive':True},
            {'name':'JERI Ministry Team','description':'JERI Ministry Team','type':'ministry','isactive':True},
            {'name':'LBR Ministry Team','description':'LBR Ministry Team','type':'ministry','isactive':True},
            {'name':'MMHA Ministry Team','description':'MMHA Ministry Team','type':'ministry','isactive':True},
            {'name':'MUNI Ministry Team','description':'MUNI Ministry Team','type':'ministry','isactive':True},
            {'name':'PSSG Ministry Team','description':'PSSG Ministry Team','type':'ministry','isactive':True},
            {'name':'SDPR Ministry Team','description':'SDPR Ministry Team','type':'ministry','isactive':True},
            {'name':'TACS Ministry Team','description':'TACS Ministry Team','type':'ministry','isactive':True},
            {'name':'TRAN Ministry Team','description':'TRAN Ministry Team','type':'ministry','isactive':True},
            {'name':'OCC Ministry Team','description':'OCC Ministry Team','type':'ministry','isactive':True},
            {'name':'PSA Ministry Team','description':'PSA Ministry Team','type':'ministry','isactive':True},
            {'name':'BRD Ministry Team','description':'BRD Ministry Team','type':'ministry','isactive':True},
            {'name':'CLB Ministry Team','description':'CLB Ministry Team','type':'ministry','isactive':True},
            {'name':'CAS Ministry Team','description':'CAS Ministry Team','type':'ministry','isactive':True},
            {'name':'EMBC Ministry Team','description':'EMBC Ministry Team','type':'ministry','isactive':True},
            {'name':'EAO Ministry Team','description':'EAO Ministry Team','type':'ministry','isactive':True},
            {'name':'GCPE Ministry Team','description':'GCPE Ministry Team','type':'ministry','isactive':True},
            {'name':'IIO Ministry Team','description':'IIO Ministry Team','type':'ministry','isactive':True},
            {'name':'PREM Ministry Team','description':'PREM Ministry Team','type':'ministry','isactive':True},
            {'name':'LDB Ministry Team','description':'LDB Ministry Team','type':'ministry','isactive':True},
            {'name':'TIC Ministry Team','description':'TIC Ministry Team','type':'ministry','isactive':True},
            {'name':'OBC Ministry Team','description':'OBC Ministry Team','type':'ministry','isactive':True},
            {'name':'MGC Ministry Team','description':'MGC Ministry Team','type':'ministry','isactive':True},
            {'name':'Scanning Team','description':'Scanning Team','type':'iao','isactive':True},
            {'name':'Business Team','description':'Business Team','type':'iao','isactive':True},
            {'name':'Central Team','description':'Central Team','type':'iao','isactive':True},
            {'name':'Justice Health Team','description':'Justice Health Team','type':'iao','isactive':True},
            {'name':'MCFD Personals Team','description':'MCFD Personals Team','type':'iao','isactive':True},
            {'name':'Resource Team','description':'Resource Team','type':'iao','isactive':True},
            {'name':'Social Tech Team','description':'Social Tech Team','type':'iao','isactive':True},
            {'name':'Intake Team','description':'Intake Team','type':'iao','isactive':True},
            {'name':'Flex Team','description':'Flex Team','type':'iao','isactive':True},
            {'name':'DAS Ministry Team','description':'DAS Ministry Team','type':'ministry','isactive':True},
            {'name':'LWR Ministry Team','description':'LWR Ministry Team','type':'ministry','isactive':True},

        ]
    )

def downgrade():

    operatingteams_table = table('OperatingTeams',
                                 column('name',String),
                                 column('description',String),
                                 column('isactive',Boolean),
                                 column('type',String),
                                   )
    op.execute('Truncate table public."OperatingTeams" RESTART IDENTITY CASCADE;commit;')                               
    op.bulk_insert(
        operatingteams_table,
        [
            {'name':'AEST Ministry Team','description':'AEST Ministry Team','type':'ministry','isactive':True},
            {'name':'AFF Ministry Team','description':'AFF Ministry Team','type':'ministry','isactive':True},
            {'name':'AG Ministry Team','description':'AG Ministry Team','type':'ministry','isactive':True},
            {'name':'MCF Ministry Team','description':'MCF Ministry Team','type':'ministry','isactive':True},
            {'name':'CITZ Ministry Team','description':'CITZ Ministry Team','type':'ministry','isactive':True},
            {'name':'EDUC Ministry Team','description':'EDUC Ministry Team','type':'ministry','isactive':True},
            {'name':'EMLI Ministry Team','description':'EMLI Ministry Team','type':'ministry','isactive':True},
            {'name':'ENV Ministry Team','description':'ENV Ministry Team','type':'ministry','isactive':True},
            {'name':'FIN Ministry Team','description':'FIN Ministry Team','type':'ministry','isactive':True},
            {'name':'FLNR Ministry Team','description':'FLNR Ministry Team','type':'ministry','isactive':True},
            {'name':'HLTH Ministry Team','description':'HLTH Ministry Team','type':'ministry','isactive':True},
            {'name':'IRR Ministry Team','description':'IRR Ministry Team','type':'ministry','isactive':True},
            {'name':'JERI Ministry Team','description':'JERI Ministry Team','type':'ministry','isactive':True},
            {'name':'LBR Ministry Team','description':'LBR Ministry Team','type':'ministry','isactive':True},
            {'name':'MMHA Ministry Team','description':'MMHA Ministry Team','type':'ministry','isactive':True},
            {'name':'MUNI Ministry Team','description':'MUNI Ministry Team','type':'ministry','isactive':True},
            {'name':'PSSG Ministry Team','description':'PSSG Ministry Team','type':'ministry','isactive':True},
            {'name':'SDPR Ministry Team','description':'SDPR Ministry Team','type':'ministry','isactive':True},
            {'name':'TACS Ministry Team','description':'TACS Ministry Team','type':'ministry','isactive':True},
            {'name':'TRAN Ministry Team','description':'TRAN Ministry Team','type':'ministry','isactive':True},
            {'name':'OCC Ministry Team','description':'OCC Ministry Team','type':'ministry','isactive':True},
            {'name':'PSA Ministry Team','description':'PSA Ministry Team','type':'ministry','isactive':True},
            {'name':'BRD Ministry Team','description':'BRD Ministry Team','type':'ministry','isactive':True},
            {'name':'CLB Ministry Team','description':'CLB Ministry Team','type':'ministry','isactive':True},
            {'name':'CAS Ministry Team','description':'CAS Ministry Team','type':'ministry','isactive':True},
            {'name':'EMBC Ministry Team','description':'EMBC Ministry Team','type':'ministry','isactive':True},
            {'name':'EAO Ministry Team','description':'EAO Ministry Team','type':'ministry','isactive':True},
            {'name':'GCPE Ministry Team','description':'GCPE Ministry Team','type':'ministry','isactive':True},
            {'name':'IIO Ministry Team','description':'IIO Ministry Team','type':'ministry','isactive':True},
            {'name':'PREM Ministry Team','description':'PREM Ministry Team','type':'ministry','isactive':True},
            {'name':'LDB Ministry Team','description':'LDB Ministry Team','type':'ministry','isactive':True},
            {'name':'TIC Ministry Team','description':'TIC Ministry Team','type':'ministry','isactive':True},
            {'name':'OBC Ministry Team','description':'OBC Ministry Team','type':'ministry','isactive':True},
            {'name':'MGC Ministry Team','description':'MGC Ministry Team','type':'ministry','isactive':True},
            {'name':'Scanning Team','description':'Scanning Team','type':'iao','isactive':True},
            {'name':'Business Team','description':'Business Team','type':'iao','isactive':True},
            {'name':'Central Team','description':'Central Team','type':'iao','isactive':True},
            {'name':'Justice Health Team','description':'Justice Health Team','type':'iao','isactive':True},
            {'name':'MCFD Personals Team','description':'MCFD Personals Team','type':'iao','isactive':True},
            {'name':'Resource Team','description':'Resource Team','type':'iao','isactive':True},
            {'name':'Social Tech Team','description':'Social Tech Team','type':'iao','isactive':True},
            {'name':'Intake Team','description':'Intake Team','type':'iao','isactive':True},
            {'name':'Flex Team','description':'Flex Team','type':'iao','isactive':True},

        ]
    )
