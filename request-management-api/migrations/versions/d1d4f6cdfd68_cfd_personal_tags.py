"""CFD Personal Tags

Revision ID: d1d4f6cdfd68
Revises: 6646acda32fe
Create Date: 2024-04-15 22:36:29.501289

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd1d4f6cdfd68'
down_revision = '6646acda32fe'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('ProgramAreaDivisions', sa.Column('type', sa.String(length=25), nullable=True))

    people = ["APPLICANT", "PERSON 1", "PERSON 2", "PERSON 3", "PERSON 4", "PERSON 5", "PERSON 6", "PERSON 7", "PERSON 8", "PERSON 9", "PERSON 10", "PERSON 11", "PERSON 12", "PERSON 13", "PERSON 14", "PERSON 15", "PERSON 16", "PERSON 17", "PERSON 18", "PERSON 19", "PERSON 20"]
    sortorder = 0

    for person in people:
        op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby, sortorder, issection, specifictopersonalrequests, type)\
        VALUES ((SELECT programareaid FROM public."ProgramAreas" WHERE iaocode =\'CFD\'), \''+person+'\', TRUE, NOW(), \'system\', '+ str(sortorder) +', FALSE, TRUE, \'person\' );')
        sortorder = sortorder+1

    filetypes = ["CS", "FS", "ICM MEMO", "INCIDENT REQUEST", "SERVICE REQUEST", "FS CFP", "FT 1", "FY 2", "FY 3", "FY 4", "FY 5", "FY 6", "FY 7", "FY 8", "FY 9", "FY 10", "FY 11", "FY 12", "FY 13", "FY 14", "FY 15", "FY 16", "FY 17", "FY 18", "FY 19", "FY 20", "FT 21", "FY 22", "FY 23", "FY 24", "FY 25", "FY 26", "FY 27", "FY 28", "FY 29", "FY 30", "FT 31", "FY 32", "FY 33", "FY 34", "FY 35", "FY 36", "FY 37", "FY 38", "FY 39", "FY 40", "FT 41", "FY 42", "FY 43", "FY 44", "FY 45", "FY 46", "FY 47", "FY 48", "FY 49", "FY 50"]
    sortorder = 1

    for ftype in filetypes:
        op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby, sortorder, issection, specifictopersonalrequests, type)\
        VALUES ((SELECT programareaid FROM public."ProgramAreas" WHERE iaocode =\'CFD\'), \''+ftype+'\', TRUE, NOW(), \'system\', '+ str(sortorder) +', FALSE, TRUE, \'filetype\' );')
        sortorder = sortorder+1

    volumes = ["VOL 1", "VOL 2", "VOL 3", "VOL 4", "VOL 5", "VOL 6", "VOL 7", "VOL 8", "VOL 9", "VOL 10", "VOL 11", "VOL 12", "VOL 13", "VOL 14", "VOL 15", "VOL 16", "VOL 17", "VOL 18", "VOL 19", "VOL 20"]
    sortorder = 1

    for vol in volumes:
        op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby, sortorder, issection, specifictopersonalrequests, type)\
        VALUES ((SELECT programareaid FROM public."ProgramAreas" WHERE iaocode =\'CFD\'), \''+vol+'\', TRUE, NOW(), \'system\', '+ str(sortorder) +', FALSE, TRUE, \'volume\' );')
        sortorder = sortorder+1

def downgrade():
    op.execute('DELETE FROM public."ProgramAreaDivisions" WHERE type in (\'person\', \'filetype\', \'volume\')')
    op.drop_column('ProgramAreaDivisions', 'type')
