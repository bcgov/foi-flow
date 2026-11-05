"""FOIMOD-5410: retire four letter templates and rename OIPC application.

Revision ID: b41d590e3a20
Revises: a4e9c7d2f1b6
Create Date: 2026-11-04

Related: FOIMOD-5409 header/footer exclusion must be configured in GitOps.

This is a data-only migration. The filename, S3 documentpath, encodedcontent,
requesttype, templatetype, and audit columns intentionally remain unchanged.
Match by stable filename, not environment-specific templateid.
"""

from alembic import op
import sqlalchemy as sa


revision = "b41d590e3a20"
down_revision = "a4e9c7d2f1b6"
branch_labels = None
depends_on = None

# (internal filename, display name, request type)
_RETIRED = (
    ("AExtension101D", "A - Extension - 10 1 D", "General"),
    ("AOIPCAppConsentTimeExt", "A - OIPC - Applicant Consent Time Extension", "General"),
    ("AOIPCSubsequentTimeExt", "A - OIPC - Subsequent Time Extension", "General"),
    (
        "PAckIndividualandOthOutofProvCountry",
        "P - Ack - Individual and Others - Out of Province or Country",
        "Personal",
    ),
)
_SURVIVING_FILENAME = "AOIPCFirstTimeExtension"
_OLD_NAME = "A - OIPC - First Time Extension"
_NEW_NAME = "A - OIPC - Time Extension Application"


def _verify_template(connection, filename, name, request_type, active):
    """Require one matching record before changing anything."""
    rows = connection.execute(
        sa.text(
            'SELECT templateid, templatename, isactive, requesttype, templatetype '
            'FROM public."Template" WHERE filename = :filename FOR UPDATE'
        ),
        {"filename": filename},
    ).mappings().all()
    if len(rows) != 1:
        raise RuntimeError(
            f"FOIMOD-5410: expected exactly one Template row for {filename}; found {len(rows)}"
        )

    record = rows[0]
    if (
        record["templatename"] != name
        or bool(record["isactive"]) != active
        or record["requesttype"] != request_type
        or record["templatetype"] != "letter"
    ):
        raise RuntimeError(
            f"FOIMOD-5410: unexpected state for {filename}: "
            f"name={record['templatename']!r}, active={record['isactive']!r}, "
            f"requesttype={record['requesttype']!r}, "
            f"templatetype={record['templatetype']!r}"
        )


def _verify_name_available(connection, name, filename):
    other = connection.execute(
        sa.text(
            'SELECT COUNT(*) FROM public."Template" '
            'WHERE templatename = :name AND filename <> :filename'
        ),
        {"name": name, "filename": filename},
    ).scalar_one()
    if other:
        raise RuntimeError(
            f"FOIMOD-5410: display name {name!r} belongs to {other} other template(s)"
        )


def _change_active(connection, filename, name, was_active, now_active):
    rows = connection.execute(
        sa.text(
            'UPDATE public."Template" SET isactive = :new_active '
            'WHERE filename = :filename AND templatename = :name '
            'AND isactive = :old_active RETURNING templateid'
        ),
        {
            "new_active": now_active,
            "old_active": was_active,
            "filename": filename,
            "name": name,
        },
    ).all()
    if len(rows) != 1:
        raise RuntimeError(f"FOIMOD-5410: expected one status change for {filename}")


def _rename(connection, old_name, new_name):
    rows = connection.execute(
        sa.text(
            'UPDATE public."Template" SET templatename = :new_name '
            'WHERE filename = :filename AND templatename = :old_name '
            'AND isactive = TRUE RETURNING templateid'
        ),
        {
            "filename": _SURVIVING_FILENAME,
            "old_name": old_name,
            "new_name": new_name,
        },
    ).all()
    if len(rows) != 1:
        raise RuntimeError("FOIMOD-5410: expected one OIPC template rename")


def upgrade():
    connection = op.get_bind()
    # Preflight every target before writing any records.
    for filename, name, request_type in _RETIRED:
        _verify_template(connection, filename, name, request_type, True)
    _verify_template(connection, _SURVIVING_FILENAME, _OLD_NAME, "General", True)
    _verify_name_available(connection, _NEW_NAME, _SURVIVING_FILENAME)

    for filename, name, _request_type in _RETIRED:
        _change_active(connection, filename, name, True, False)
    _rename(connection, _OLD_NAME, _NEW_NAME)


def downgrade():
    connection = op.get_bind()
    for filename, name, request_type in _RETIRED:
        _verify_template(connection, filename, name, request_type, False)
    _verify_template(connection, _SURVIVING_FILENAME, _NEW_NAME, "General", True)
    _verify_name_available(connection, _OLD_NAME, _SURVIVING_FILENAME)

    for filename, name, _request_type in _RETIRED:
        _change_active(connection, filename, name, False, True)
    _rename(connection, _NEW_NAME, _OLD_NAME)
