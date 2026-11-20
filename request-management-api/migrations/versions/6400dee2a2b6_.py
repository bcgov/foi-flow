"""Govt BC Organization Changes Nov 20, 2026 (Provincial Elections)

Revision ID: 6400dee2a2b6
Revises: a4e9c7d2f1b6
Create Date: 2026-11-17 14:22:47.333055

"""
import os
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '6400dee2a2b6'
down_revision = 'a4e9c7d2f1b6'
branch_labels = None
depends_on = None

ENVIRONMENT = os.getenv('OSS_S3_ENVIRONMENT') or 'dev'
access = os.getenv('OSS_S3_FORMS_ACCESS_KEY_ID') or '<fake-access-key>'
secret = os.getenv('OSS_S3_FORMS_SECRET_ACCESS_KEY') or '<fake-secret-key>'
s3accesskeyjson = f'{{"s3accesskey": "{access}", "s3secretkey": "{secret}"}}'

NEW_MINISTRIES = [
    {
        'name': 'Ministry of Energy, Mines, and Petroleum Resources',
        'type': 'BC GOV Ministry', # 'BC Gov Ministry' or 'Other'
        # If type is 'Other', add 'operatingteamname': '<name of operating team>'
        'bcgovcode': 'EMP',
        'iaocode': 'EMP',
        'divisions': []
    },
    {
        'name': 'Ministry of Economic Development and Tourism',
        'type': 'BC GOV Ministry',
        'bcgovcode': 'EDT',
        'iaocode': 'EDT',
        'divisions': []
    },
    {
        'name': 'Ministry of Local Government, Housing, Sport and Culture',
        'type': 'BC GOV Ministry',
        'bcgovcode': 'LHS',
        'iaocode': 'LHS',
        'divisions': []
    },
]

def preview_sql(statement, params):
    compiled = statement.compile(dialect=postgresql.dialect())
    print(compiled)
    print(params)

def upgrade():
    # Ministry name changes (do not require new ministry teams and ORG codes remain the same)
    op.execute('''UPDATE public."ProgramAreas" SET name = 'Ministry of Agriculture' WHERE iaocode = 'AGR';''')
    op.execute('''UPDATE public."ProgramAreas" SET name = 'Ministry of Citizens’ Services and Technology' WHERE iaocode = 'CTZ';''')
    op.execute('''UPDATE public."ProgramAreas" SET name = 'Ministry of Environment' WHERE iaocode = 'MOE';''')
    op.execute('''UPDATE public."ProgramAreas" SET name = 'Ministry of Post-Secondary and Labour' WHERE iaocode = 'PSE';''')
    op.execute('''UPDATE public."ProgramAreas" SET name = 'Ministry of Social Development' WHERE iaocode = 'MSD';''')
    op.execute('''UPDATE public."ProgramAreas" SET name = 'Ministry of Transportation and Infrastructure' WHERE iaocode = 'TRA';''')
    op.execute('''UPDATE public."ProgramAreas" SET name = 'Ministry of Waters, Land and Natural Resource Operations' WHERE iaocode = 'WLR';''')
    
    connection = op.get_bind()
    # Ministry ORG code changes
    for org in NEW_MINISTRIES:
        bucket_name = org['iaocode'].lower() + f"-{ENVIRONMENT}-e"

        ####################
        ####################
        # DocumentPathMapper
        statement = sa.text('''
                        INSERT INTO public."DocumentPathMapper" (category, bucket, attributes, isactive, createdby)
                        VALUES ('Records', :bucket_name, :s3accesskeyjson, TRUE, 'System')
                    ''')
        params = {'bucket_name': bucket_name, 's3accesskeyjson': s3accesskeyjson}
        connection.execute(statement, params)

        ####################
        ####################
        # ProgramAreas
        statement = sa.text('''
            INSERT INTO public."ProgramAreas" (name, type, isactive, bcgovcode, iaocode)
            VALUES (:name, :type, True, :bcgovcode, :iaocode)
            RETURNING programareaid
        ''')
        params = {
            'name': org['name'],
            'type': org['type'],
            'bcgovcode': org['bcgovcode'],
            'iaocode': org['iaocode']
        }
        connection.execute(statement, params).scalar()

        ####################
        ####################
        # ProgramAreaDivisions
        # programareaid = '<placeholderid>'
        # programareaid = connection.execute(statement, params).scalar()
        # for division in org['divisions']:
        #     division_statement = sa.text('''
        #         INSERT INTO public."ProgramAreaDivisions" (programareaid, name, isactive, created_at, createdby, sortorder, issection, parentid, specifictopersonalrequests, type, isselectable)
        #         VALUES (:programareaid, :name, TRUE, NOW(), 'system', :sortorder, :issection, :parentid, :specifictopersonalrequests, :type, :isselectable)
        #     ''')
        #     division_params = {
        #         'programareaid': programareaid, 
        #         'name': division['name'], 
        #         'sortorder': division['sortorder'], 
        #         'issection': division['issection'], 
        #         'parentid': division['parentid'], 
        #         'specifictopersonalrequests': division['specifictopersonalrequests'], 
        #         'isselectable': division['isselectable'],
        #         'type': division['type']
        #     }
        #     connection.execute(division_statement, division_params)

        ####################
        ####################
        # OperatingTeams
        if org['type'] == 'BC GOV Ministry':
            operatingteamname = org['iaocode'].upper() + ' Ministry Team'
            operatingteamtype = 'ministry'
        elif org['type'] == 'Other':
            operatingteamname = org['operatingteamname']
            operatingteamtype = 'iao'

        statement = sa.text('''
            INSERT INTO public."OperatingTeams" (name, description, type, isactive)
            VALUES (:name, :description, :type, True)
        ''')
        params = {'name': operatingteamname, 'description': operatingteamname, 'type': operatingteamtype}
        connection.execute(statement, params)


