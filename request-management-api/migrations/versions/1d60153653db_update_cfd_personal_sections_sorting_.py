"""Update CFD Personal Sections Sorting Order

Revision ID: 1d60153653db
Revises: 06283c0685fb
Create Date: 2024-08-19 09:36:01.403157

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1d60153653db'
down_revision = '06283c0685fb'
branch_labels = None
depends_on = None


def upgrade():
    sections = ["Activity Forms","Adoption","Case Notes","Change Card and Forms","Collaborative Planning","Correspondence","Cultural Planning","Education, Employment and Training","External Assessments","Family Group Mediation","Financial","Incidents","Internal Assessments","Inside Back Cover","Inside Front Cover","Intake and Investigation","Legal","Medical","Personal History and Records","Young Offenders","Accountability","ADR","Agreements and Approvals","Caregiver Information","Case Conference","Case Snapshot","Child and Birth Family Background","Child in Care Information","Consents and Authorizations","Contracts","Documents","File Summary","Maples","Mediation","Note Pad Screens","Out-of-Care Services","Physical File Summary","Placement Slips","Planning","Protocol and Incidents","Reconsideration","Running Record","Referrals","Relief Care Giver Documentation","Reports","Reviews","Services for Children Not in Care","Supervisor Orders"]
    secsortorder = 1

    op.execute('UPDATE public."ProgramAreaDivisions" SET isactive = FALSE WHERE programareaid in (SELECT programareaid FROM public."ProgramAreas" WHERE iaocode =\'CFD\') AND type = \'section\' AND name != \'TBD\'')
    for sec in sections:
        op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby, sortorder, issection, specifictopersonalrequests, type)\
        VALUES ((SELECT programareaid FROM public."ProgramAreas" WHERE iaocode =\'CFD\'), \''+sec+'\', TRUE, NOW(), \'system\', '+ str(secsortorder) +', TRUE, TRUE, \'section\');')
        secsortorder = secsortorder+1
    
    op.execute('UPDATE public."ProgramAreaDivisions" SET sortorder = '+str(secsortorder)+' WHERE programareaid in (SELECT programareaid FROM public."ProgramAreas" WHERE iaocode =\'CFD\') AND type = \'section\' AND name = \'TBD\'')

def downgrade():
    op.execute('UPDATE public."ProgramAreaDivisions" SET isactive = FALSE WHERE programareaid in (SELECT programareaid FROM public."ProgramAreas" WHERE iaocode =\'CFD\') AND type = \'section\' AND name != \'TBD\'')