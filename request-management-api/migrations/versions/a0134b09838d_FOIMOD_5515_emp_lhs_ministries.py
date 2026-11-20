"""FOIMOD-5515: EMP replaces ECS and LHS replaces HSG.

Revision ID: a0134b09838d
Revises: a4e9c7d2f1b6
Create Date: 2026-11-20

For each replacement, this revision:
  * creates the new ministry in ProgramAreas (bcgovcode = iaocode = new code);
  * creates its operating team "<NEW> Ministry Team";
  * copies the old ministry's active divisions;
  * copies the old ministry's FOIRequestTeams routing, with the old ministry team swapped for the new one;
  * adds an active Records DocumentPathMapper row for "<new>-<env>-e", reusing the old Records row's
    attributes (same storage account). The environment suffix comes from the old bucket name;
  * deactivates the old ministry (isactive = false). Its team, divisions, routing and bucket stay, so its
    existing requests keep working.

The old ministry's staff get access to the new ministry through MINISTRY_GROUP_ACCESS_GRANTS
(request_api/utils/ministrygroupaccess.py), not through data.

The upgrade refuses to run when a new code, team or bucket already exists, when the new bucket would be
ambiguous for Flow's "bucket ILIKE '<code>%'" lookup, or when the old ministry, its team or its Records row is
missing. Credentials are never printed.

The downgrade removes only what this revision created and reactivates the old ministries. It refuses while any
request references a new ministry.
"""
import logging

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'a0134b09838d'
down_revision = 'a4e9c7d2f1b6'
branch_labels = None
depends_on = None

logger = logging.getLogger(f'alembic.{revision}')

CREATED_BY = 'FOIMOD-5515'
CATALOGUE_TYPE = 'BC GOV Ministry'

REPLACEMENTS = (
    {'old': 'ECS', 'new': 'EMP', 'name': 'Ministry of Energy, Mines, and Petroleum Resources'},
    {'old': 'HSG', 'new': 'LHS', 'name': 'Ministry of Local Government, Housing, Sport and Culture'},
)


def _fail(message):
    raise RuntimeError(f'{revision}: {message}')


def _scalar(conn, sql, **params):
    return conn.execute(sa.text(sql), params).scalar()


def _team(code):
    return f'{code} Ministry Team'


def _old_records_row(conn, old):
    rows = conn.execute(sa.text('''
        SELECT documentpathid, bucket FROM public."DocumentPathMapper"
         WHERE category = 'Records' AND isactive AND bucket ILIKE lower(:code) || '-%'
         ORDER BY documentpathid'''), {'code': old}).fetchall()
    if len(rows) != 1:
        _fail(f'expected one active Records bucket for {old}, found {len(rows)}')
    return rows[0]


def _new_bucket(old, new, old_bucket):
    prefix = old.lower() + '-'
    if not old_bucket.lower().startswith(prefix):
        _fail(f'bucket {old_bucket} does not follow "<code>-<env>-e"')
    return new.lower() + '-' + old_bucket[len(prefix):]


def _guards(conn, r, new_bucket):
    old, new = r['old'], r['new']
    if not _scalar(conn, 'SELECT count(*) FROM public."ProgramAreas" WHERE bcgovcode = :c', c=old):
        _fail(f'ministry {old} does not exist')
    if _scalar(conn, 'SELECT count(*) FROM public."ProgramAreas" WHERE upper(bcgovcode) = :c OR upper(iaocode) = :c',
               c=new):
        _fail(f'a ministry with code {new} already exists')
    if not _scalar(conn, 'SELECT count(*) FROM public."OperatingTeams" WHERE name = :n', n=_team(old)):
        _fail(f'operating team "{_team(old)}" does not exist')
    if _scalar(conn, 'SELECT count(*) FROM public."OperatingTeams" WHERE lower(name) = lower(:n)', n=_team(new)):
        _fail(f'operating team "{_team(new)}" already exists')
    # Flow picks the records bucket with bucket ILIKE '<code>%'. The new bucket must not be matched by an
    # existing ministry's lookup, and no existing bucket may match the new ministry's lookup.
    clash = _scalar(conn, '''
        SELECT string_agg(DISTINCT x, ', ') FROM (
            SELECT m.bucket AS x FROM public."DocumentPathMapper" m
             WHERE m.category = 'Records' AND m.isactive AND m.bucket ILIKE lower(:code) || '%'
            UNION
            SELECT p.bcgovcode FROM public."ProgramAreas" p
             WHERE p.bcgovcode IS NOT NULL AND :bucket ILIKE lower(p.bcgovcode) || '%'
        ) c''', code=new, bucket=new_bucket)
    if clash:
        _fail(f'records bucket {new_bucket} would be ambiguous for Flow\'s prefix lookup: {clash}')