def downgrade():
    op.execute('''UPDATE public."ProgramAreas" SET name = 'Ministry of Water, Land and Resource Stewardship' WHERE iaocode = 'WLR';''')
    op.execute('''UPDATE public."ProgramAreas" SET name = 'Ministry of Transportation and Transit' WHERE iaocode = 'TRA';''')
    op.execute('''UPDATE public."ProgramAreas" SET name = 'Ministry of Social Development and Poverty Reduction' WHERE iaocode = 'MSD';''')
    op.execute('''UPDATE public."ProgramAreas" SET name = 'Ministry of Post-Secondary and Future Skills' WHERE iaocode = 'PSE';''')
    op.execute('''UPDATE public."ProgramAreas" SET name = 'Ministry of Environment and Parks' WHERE iaocode = 'MOE';''')
    op.execute('''UPDATE public."ProgramAreas" SET name = 'Ministry of Citizens’ Services' WHERE iaocode = 'CTZ';''')
    op.execute('''UPDATE public."ProgramAreas" SET name = 'Ministry of Agriculture and Food' WHERE iaocode = 'AGR';''')
    
    connection = op.get_bind()
    # Reverse upgrade order so names still match when lists overlap.
    for org in reversed(NEW_MINISTRIES):
        if org['type'] == 'BC GOV Ministry':
            operatingteamname = org['iaocode'].upper() + ' Ministry Team'
            operatingteamtype = 'ministry'
        elif org['type'] == 'Other':
            operatingteamname = org['operatingteamname']
            operatingteamtype = 'iao'

        statement = sa.text('''
                DELETE FROM public."OperatingTeams"
                WHERE name = :name AND type = :type
            ''')
        params = {'name': operatingteamname, 'type': operatingteamtype}
        connection.execute(statement, params)

        # for division in reversed(org['divisions']):
        #     statement = sa.text('''
        #             DELETE FROM public."ProgramAreaDivisions"
        #             WHERE programareaid = (
        #                 SELECT programareaid FROM public."ProgramAreas"
        #                 WHERE bcgovcode = :bcgovcode AND iaocode = :iaocode
        #             )
        #             AND name = :name
        #         ''')
        #     params = {
        #         'bcgovcode': org['bcgovcode'],
        #         'iaocode': org['iaocode'],
        #         'name': division['name'],
        #     }
        #     connection.execute(statement, params)

        statement = sa.text('''
                DELETE FROM public."ProgramAreas"
                WHERE bcgovcode = :bcgovcode AND iaocode = :iaocode
            ''')
        params = {'bcgovcode': org['bcgovcode'], 'iaocode': org['iaocode']}
        connection.execute(statement, params)

        bucket_name = org['iaocode'].lower() + f"-{ENVIRONMENT}-e"
        statement = sa.text('''
                DELETE FROM public."DocumentPathMapper"
                WHERE category = 'Records' AND bucket = :bucket_name
                  AND createdby = 'System'
            ''')
        params = {'bucket_name': bucket_name}
        connection.execute(statement, params)