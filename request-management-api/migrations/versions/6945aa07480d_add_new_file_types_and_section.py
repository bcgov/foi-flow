"""Add_new_file_types_and_section

Revision ID: 6945aa07480d
Revises: d93211421685
Create Date: 2025-03-21 10:55:22.225605

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '6945aa07480d'
down_revision = 'd93211421685'
branch_labels = None
depends_on = None


def upgrade():
    sql = '''INSERT INTO "ProgramAreaDivisions" (programareaid, name, isactive, created_at, createdby, sortorder, issection, specifictopersonalrequests, type) VALUES 
    (4, 'Youth', true, current_timestamp, 'system', 45, false, true, 'filetype'),
    (4, 'Guardianship Case Review', true, current_timestamp, 'system', 46, false, true, 'filetype'),
    (4, 'Abuse and Neglect Investigation', true, current_timestamp, 'system', 47, false, true, 'filetype'),
    (4, 'CAFCA Client', true, current_timestamp, 'system', 48, false, true, 'filetype'),
    (4, 'ICM SP', true, current_timestamp, 'system', 49, true, true, 'section')
    '''
    op.execute(sql)

    addvolumesqlunformatted = '''INSERT INTO "ProgramAreaDivisions" (programareaid, name, isactive, created_at, createdby, sortorder, issection, specifictopersonalrequests, type) VALUES 
                    (4, 'VOL {vol}', true, current_timestamp, 'system', {vol}, false, true, 'volume')'''
    for volumenumber in range(21, 31):
        sql = addvolumesqlunformatted.format(vol = volumenumber)
        op.execute(sql)

def downgrade():
    volumestoremove = "("
    for vol in range(21,31):
        volumestoremove += ("'VOL {volume}'".format(volume=vol))
        if vol < 30: 
            volumestoremove += ', '
    volumestoremove += ")"

    sql = '''DELETE FROM "ProgramAreaDivisions" WHERE 
    name = 'Youth' OR
    name = 'Guardianship Case Review' OR
    name = 'Abuse and Neglect Investigation' OR
    name = 'CAFCA Client' OR
    name = 'ICM SP' OR
    name IN {volumestoremove}
    '''.format(volumestoremove=volumestoremove)
    op.execute(sql)