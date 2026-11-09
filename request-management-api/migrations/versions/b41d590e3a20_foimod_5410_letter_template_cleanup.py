"""FOIMOD-5410: retire obsolete letter templates and rename the OIPC application.

Revision ID: b41d590e3a20
Revises: a4e9c7d2f1b6

Data-only migration. Keep template IDs, S3 paths, content, and audit fields intact.
"""

import logging

from alembic import op
import sqlalchemy as sa

revision = "b41d590e3a20"
down_revision = "a4e9c7d2f1b6"
branch_labels = None
depends_on = None

log = logging.getLogger(__name__)

# (stable filename, current display name)
DEACTIVATE = (
    ("AExtension101D", "A - Extension - 10 1 D"),
    ("AOIPCAppConsentTimeExt", "A - OIPC - Applicant Consent Time Extension"),
    ("AOIPCSubsequentTimeExt", "A - OIPC - Subsequent Time Extension"),
    (
        "PAckIndividualandOthOutofProvCountry",
        "P - Ack - Individual and Others - Out of Province or Country",
    ),
)

OIPC_FILENAME = "AOIPCFirstTimeExtension"
OLD_OIPC_NAME = "A - OIPC - First Time Extension"
NEW_OIPC_NAME = "A - OIPC - Time Extension Application"

RENAME_SQL = sa.text('''
    UPDATE public."Template" AS t
    SET templatename = :to_name
    WHERE t.filename = :filename
      AND t.templatename = :from_name
      AND t.isactive = TRUE
      AND NOT EXISTS (
          SELECT 1 FROM public."Template" AS other
          WHERE other.templatename = :to_name AND other.isactive = TRUE
      )
''')

DEACTIVATE_SQL = sa.text('''
    UPDATE public."Template"
    SET isactive = FALSE
    WHERE filename = :filename AND templatename = :name AND isactive = TRUE
''')

REACTIVATE_SQL = sa.text('''
    UPDATE public."Template"
    SET isactive = TRUE
    WHERE filename = :filename AND templatename = :name AND isactive = FALSE
''')


def _report(action, name, rowcount):
    if rowcount == 0:
        log.warning("FOIMOD-5410: %s skipped for %r (no matching row)", action, name)
    elif rowcount > 1:
        # Roll back the migration instead of silently changing duplicate records.
        raise RuntimeError(f"FOIMOD-5410: {action} unexpectedly affected {rowcount} rows for {name!r}")
    else:
        log.info("FOIMOD-5410: %s %r", action, name)


def _rename(from_name, to_name):
    result = op.get_bind().execute(RENAME_SQL, {
        "filename": OIPC_FILENAME,
        "from_name": from_name,
        "to_name": to_name,
    })
    _report("rename", f"{from_name} -> {to_name}", result.rowcount)


def upgrade():
    connection = op.get_bind()
    for filename, name in DEACTIVATE:
        result = connection.execute(DEACTIVATE_SQL, {"filename": filename, "name": name})
        _report("deactivate", name, result.rowcount)
    _rename(OLD_OIPC_NAME, NEW_OIPC_NAME)


def downgrade():
    # All four targets were active before this migration in the verified
    # environments. Check production preconditions before promotion/rollback.
    _rename(NEW_OIPC_NAME, OLD_OIPC_NAME)
    connection = op.get_bind()
    for filename, name in DEACTIVATE:
        result = connection.execute(REACTIVATE_SQL, {"filename": filename, "name": name})
        _report("reactivate", name, result.rowcount)
