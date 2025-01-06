"""Create OperatingTeamEmails table

Revision ID: 3e8203b24730
Revises: dc99ffc3a6f7
Create Date: 2024-06-20 15:43:52.554964

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '3e8203b24730'
down_revision = 'dc99ffc3a6f7'
branch_labels = None
depends_on = None


def upgrade():
    operatingteamemailstable = op.create_table('OperatingTeamEmails',
    sa.Column('emailid', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('teamid', sa.Integer(), unique=False, nullable=False),
    sa.Column('email_address', sa.String(length=255), unique=False, nullable=False),
    # sa.Column('isactive', sa.Boolean, nullable=False, server_default="true"),
    sa.Column('isactive', sa.Boolean, nullable=False, server_default="true"),
    sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
    sa.Column('updated_at', sa.DateTime(), nullable=True),    
    sa.ForeignKeyConstraint(['teamid'], ['OperatingTeams.teamid'], ),
    sa.PrimaryKeyConstraint('emailid')
    )

    op.execute('''INSERT INTO public."OperatingTeamEmails" (teamid, email_address)
                    VALUES
                        ((SELECT teamid FROM public."OperatingTeams" WHERE name = 'Central and Economy Team'), 'IAOCentralTeam@gov.bc.ca'),
                        ((SELECT teamid FROM public."OperatingTeams" WHERE name = 'Community and Health Team'), 'FOI.SocialEducationTeam@gov.bc.ca'),
                        ((SELECT teamid FROM public."OperatingTeams" WHERE name = 'Resource and Justice Team'), 'IAOResourceTeam@gov.bc.ca'),
                        ((SELECT teamid FROM public."OperatingTeams" WHERE name = 'Children and Family Team'), 'IAO.ChildrenandEducationTeam@gov.bc.ca'),
                        ((SELECT teamid FROM public."OperatingTeams" WHERE name = 'Children and Education Team'), 'IAO.ChildrenandEducationTeam@gov.bc.ca'),
                        ((SELECT teamid FROM public."OperatingTeams" WHERE name = 'Scanning Team'), 'IAO.ChildrenandEducationTeam@gov.bc.ca'),
                        ((SELECT teamid FROM public."OperatingTeams" WHERE name = 'Intake Team'), 'IAOIntaketeam@gov.bc.ca'),
                        ((SELECT teamid FROM public."OperatingTeams" WHERE name = 'Coordinated Response Unit'), 'IAO.CoordinatedResponseUnit@gov.bc.ca')''')

def downgrade():
    op.drop_table('OperatingTeamEmails')
