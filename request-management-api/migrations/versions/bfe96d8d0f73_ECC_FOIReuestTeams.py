"""empty message

Revision ID: bfe96d8d0f73
Revises: 7475633301cd
Create Date: 2023-01-04 17:27:01.614428

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bfe96d8d0f73'
down_revision = '7475633301cd'
branch_labels = None
depends_on = None


def upgrade():
    #personal
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'Personal\',(select requeststatusid from public."FOIRequestStatuses" where name=\'Deduplication\'),(select teamid from public."OperatingTeams" where name=\'ECC Ministry Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'PSE\'),true);commit;')
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'Personal\',(select requeststatusid from public."FOIRequestStatuses" where name=\'Open\'),(select teamid from public."OperatingTeams" where name=\'ECC Ministry Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'PSE\'),true);commit;')
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'Personal\',(select requeststatusid from public."FOIRequestStatuses" where name=\'Call For Records\'),(select teamid from public."OperatingTeams" where name=\'ECC Ministry Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'PSE\'),true);commit;')
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'Personal\',(select requeststatusid from public."FOIRequestStatuses" where name=\'Closed\'),(select teamid from public."OperatingTeams" where name=\'ECC Ministry Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'PSE\'),true);commit;')
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'Personal\',(select requeststatusid from public."FOIRequestStatuses" where name=\'Consult\'),(select teamid from public."OperatingTeams" where name=\'ECC Ministry Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'PSE\'),true);commit;')
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'Personal\',(select requeststatusid from public."FOIRequestStatuses" where name=\'Ministry Sign Off\'),(select teamid from public."OperatingTeams" where name=\'ECC Ministry Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'PSE\'),true);commit;')
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'Personal\',(select requeststatusid from public."FOIRequestStatuses" where name=\'On Hold\'),(select teamid from public."OperatingTeams" where name=\'ECC Ministry Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'PSE\'),true);commit;')
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'Personal\',(select requeststatusid from public."FOIRequestStatuses" where name=\'Harms Assessment\'),(select teamid from public."OperatingTeams" where name=\'ECC Ministry Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'PSE\'),true);commit;')
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'Personal\',(select requeststatusid from public."FOIRequestStatuses" where name=\'Response\'),(select teamid from public."OperatingTeams" where name=\'ECC Ministry Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'PSE\'),true);commit;')
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'Personal\',(select requeststatusid from public."FOIRequestStatuses" where name=\'Fee Estimate\'),(select teamid from public."OperatingTeams" where name=\'ECC Ministry Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'PSE\'),true);commit;')
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'Personal\',(select requeststatusid from public."FOIRequestStatuses" where name=\'Records Review\'),(select teamid from public."OperatingTeams" where name=\'ECC Ministry Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'PSE\'),true);commit;')

    #general
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'General\',(select requeststatusid from public."FOIRequestStatuses" where name=\'Call For Records\'),(select teamid from public."OperatingTeams" where name=\'ECC Ministry Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'PSE\'),true);commit;')
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'General\',(select requeststatusid from public."FOIRequestStatuses" where name=\'Closed\'),(select teamid from public."OperatingTeams" where name=\'ECC Ministry Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'PSE\'),true);commit;')
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'General\',(select requeststatusid from public."FOIRequestStatuses" where name=\'Consult\'),(select teamid from public."OperatingTeams" where name=\'ECC Ministry Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'PSE\'),true);commit;')
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'General\',(select requeststatusid from public."FOIRequestStatuses" where name=\'Ministry Sign Off\'),(select teamid from public."OperatingTeams" where name=\'ECC Ministry Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'PSE\'),true);commit;')
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'General\',(select requeststatusid from public."FOIRequestStatuses" where name=\'Deduplication\'),(select teamid from public."OperatingTeams" where name=\'ECC Ministry Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'PSE\'),true);commit;')
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'General\',(select requeststatusid from public."FOIRequestStatuses" where name=\'Harms Assessment\'),(select teamid from public."OperatingTeams" where name=\'ECC Ministry Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'PSE\'),true);commit;')
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'General\',(select requeststatusid from public."FOIRequestStatuses" where name=\'Response\'),(select teamid from public."OperatingTeams" where name=\'ECC Ministry Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'PSE\'),true);commit;')
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'General\',(select requeststatusid from public."FOIRequestStatuses" where name=\'Fee Estimate\'),(select teamid from public."OperatingTeams" where name=\'ECC Ministry Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'PSE\'),true);commit;')
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'General\',(select requeststatusid from public."FOIRequestStatuses" where name=\'Records Review\'),(select teamid from public."OperatingTeams" where name=\'ECC Ministry Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'PSE\'),true);commit;')
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'General\',(select requeststatusid from public."FOIRequestStatuses" where name=\'On Hold\'),(select teamid from public."OperatingTeams" where name=\'ECC Ministry Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'PSE\'),true);commit;')



def downgrade():
    op.execute('DELETE FROM public."FOIRequestTeams" WHERE requesttype = \'Personal\'and requeststatusid in (select requeststatusid from public."FOIRequestStatuses" where name in (\'Harms Assessment\',\'Deduplication\',\'Open\',\'Call For Records\',\'Closed\',\'Consult\',\'Ministry Sign Off\',\'On Hold\',\'Response\',\'Fee Estimate\',\'Records Review\'));commit;')
    op.execute('DELETE FROM public."FOIRequestTeams" WHERE requesttype = \'General\'and requeststatusid in (select requeststatusid from public."FOIRequestStatuses" where name in (\'Harms Assessment\',\'Deduplication\',\'Call For Records\',\'Closed\',\'Consult\',\'Ministry Sign Off\',\'On Hold\',\'Response\',\'Fee Estimate\',\'Records Review\'));commit;')
