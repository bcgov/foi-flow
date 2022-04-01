"""empty message

Revision ID: e8bf3ced66ab
Revises: 2a8e09fa63cc
Create Date: 2022-04-01 13:50:36.995576

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e8bf3ced66ab'
down_revision = '2a8e09fa63cc'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('update public."ProgramAreaDivisions" set name = \'Services & Technology\' where name=\'services & Technology\';')
    op.execute('update public."ProgramAreaDivisions" set name = \'Small Business & Economic Development\' where name=\'small Business & Economic Development\';')
    op.execute('update public."ProgramAreaDivisions" set name = \'Sport and Creative Sector\' where name=\'sport and Creative Sector\';')
    op.execute('update public."ProgramAreaDivisions" set name = \'Arts & Culture\' where name=\'Arts & Cultur\';')
    op.execute('delete from public."ProgramAreaDivisions" where name=\'Economic Restart (? – maybe part of DMO?)\';')


def downgrade():
    op.execute('update public."ProgramAreaDivisions" set name = \'services & Technology\' where name=\'Services & Technology\';')
    op.execute('update public."ProgramAreaDivisions" set name = \'small Business & Economic Development\' where name=\'Small Business & Economic Development\';')
    op.execute('update public."ProgramAreaDivisions" set name = \'sport and Creative Sector\' where name=\'Sport and Creative Sector\';')
    op.execute('update public."ProgramAreaDivisions" set name = \'Arts & Cultur\' where name=\'Arts & Culture\';')
    op.execute('Insert into public."ProgramAreaDivisions" (programareaid, name, isactive, created_at, createdby) values ((select programareaid from public."ProgramAreas" where name=\'Ministry of Jobs, Economic Recovery and Innovation\'), \'Economic Restart (? – maybe part of DMO?)\', true, now(), \'system\');')
