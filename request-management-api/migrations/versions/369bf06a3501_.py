"""empty message

Revision ID: 369bf06a3501
Revises: 40dae8cc58cb
Create Date: 2022-05-03 12:30:06.218396

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import column, table
from sqlalchemy.sql.sqltypes import Boolean, String, Integer


# revision identifiers, used by Alembic.
revision = '369bf06a3501'
down_revision = '40dae8cc58cb'
branch_labels = None
depends_on = None


def upgrade():
    #General - Closed
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'General\',3,(select teamid from public."OperatingTeams" where name=\'DAS Ministry Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'DAS\'),true);commit;')
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'General\',3,(select teamid from public."OperatingTeams" where name=\'LWR Ministry Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'LWR\'),true);commit;')
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'General\',3,(select teamid from public."OperatingTeams" where name=\'Resource Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'DAS\'),true);commit;')
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'General\',3,(select teamid from public."OperatingTeams" where name=\'Resource Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'LWR\'),true);commit;')

# General - Call For Records
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'General\',2,(select teamid from public."OperatingTeams" where name=\'DAS Ministry Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'DAS\'),true);commit;')
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'General\',2,(select teamid from public."OperatingTeams" where name=\'LWR Ministry Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'LWR\'),true);commit;')

# General - Fee Estimate
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'General\',8,(select teamid from public."OperatingTeams" where name=\'Resource Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'DAS\'),true);commit;')
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'General\',8,(select teamid from public."OperatingTeams" where name=\'Resource Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'LWR\'),true);commit;')

# General - Deduplication
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'General\',12,(select teamid from public."OperatingTeams" where name=\'DAS Ministry Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'DAS\'),true);commit;')
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'General\',12,(select teamid from public."OperatingTeams" where name=\'LWR Ministry Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'LWR\'),true);commit;')

# General - On Hold
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'General\',11,(select teamid from public."OperatingTeams" where name=\'Resource Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'DAS\'),true);commit;')
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'General\',11,(select teamid from public."OperatingTeams" where name=\'Resource Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'LWR\'),true);commit;')

# General - Harms Assessment
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'General\',13,(select teamid from public."OperatingTeams" where name=\'Resource Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'DAS\'),true);commit;')
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'General\',13,(select teamid from public."OperatingTeams" where name=\'Resource Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'LWR\'),true);commit;')

# General - Records Review
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'General\',7,(select teamid from public."OperatingTeams" where name=\'Resource Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'DAS\'),true);commit;')
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'General\',7,(select teamid from public."OperatingTeams" where name=\'Resource Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'LWR\'),true);commit;')

# General - Ministry Sign Off
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'General\',10,(select teamid from public."OperatingTeams" where name=\'Resource Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'DAS\'),true);commit;')
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'General\',10,(select teamid from public."OperatingTeams" where name=\'Resource Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'LWR\'),true);commit;')

# General - Response
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'General\',14,(select teamid from public."OperatingTeams" where name=\'Resource Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'DAS\'),true);commit;')
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'General\',14,(select teamid from public."OperatingTeams" where name=\'Resource Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'LWR\'),true);commit;')

# General - Consult
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'General\',9,(select teamid from public."OperatingTeams" where name=\'Resource Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'DAS\'),true);commit;')
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'General\',9,(select teamid from public."OperatingTeams" where name=\'Resource Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'LWR\'),true);commit;')

# Personal - Open
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'Personal\',1,(select teamid from public."OperatingTeams" where name=\'Resource Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'DAS\'),true);commit;')
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'Personal\',1,(select teamid from public."OperatingTeams" where name=\'Resource Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'LWR\'),true);commit;')

# Personal - Call For Records
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'Personal\',2,(select teamid from public."OperatingTeams" where name=\'Resource Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'DAS\'),true);commit;')
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'Personal\',2,(select teamid from public."OperatingTeams" where name=\'Resource Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'LWR\'),true);commit;')

# Personal - Fee Estimate
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'Personal\',8,(select teamid from public."OperatingTeams" where name=\'Resource Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'DAS\'),true);commit;')
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'Personal\',8,(select teamid from public."OperatingTeams" where name=\'Resource Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'LWR\'),true);commit;')

# Personal - On Hold
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'Personal\',11,(select teamid from public."OperatingTeams" where name=\'Resource Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'DAS\'),true);commit;')
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'Personal\',11,(select teamid from public."OperatingTeams" where name=\'Resource Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'LWR\'),true);commit;')

# Personal - Records Review
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'Personal\',7,(select teamid from public."OperatingTeams" where name=\'Resource Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'DAS\'),true);commit;')
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'Personal\',7,(select teamid from public."OperatingTeams" where name=\'Resource Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'LWR\'),true);commit;')

# Personal - Consult
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'Personal\',9,(select teamid from public."OperatingTeams" where name=\'Resource Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'DAS\'),true);commit;')
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'Personal\',9,(select teamid from public."OperatingTeams" where name=\'Resource Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'LWR\'),true);commit;')

# Personal - Ministry Sign Off
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'Personal\',10,(select teamid from public."OperatingTeams" where name=\'Resource Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'DAS\'),true);commit;')
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'Personal\',10,(select teamid from public."OperatingTeams" where name=\'Resource Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'LWR\'),true);commit;')

# Personal - Response
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'Personal\',14,(select teamid from public."OperatingTeams" where name=\'Resource Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'DAS\'),true);commit;')
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'Personal\',14,(select teamid from public."OperatingTeams" where name=\'Resource Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'LWR\'),true);commit;')

# Personal - Closed
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'Personal\',3,(select teamid from public."OperatingTeams" where name=\'Resource Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'DAS\'),true);commit;')
    op.execute('Insert into public."FOIRequestTeams" (requesttype, requeststatusid, teamid, programareaid, isactive) values (\'Personal\',3,(select teamid from public."OperatingTeams" where name=\'Resource Team\'),(select programareaid from public."ProgramAreas" where iaocode=\'LWR\'),true);commit;')



def downgrade():

    op.execute('DELETE FROM public."FOIRequestTeams" WHERE programareaid in (select programareaid from public."ProgramAreas" where iaocode in (\'DAS\', \'LWR\'));commit;')
    
