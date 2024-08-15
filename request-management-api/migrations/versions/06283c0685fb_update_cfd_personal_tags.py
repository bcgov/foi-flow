"""update CFD Personal tags

Revision ID: 06283c0685fb
Revises: aa2691fa6c3c
Create Date: 2024-08-14 12:40:37.844463

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '06283c0685fb'
down_revision = 'aa2691fa6c3c'
branch_labels = None
depends_on = None


def upgrade():
    filetypes = ["AD_C","AA","AH","AO","FH","CS","CYMH","DIV","FS","ICM","MAPLES","RE","SP","PABS","VAN-AA","VAN-CAS","VAN-CIC","VAN-CCAS","VIC-AA","YAG","Autism Case File","Assessment & Resource","AR ","AS","AM","AP","CC","Choices","CIC","CYSN","CS UNREG","CT","CH","FS UNREG","RE UNREG","SN","Woodlands","Incident","Memo ","Service Request","FS Case","CS Case","SR Case","Complaint"]
    ftsortorder = 1

    op.execute('DELETE FROM public."ProgramAreaDivisions" WHERE programareaid in (SELECT programareaid FROM public."ProgramAreas" WHERE iaocode =\'CFD\') AND type = \'filetype\'')
    for ftype in filetypes:
        op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby, sortorder, issection, specifictopersonalrequests, type)\
        VALUES ((SELECT programareaid FROM public."ProgramAreas" WHERE iaocode =\'CFD\'), \''+ftype+'\', TRUE, NOW(), \'system\', '+ str(ftsortorder) +', FALSE, TRUE, \'filetype\');')
        ftsortorder = ftsortorder+1


    sections = ["Accountability","Activity Forms","Adoption","ADR","Agreements and Approvals","Caregiver Information","Case Conference","Case Notes","Case Snapshot","Change Card and Forms","Child and Birth Family Background","Child in Care Information","Collaborative Planning","Consents and Authorizations","Contracts","Correspondence","Cultural Planning","Documents","Education, Employment and Training","External Assessments","Family Group Mediation","File Summary","Financial","Incidents","Internal Assessments","Inside Back Cover","Inside Front Cover","Intake and Investigation","Legal","Maples","Mediation","Medical","Note Pad Screens","Out-of-Care Services","Personal History and Records","Physical File Summary","Placement Slips","Planning","Protocol and Incidents","Reconsideration","Running Record","Referrals","Relief Care Giver Documentation","Reports","Reviews","Services for Children Not in Care","Supervisor Orders","Young Offenders"]
    secsortorder = 1

    op.execute('DELETE FROM public."ProgramAreaDivisions" WHERE programareaid in (SELECT programareaid FROM public."ProgramAreas" WHERE iaocode =\'CFD\') AND type = \'section\' AND name != \'TBD\'')
    for sec in sections:
        op.execute('INSERT INTO public."ProgramAreaDivisions"(programareaid, name, isactive, created_at, createdby, sortorder, issection, specifictopersonalrequests, type)\
        VALUES ((SELECT programareaid FROM public."ProgramAreas" WHERE iaocode =\'CFD\'), \''+sec+'\', TRUE, NOW(), \'system\', '+ str(secsortorder) +', TRUE, TRUE, \'section\');')
        secsortorder = secsortorder+1
    
    op.execute('UPDATE public."ProgramAreaDivisions" SET sortorder = '+str(secsortorder)+' WHERE programareaid in (SELECT programareaid FROM public."ProgramAreas" WHERE iaocode =\'CFD\') AND type = \'section\' AND name = \'TBD\'')

def downgrade():
    op.execute('DELETE FROM public."ProgramAreaDivisions" WHERE programareaid in (SELECT programareaid FROM public."ProgramAreas" WHERE iaocode =\'CFD\') AND type = \'filetype\'')
    op.execute('DELETE FROM public."ProgramAreaDivisions" WHERE programareaid in (SELECT programareaid FROM public."ProgramAreas" WHERE iaocode =\'CFD\') AND type = \'section\' AND name != \'TBD\'')