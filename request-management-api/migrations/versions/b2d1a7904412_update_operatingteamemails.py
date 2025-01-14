"""Update OperatingTeamEmails

Revision ID: b2d1a7904412
Revises: 1bda7f7bae57
Create Date: 2025-01-13 19:03:22.790184

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'b2d1a7904412'
down_revision = '1bda7f7bae57'
branch_labels = None
depends_on = None

def upgrade():
    op.execute('UPDATE public."OperatingTeamEmails" SET email_address = \'IAO.CentralAndEconomyTeam@gov.bc.ca\' WHERE teamid = (SELECT teamid FROM public."OperatingTeams" WHERE name = \'Central and Economy Team\');')
    op.execute('UPDATE public."OperatingTeamEmails" SET email_address = \'IAO.CommunityandHealthTeam@gov.bc.ca\' WHERE teamid = (SELECT teamid FROM public."OperatingTeams" WHERE name = \'Community and Health Team\');')

def downgrade():
    op.execute('UPDATE public."OperatingTeamEmails" SET email_address = \'IAOCentralTeam@gov.bc.ca\' WHERE teamid = (SELECT teamid FROM public."OperatingTeams" WHERE name = \'Central and Economy Team\');')
    op.execute('UPDATE public."OperatingTeamEmails" SET email_address = \'FOI.SocialEducationTeam@gov.bc.ca\' WHERE teamid = (SELECT teamid FROM public."OperatingTeams" WHERE name = \'Community and Health Team\');')