"""empty message

Revision ID: cb0ca82dabf7
Revises: 4a8a8487692c
Create Date: 2023-02-15 23:10:59.045914

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cb0ca82dabf7'
down_revision = '4a8a8487692c'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('UPDATE public."FOIRequestTeams"\
	    SET  programareaid=(SELECT programareaid FROM "ProgramAreas" \
        WHERE iaocode in(\'WLR\') and isactive = true)\
	    WHERE  programareaid in (SELECT programareaid FROM "ProgramAreas" \
        WHERE iaocode in(\'LWR\') and isactive = false);')
    op.execute('UPDATE public."FOIRequestTeams"\
	    SET  programareaid=(SELECT programareaid FROM "ProgramAreas" \
        WHERE iaocode in(\'EMC\') and isactive = true)\
	    WHERE  programareaid in (SELECT programareaid FROM "ProgramAreas" \
        WHERE iaocode in(\'EMB\') and isactive = false);')    


def downgrade():
    op.execute('UPDATE public."FOIRequestTeams"\
	    SET  programareaid=(SELECT programareaid FROM "ProgramAreas" \
        WHERE iaocode in(\'LWR\') and isactive = false)\
	    WHERE  programareaid in (SELECT programareaid FROM "ProgramAreas" \
        WHERE iaocode in(\'WLR\') and isactive = true);')
    op.execute('UPDATE public."FOIRequestTeams"\
	    SET  programareaid=(SELECT programareaid FROM "ProgramAreas" \
        WHERE iaocode in(\'EMB\') and isactive = false)\
	    WHERE  programareaid in (SELECT programareaid FROM "ProgramAreas" \
        WHERE iaocode in(\'EMC\') and isactive = true);')  
