"""Deactivate Old Processing Teams

Revision ID: 05dee3d60a8c
Revises: 3a4f7b2c6d9e
Create Date: 2025-12-07 15:26:16.304413

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '05dee3d60a8c'
down_revision = '3a4f7b2c6d9e'
branch_labels = None
depends_on = None


def upgrade():
    # Deactivate old teams
    op.execute('''UPDATE public."OperatingTeams" SET isactive = false WHERE name = 'Coordinated Response Unit';''')
    op.execute('''UPDATE public."OperatingTeams" SET isactive = false WHERE name = 'Central and Economy Team';''')
    op.execute('''UPDATE public."OperatingTeams" SET isactive = false WHERE name = 'Resource and Justice Team';''')
    
    # Deactivate FOIRequestTeam mapping for old teams
    op.execute('''UPDATE public."FOIRequestTeams" SET isactive = false WHERE teamid = (SELECT teamid FROM public."OperatingTeams" WHERE name = 'Central and Economy Team');''')
    op.execute('''UPDATE public."FOIRequestTeams" SET isactive = false WHERE teamid = (SELECT teamid FROM public."OperatingTeams" WHERE name = 'Resource and Justice Team');''')
    op.execute('''UPDATE public."FOIRequestTeams" SET isactive = false WHERE teamid = (SELECT teamid FROM public."OperatingTeams" WHERE name = 'Coordinated Response Unit');''')

def downgrade():
    op.execute('''UPDATE public."FOIRequestTeams" SET isactive = true WHERE teamid = (SELECT teamid from public."OperatingTeams" WHERE name = 'Central and Economy Team');''')
    op.execute('''UPDATE public."FOIRequestTeams" SET isactive = true WHERE teamid = (SELECT teamid from public."OperatingTeams" WHERE name = 'Resource and Justice Team');''')
    op.execute('''UPDATE public."FOIRequestTeams" SET isactive = true WHERE teamid = (SELECT teamid from public."OperatingTeams" WHERE name = 'Coordinated Response Unit');''')

    op.execute('''UPDATE public."OperatingTeams" SET isactive = true WHERE name = 'Coordinated Response Unit';''')
    op.execute('''UPDATE public."OperatingTeams" SET isactive = true WHERE name = 'Central and Economy Team';''')
    op.execute('''UPDATE public."OperatingTeams" SET isactive = true WHERE name = 'Resource and Justice Team';''')