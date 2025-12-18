"""empty message

Revision ID: 898ea7d002de
Revises: 4f6729690cec
Create Date: 2022-12-30 16:01:37.801602

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '898ea7d002de'
down_revision = '4f6729690cec'
branch_labels = None
depends_on = None


def upgrade():
    #personal
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'Personal\',(select requeststatusid from public."FOIRequestStatuses" where name=\'Deduplication\'),(select teamid from public."OperatingTeams" where name=\'PSE Ministry Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'PSE\'),true);commit;')
    #op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'Personal\',(select requeststatusid from public."FOIRequestStatuses" where name=\'Open\'),(select teamid from public."OperatingTeams" where name=\'PSE Ministry Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'PSE\'),true);commit;')
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'Personal\',(select requeststatusid from public."FOIRequestStatuses" where name=\'Call For Records\'),(select teamid from public."OperatingTeams" where name=\'PSE Ministry Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'PSE\'),true);commit;')
    #op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'Personal\',(select requeststatusid from public."FOIRequestStatuses" where name=\'Closed\'),(select teamid from public."OperatingTeams" where name=\'PSE Ministry Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'PSE\'),true);commit;')
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'Personal\',(select requeststatusid from public."FOIRequestStatuses" where name=\'Consult\'),(select teamid from public."OperatingTeams" where name=\'PSE Ministry Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'PSE\'),true);commit;')
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'Personal\',(select requeststatusid from public."FOIRequestStatuses" where name=\'Ministry Sign Off\'),(select teamid from public."OperatingTeams" where name=\'PSE Ministry Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'PSE\'),true);commit;')
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'Personal\',(select requeststatusid from public."FOIRequestStatuses" where name=\'On Hold\'),(select teamid from public."OperatingTeams" where name=\'PSE Ministry Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'PSE\'),true);commit;')
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'Personal\',(select requeststatusid from public."FOIRequestStatuses" where name=\'Harms Assessment\'),(select teamid from public."OperatingTeams" where name=\'PSE Ministry Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'PSE\'),true);commit;')
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'Personal\',(select requeststatusid from public."FOIRequestStatuses" where name=\'Response\'),(select teamid from public."OperatingTeams" where name=\'PSE Ministry Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'PSE\'),true);commit;')
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'Personal\',(select requeststatusid from public."FOIRequestStatuses" where name=\'Fee Estimate\'),(select teamid from public."OperatingTeams" where name=\'PSE Ministry Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'PSE\'),true);commit;')
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'Personal\',(select requeststatusid from public."FOIRequestStatuses" where name=\'Records Review\'),(select teamid from public."OperatingTeams" where name=\'PSE Ministry Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'PSE\'),true);commit;')

    #general
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'General\',(select requeststatusid from public."FOIRequestStatuses" where name=\'Call For Records\'),(select teamid from public."OperatingTeams" where name=\'PSE Ministry Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'PSE\'),true);commit;')
    #op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'General\',(select requeststatusid from public."FOIRequestStatuses" where name=\'Closed\'),(select teamid from public."OperatingTeams" where name=\'PSE Ministry Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'PSE\'),true);commit;')
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'General\',(select requeststatusid from public."FOIRequestStatuses" where name=\'Consult\'),(select teamid from public."OperatingTeams" where name=\'PSE Ministry Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'PSE\'),true);commit;')
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'General\',(select requeststatusid from public."FOIRequestStatuses" where name=\'Ministry Sign Off\'),(select teamid from public."OperatingTeams" where name=\'PSE Ministry Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'PSE\'),true);commit;')
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'General\',(select requeststatusid from public."FOIRequestStatuses" where name=\'Deduplication\'),(select teamid from public."OperatingTeams" where name=\'PSE Ministry Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'PSE\'),true);commit;')
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'General\',(select requeststatusid from public."FOIRequestStatuses" where name=\'Harms Assessment\'),(select teamid from public."OperatingTeams" where name=\'PSE Ministry Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'PSE\'),true);commit;')
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'General\',(select requeststatusid from public."FOIRequestStatuses" where name=\'Response\'),(select teamid from public."OperatingTeams" where name=\'PSE Ministry Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'PSE\'),true);commit;')
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'General\',(select requeststatusid from public."FOIRequestStatuses" where name=\'Fee Estimate\'),(select teamid from public."OperatingTeams" where name=\'PSE Ministry Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'PSE\'),true);commit;')
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'General\',(select requeststatusid from public."FOIRequestStatuses" where name=\'Records Review\'),(select teamid from public."OperatingTeams" where name=\'PSE Ministry Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'PSE\'),true);commit;')
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'General\',(select requeststatusid from public."FOIRequestStatuses" where name=\'On Hold\'),(select teamid from public."OperatingTeams" where name=\'PSE Ministry Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'PSE\'),true);commit;')



def downgrade():
    op.execute('DELETE FROM public."FOIRequestTeams" WHERE requesttype = \'Personal\'and requeststatusid in (select requeststatusid from public."FOIRequestStatuses" where name in (\'Harms Assessment\',\'Deduplication\',\'Open\',\'Call For Records\',\'Closed\',\'Consult\',\'Ministry Sign Off\',\'On Hold\',\'Response\',\'Fee Estimate\',\'Records Review\')) and teamid in (select teamid from public."OperatingTeams" where name=\'PSE Ministry Team\');commit;')
    op.execute('DELETE FROM public."FOIRequestTeams" WHERE requesttype = \'General\'and requeststatusid in (select requeststatusid from public."FOIRequestStatuses" where name in (\'Harms Assessment\',\'Deduplication\',\'Call For Records\',\'Closed\',\'Consult\',\'Ministry Sign Off\',\'On Hold\',\'Response\',\'Fee Estimate\',\'Records Review\')) and teamid in (select teamid from public."OperatingTeams" where name=\'PSE Ministry Team\');commit;')