def _replace(conn, r):
    old, new = r['old'], r['new']
    old_row = _old_records_row(conn, old)
    new_bucket = _new_bucket(old, new, old_row.bucket)
    _guards(conn, r, new_bucket)

    old_programareaid = _scalar(conn, 'SELECT programareaid FROM public."ProgramAreas" WHERE bcgovcode = :c', c=old)
    old_teamid = _scalar(conn, 'SELECT teamid FROM public."OperatingTeams" WHERE name = :n', n=_team(old))

    programareaid = conn.execute(sa.text('''
        INSERT INTO public."ProgramAreas" (name, type, isactive, bcgovcode, iaocode)
        VALUES (:name, :type, TRUE, :code, :code)
        RETURNING programareaid'''),
        {'name': r['name'], 'type': CATALOGUE_TYPE, 'code': new},
    ).scalar()

    teamid = conn.execute(sa.text('''
        INSERT INTO public."OperatingTeams" (name, description, type, isactive)
        VALUES (:name, :name, 'ministry', TRUE)
        RETURNING teamid'''),
        {'name': _team(new)},
    ).scalar()

    # Divisions: copy the active ones, then point copied children at their copied parents.
    divisions = conn.execute(sa.text('''
        SELECT divisionid, name, sortorder, issection, parentid, specifictopersonalrequests, type, isselectable
          FROM public."ProgramAreaDivisions"
         WHERE programareaid = :p AND isactive
         ORDER BY divisionid'''), {'p': old_programareaid}).fetchall()
    copied = {}
    for division in divisions:
        copied[division.divisionid] = conn.execute(sa.text('''
            INSERT INTO public."ProgramAreaDivisions"
                (programareaid, name, isactive, created_at, createdby, sortorder, issection, parentid,
                 specifictopersonalrequests, type, isselectable)
            VALUES (:p, :name, TRUE, now(), :createdby, :sortorder, :issection, NULL,
                    :specifictopersonalrequests, :type, :isselectable)
            RETURNING divisionid'''),
            {'p': programareaid, 'name': division.name, 'createdby': CREATED_BY,
             'sortorder': division.sortorder, 'issection': division.issection,
             'specifictopersonalrequests': division.specifictopersonalrequests,
             'type': division.type, 'isselectable': division.isselectable},
        ).scalar()
    for division in divisions:
        if division.parentid is not None:
            conn.execute(sa.text('UPDATE public."ProgramAreaDivisions" SET parentid = :parent WHERE divisionid = :d'),
                         {'parent': copied.get(division.parentid), 'd': copied[division.divisionid]})

    # Routing: same request types and states as the old ministry; its ministry team becomes the new team.
    routed = conn.execute(sa.text('''
        INSERT INTO public."FOIRequestTeams" (requesttype, requeststatusid, requeststatuslabel, teamid, programareaid, isactive)
        SELECT requesttype, requeststatusid, requeststatuslabel,
               CASE WHEN teamid = :old_teamid THEN :teamid ELSE teamid END,
               :p, TRUE
          FROM public."FOIRequestTeams"
         WHERE programareaid = :old_p AND isactive'''),
        {'old_teamid': old_teamid, 'teamid': teamid, 'p': programareaid, 'old_p': old_programareaid},
    ).rowcount
    if not routed:
        logger.warning('%s: %s has no active FOIRequestTeams rows; %s gets no routing', revision, old, new)

    conn.execute(sa.text('''
        INSERT INTO public."DocumentPathMapper" (category, bucket, attributes, isactive, createdby, created_at)
        SELECT 'Records', :bucket, attributes, TRUE, :createdby, now()
          FROM public."DocumentPathMapper" WHERE documentpathid = :id'''),
        {'bucket': new_bucket, 'createdby': CREATED_BY, 'id': old_row.documentpathid},
    )

    conn.execute(sa.text('UPDATE public."ProgramAreas" SET isactive = FALSE WHERE programareaid = :p'),
                 {'p': old_programareaid})
    logger.info('%s: %s created (%d divisions, %d routing rows, bucket %s); %s deactivated',
                revision, new, len(divisions), routed, new_bucket, old)


def upgrade():
    conn = op.get_bind()
    for replacement in REPLACEMENTS:
        _replace(conn, replacement)


def downgrade():
    conn = op.get_bind()
    for r in REPLACEMENTS:
        old, new = r['old'], r['new']
        programareaid = _scalar(conn, 'SELECT programareaid FROM public."ProgramAreas" WHERE bcgovcode = :c', c=new)
        teamid = _scalar(conn, 'SELECT teamid FROM public."OperatingTeams" WHERE name = :n', n=_team(new))
        if programareaid is not None:
            if _scalar(conn, 'SELECT count(*) FROM public."FOIMinistryRequests" WHERE programareaid = :p', p=programareaid):
                _fail(f'{new} has requests; it cannot be removed')
            if _scalar(conn, '''SELECT count(*) FROM public."FOIMinistryRequestDivisions" r
                                JOIN public."ProgramAreaDivisions" v ON v.divisionid = r.divisionid
                                WHERE v.programareaid = :p''', p=programareaid):
                _fail(f'{new} divisions are tagged on requests; they cannot be removed')
        if teamid is not None and _scalar(conn, 'SELECT count(*) FROM public."OperatingTeamEmails" WHERE teamid = :t',
                                          t=teamid):
            _fail(f'"{_team(new)}" has a team mailbox row; remove it first')

        if programareaid is not None:
            conn.execute(sa.text('DELETE FROM public."FOIRequestTeams" WHERE programareaid = :p'), {'p': programareaid})
            conn.execute(sa.text('UPDATE public."ProgramAreaDivisions" SET parentid = NULL WHERE programareaid = :p'),
                         {'p': programareaid})
            conn.execute(sa.text('DELETE FROM public."ProgramAreaDivisions" WHERE programareaid = :p'), {'p': programareaid})
        if teamid is not None and not _scalar(conn, 'SELECT count(*) FROM public."FOIRequestTeams" WHERE teamid = :t',
                                              t=teamid):
            conn.execute(sa.text('DELETE FROM public."OperatingTeams" WHERE teamid = :t'), {'t': teamid})
        if programareaid is not None:
            conn.execute(sa.text('DELETE FROM public."ProgramAreas" WHERE programareaid = :p'), {'p': programareaid})
        conn.execute(sa.text('''DELETE FROM public."DocumentPathMapper"
                                WHERE category = 'Records' AND bucket ILIKE lower(:code) || '-%' AND createdby = :createdby'''),
                     {'code': new, 'createdby': CREATED_BY})
        conn.execute(sa.text('UPDATE public."ProgramAreas" SET isactive = TRUE WHERE bcgovcode = :c'), {'c': old})
