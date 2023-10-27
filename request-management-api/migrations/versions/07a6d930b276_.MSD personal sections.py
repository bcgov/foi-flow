"""MSD Personal Sections for SDD

Revision ID: 07a6d930b276
Revises: bdef238edb41
Create Date: 2023-09-12 16:49:26.208024

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '07a6d930b276'
down_revision = 'bdef238edb41'
branch_labels = None
depends_on = None


def upgrade():
    sections = ['GA KEY PLAYER','GA KEY PLAYER AHR','GA SPOUSE','GA SPOUSE AHR','GA DEPENDENT','GA DEPENDENT AHR','FM1 KEY PLAYER','FM1 KEY PLAYER AHR','FM2 RESPONDENT','FM2 RESPONDENT AHR','TPA','FM3','FM3 AHR','FM4','FM4 AHR','FM5','FM5 AHR','GA 2 DEPENDENT','GA 2 DEPENDENT AHR','GA 2 SPOUSE','GA 2 SPOUSE AHR','GA 3 SPOUSE','GA 3 SPOUSE AHR','GA KEY PLAYER PHYSICAL','GA SPOUSE PHYSICAL','GA2 SPOUSE PHYSICAL','GA3 SPOUSE PHYSICAL','GA DEPENDENT PHYSICAL','GA2 DEPENDENT PHYSICAL','FM1 KEY PLAYER PHYSICAL','FM2 RESPONDENT PHYSICAL','FM3 PHYSICAL','FM4 PHYSICAL','FM5 PHYSICAL']
    sortorder = 1

    for section in sections:
        op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby, sortorder,  issection, specifictopersonalrequests,parentid)\
        VALUES ((SELECT programareaid FROM public."ProgramAreas" WHERE iaocode =\'MSD\'), \''+section+'\', TRUE, NOW(), \'system\', '+ str(sortorder) +',TRUE, TRUE, (SELECT divisionid FROM public."ProgramAreaDivisions" WHERE name =\'SDD Document Tracking\' and isactive=true and programareaid in (SELECT programareaid FROM public."ProgramAreas" WHERE iaocode =\'MSD\' LIMIT 1)) );')
        sortorder = sortorder+1

def downgrade():
    op.execute('DELETE FROM public."ProgramAreaDivisions" WHERE programareaid in (SELECT programareaid FROM public."ProgramAreas" WHERE iaocode =\'MSD\') AND issection=TRUE and specifictopersonalrequests=TRUE and parentid in (SELECT divisionid FROM public."ProgramAreaDivisions" WHERE name =\'SDD Document Tracking\' and isactive=true and programareaid in (SELECT programareaid FROM public."ProgramAreas" WHERE iaocode =\'MSD\' LIMIT 1))')
