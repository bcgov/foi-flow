"""Update OperatingTeamEmails for Infrastructure and Justice Teams

Revision ID: fdb798418feb
Revises: 05dee3d60a8c
Create Date: 2026-01-15 12:12:58.204086

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'fdb798418feb'
down_revision = '05dee3d60a8c'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('''UPDATE public."OperatingTeamEmails" SET email_address = 'IAO.IndustryTeam@gov.bc.ca' WHERE teamid = (SELECT teamid FROM public."OperatingTeams" WHERE name = 'Industry Team');''')
    op.execute('''UPDATE public."OperatingTeamEmails" SET email_address = 'IAO.JusticeTeam@gov.bc.ca' WHERE teamid = (SELECT teamid FROM public."OperatingTeams" WHERE name = 'Justice Team');''')

def downgrade():
    op.execute('''UPDATE public."OperatingTeamEmails" SET email_address = 'IAO.CentralAndEconomyTeam@gov.bc.ca' WHERE teamid = (SELECT teamid FROM public."OperatingTeams" WHERE name = 'Industry Team');''')
    op.execute('''UPDATE public."OperatingTeamEmails" SET email_address = 'IAO.CoordinatedResponseUnit@gov.bc.ca' WHERE teamid = (SELECT teamid FROM public."OperatingTeams" WHERE name = 'Justice Team');''')