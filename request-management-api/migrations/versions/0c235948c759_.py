"""empty message

Revision ID: 0c235948c759
Revises: 688bd7c77b01
Create Date: 2022-05-02 13:00:55.126582

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import column, table
from sqlalchemy.sql.sqltypes import Boolean, String


# revision identifiers, used by Alembic.
revision = '0c235948c759'
down_revision = '688bd7c77b01'
branch_labels = None
depends_on = None


def upgrade():
    ##Program Areas Data Insertion
    programareas_table = table('ProgramAreas',
                                 column('name',String),
                                 column('type',String),
                                 column('isactive',Boolean),
                                 column('bcgovcode',String),
                                 column('iaocode',String),
                                   )
    op.execute('Truncate table public."ProgramAreas" RESTART IDENTITY CASCADE;commit;')                               
    op.bulk_insert(
        programareas_table,
        [
            {'name':'Ministry of Advanced Education and Skills Training','type':'BC GOV Ministry','isactive':True,'bcgovcode':'AEST','iaocode':'AED'},
            {'name':'Ministry of Agriculture and Food','type':'BC GOV Ministry','isactive':True,'bcgovcode':'AGR','iaocode':'AGR'},
            {'name':'Ministry of Attorney General','type':'BC GOV Ministry','isactive':True,'bcgovcode':'AG','iaocode':'MAG'},
            {'name':'Ministry of Children and Family Development','type':'BC GOV Ministry','isactive':True,'bcgovcode':'MCF','iaocode':'CFD'},
            {'name':'Ministry of Citizens’ Services','type':'BC GOV Ministry','isactive':True,'bcgovcode':'CITZ','iaocode':'CTZ'},
            {'name':'Ministry of Education and Childcare','type':'BC GOV Ministry','isactive':True,'bcgovcode':'EDU','iaocode':'EDU'},
            {'name':'Ministry of Energy, Mines and Low Carbon Innovation','type':'BC GOV Ministry','isactive':True,'bcgovcode':'EMLI','iaocode':'EML'},
            {'name':'Ministry of Environment and Climate Change Strategy','type':'BC GOV Ministry','isactive':True,'bcgovcode':'ENV','iaocode':'MOE'},
            {'name':'Ministry of Finance','type':'BC GOV Ministry','isactive':True,'bcgovcode':'FIN','iaocode':'FIN'},
            {'name':'Ministry of Forests','type':'BC GOV Ministry','isactive':True,'bcgovcode':'FOR','iaocode':'FOR'},
            {'name':'Ministry of Health','type':'BC GOV Ministry','isactive':True,'bcgovcode':'HLTH','iaocode':'HLTH'},
            {'name':'Ministry of Indigenous Relations and Reconciliation','type':'BC GOV Ministry','isactive':True,'bcgovcode':'IRR','iaocode':'IRR'},
            {'name':'Ministry of Jobs, Economic Recovery and Innovation','type':'BC GOV Ministry','isactive':True,'bcgovcode':'JERI','iaocode':'JER'},
            {'name':'Ministry of Labour','type':'BC GOV Ministry','isactive':True,'bcgovcode':'LBR','iaocode':'LBR'},
            {'name':'Ministry of Mental Health and Addictions','type':'BC GOV Ministry','isactive':True,'bcgovcode':'MMHA','iaocode':'MHA'},
            {'name':'Ministry of Municipal Affairs','type':'BC GOV Ministry','isactive':True,'bcgovcode':'MUNI','iaocode':'MMA'},
            {'name':'Ministry of Public Safety and Solicitor General','type':'BC GOV Ministry','isactive':True,'bcgovcode':'PSSG','iaocode':'PSS'},
            {'name':'Ministry of Social Development and Poverty Reduction','type':'BC GOV Ministry','isactive':True,'bcgovcode':'SDPR','iaocode':'MSD'},
            {'name':'Ministry of Tourism, Arts, Culture and Sport','type':'BC GOV Ministry','isactive':True,'bcgovcode':'TACS','iaocode':'TAC'},
            {'name':'Ministry of Transportation and Infrastructure','type':'BC GOV Ministry','isactive':True,'bcgovcode':'TRAN','iaocode':'TRA'},
            {'name':'BC Coroners Service','type':'Other','isactive':True,'bcgovcode':'OCC','iaocode':'OCC'},
            {'name':'BC Public Service Agency','type':'Other','isactive':True,'bcgovcode':'PSA','iaocode':'PSA'},
            {'name':'Board Resourcing and Development Office','type':'Other','isactive':True,'bcgovcode':'BRD','iaocode':'BRD'},
            {'name':'Community Living BC','type':'Other','isactive':True,'bcgovcode':'CLB','iaocode':'CLB'},
            {'name':'Crown Agencies Secretariat','type':'Other','isactive':True,'bcgovcode':'CAS','iaocode':'CAS'},
            {'name':'Emergency Management BC','type':'Other','isactive':True,'bcgovcode':'EMBC','iaocode':'EMB'},
            {'name':'Environmental Assessment Office','type':'Other','isactive':True,'bcgovcode':'EAO','iaocode':'EAO'},
            {'name':'Government Communications and Public Engagement','type':'Other','isactive':True,'bcgovcode':'GCPE','iaocode':'GCP'},
            {'name':'Independent Investigations Office','type':'Other','isactive':True,'bcgovcode':'IIO','iaocode':'IIO'},
            {'name':'Office of the Premier','type':'Other','isactive':True,'bcgovcode':'PREM','iaocode':'OOP'},
            {'name':'Liquor Distribution Branch','type':'Other','isactive':True,'bcgovcode':'LDB','iaocode':'LDB'},
            {'name':'Transportation Investment Corporation','type':'Other','isactive':True,'bcgovcode':'TIC','iaocode':'TIC'},
            {'name':'Order of British Columbia Advisory Council','type':'Other','isactive':True,'bcgovcode':'OBC','iaocode':'OBC'},
            {'name':'Medal of Good Citizenship Selection Committee','type':'Other','isactive':True,'bcgovcode':'MGC','iaocode':'MGC'},
            {'name':'Ministry of Declaration Act Secretariat','type':'BC GOV Ministry','isactive':True,'bcgovcode':'DAS','iaocode':'DAS'},
            {'name':'Ministry of Lands, Water and Resource Stewardship','type':'BC GOV Ministry','isactive':True,'bcgovcode':'LWR','iaocode':'LWR'}

        ]
    )
    

def downgrade():
    ##Program Areas Data Insertion
    programareas_table = table('ProgramAreas',
                                 column('name',String),
                                 column('type',String),
                                 column('isactive',Boolean),
                                 column('bcgovcode',String),
                                 column('iaocode',String),
                                   )
    op.execute('Truncate table public."ProgramAreas" RESTART IDENTITY CASCADE;commit;')                               
    op.bulk_insert(
        programareas_table,
        [
            {'name':'Ministry of Advanced Education and Skills Training','type':'BC GOV Ministry','isactive':True,'bcgovcode':'AEST','iaocode':'AED'},
            {'name':'Ministry of Agriculture, Food and Fisheries','type':'BC GOV Ministry','isactive':True,'bcgovcode':'AFF','iaocode':'AGR'},
            {'name':'Ministry of Attorney General','type':'BC GOV Ministry','isactive':True,'bcgovcode':'AG','iaocode':'MAG'},
            {'name':'Ministry of Children and Family Development','type':'BC GOV Ministry','isactive':True,'bcgovcode':'MCF','iaocode':'CFD'},
            {'name':'Ministry of Citizens’ Services','type':'BC GOV Ministry','isactive':True,'bcgovcode':'CITZ','iaocode':'CTZ'},
            {'name':'Ministry of Education','type':'BC GOV Ministry','isactive':True,'bcgovcode':'EDUC','iaocode':'EDU'},
            {'name':'Ministry of Energy, Mines and Low Carbon Innovation','type':'BC GOV Ministry','isactive':True,'bcgovcode':'EMLI','iaocode':'EML'},
            {'name':'Ministry of Environment and Climate Change Strategy','type':'BC GOV Ministry','isactive':True,'bcgovcode':'ENV','iaocode':'MOE'},
            {'name':'Ministry of Finance','type':'BC GOV Ministry','isactive':True,'bcgovcode':'FIN','iaocode':'FIN'},
            {'name':'Ministry of Forests, Lands, Natural Resource Operations and Rural Development','type':'BC GOV Ministry','isactive':True,'bcgovcode':'FLNR','iaocode':'FNR'},
            {'name':'Ministry of Health','type':'BC GOV Ministry','isactive':True,'bcgovcode':'HLTH','iaocode':'HLTH'},
            {'name':'Ministry of Indigenous Relations and Reconciliation','type':'BC GOV Ministry','isactive':True,'bcgovcode':'IRR','iaocode':'IRR'},
            {'name':'Ministry of Jobs, Economic Recovery and Innovation','type':'BC GOV Ministry','isactive':True,'bcgovcode':'JERI','iaocode':'JER'},
            {'name':'Ministry of Labour','type':'BC GOV Ministry','isactive':True,'bcgovcode':'LBR','iaocode':'LBR'},
            {'name':'Ministry of Mental Health and Addictions','type':'BC GOV Ministry','isactive':True,'bcgovcode':'MMHA','iaocode':'MHA'},
            {'name':'Ministry of Municipal Affairs','type':'BC GOV Ministry','isactive':True,'bcgovcode':'MUNI','iaocode':'MMA'},
            {'name':'Ministry of Public Safety and Solicitor General','type':'BC GOV Ministry','isactive':True,'bcgovcode':'PSSG','iaocode':'PSS'},
            {'name':'Ministry of Social Development and Poverty Reduction','type':'BC GOV Ministry','isactive':True,'bcgovcode':'SDPR','iaocode':'MSD'},
            {'name':'Ministry of Tourism, Arts, Culture and Sport','type':'BC GOV Ministry','isactive':True,'bcgovcode':'TACS','iaocode':'TAC'},
            {'name':'Ministry of Transportation and Infrastructure','type':'BC GOV Ministry','isactive':True,'bcgovcode':'TRAN','iaocode':'TRA'},
            {'name':'BC Coroners Service','type':'Other','isactive':True,'bcgovcode':'OCC','iaocode':'OCC'},
            {'name':'BC Public Service Agency','type':'Other','isactive':True,'bcgovcode':'PSA','iaocode':'PSA'},
            {'name':'Board Resourcing and Development Office','type':'Other','isactive':True,'bcgovcode':'BRD','iaocode':'BRD'},
            {'name':'Community Living BC','type':'Other','isactive':True,'bcgovcode':'CLB','iaocode':'CLB'},
            {'name':'Crown Agencies Secretariat','type':'Other','isactive':True,'bcgovcode':'CAS','iaocode':'CAS'},
            {'name':'Emergency Management BC','type':'Other','isactive':True,'bcgovcode':'EMBC','iaocode':'EMB'},
            {'name':'Environmental Assessment Office','type':'Other','isactive':True,'bcgovcode':'EAO','iaocode':'EAO'},
            {'name':'Government Communications and Public Engagement','type':'Other','isactive':True,'bcgovcode':'GCPE','iaocode':'GCP'},
            {'name':'Independent Investigations Office','type':'Other','isactive':True,'bcgovcode':'IIO','iaocode':'IIO'},
            {'name':'Office of the Premier','type':'Other','isactive':True,'bcgovcode':'PREM','iaocode':'OOP'},
            {'name':'Liquor Distribution Branch','type':'Other','isactive':True,'bcgovcode':'LDB','iaocode':'LDB'},
            {'name':'Transportation Investment Corporation','type':'Other','isactive':True,'bcgovcode':'TIC','iaocode':'TIC'},
            {'name':'Order of British Columbia Advisory Council','type':'Other','isactive':True,'bcgovcode':'OBC','iaocode':'OBC'},
            {'name':'Medal of Good Citizenship Selection Committee','type':'Other','isactive':True,'bcgovcode':'MGC','iaocode':'MGC'}

        ]
    )

    