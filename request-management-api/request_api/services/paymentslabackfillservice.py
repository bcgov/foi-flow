"""One-time backfill of the n8n ``foi-payment-sla`` Data Table from Camunda.

Payments started in Camunda have no row in ``foi-payment-sla``, so after cutover n8n could not expire them or
mark the applicant's Form.io submission paid. This service finds the payments Camunda is still waiting on and
creates the missing rows with the same shape the n8n fee workflow writes.

Sources of truth
- Camunda runtime: ``foi-fee-processing`` instances waiting at the payment gateway, plus the ids and expiry
  date held as process variables (``formId``, ``submissionId``, ``paymentExpiryDate``, ``expirycounter``).
- FOI database: the payment must still be unpaid. Same rule as ``FOIRequestPayment.getactivepayment``; the
  Form.io ids in its ``paymenturl`` must equal the Camunda ones.
- n8n Data Table: existing rows, so a rerun never duplicates, resets a deadline or revives a closed row.

Camunda keeps an instance waiting after it has expired and notified (``expirycounter`` >= 1). Backfilling such a
payment as ``ACTIVE`` would make the n8n expiry job notify the applicant a second time, so it is reported
separately and only written, as ``EXPIRED``, when ``include_expired`` is set.
"""

import json
import logging
import os
import re
import uuid
from datetime import datetime, timezone
from urllib.parse import quote, urlencode

import pytz
import requests

FEE_PROCESS_KEY = 'foi-fee-processing'
PAYMENT_WAIT_ACTIVITY = 'Gateway_1771ld6'  # event based gateway: waits for foi-manage-payment or the daily timer
SLA_TYPE = 'payment-expiry'
SLA_TABLE_NAME = 'foi-payment-sla'
VANCOUVER = pytz.timezone('America/Vancouver')

# Only these Camunda variables are requested. The instances also hold credentials and tokens.
CAMUNDA_VARIABLES = (
    'formId', 'submissionId', 'formUrl', 'paymentExpiryDate', 'paymentstatus', 'expirycounter',
    'foiRequestID', 'ministryRequestID', 'fileNumber', 'servicekey', 'templateName', 'prevStatus',
    'isofflinepayment', 'applicantCorrespondenceId', 'foiRequestMetaData',
)

OBJECT_ID = re.compile(r'^[0-9a-f]{24}$')
PAYMENT_URL_IDS = re.compile(r'/form/([0-9a-fA-F]{24})/submission/([0-9a-fA-F]{24})')

# Outcomes
CREATE = 'create'
ALREADY_VALID = 'already_valid'
EXPIRED_NOTIFIED = 'expired_notified_not_written'
SKIPPED = 'skipped_ineligible'
INVALID_IDS = 'invalid_identifiers'
EXPIRY_UNRESOLVED = 'expiry_unresolved'
SLA_CONFLICT = 'sla_conflict'
ERROR = 'error'
MANUAL_REVIEW = (INVALID_IDS, EXPIRY_UNRESOLVED, SLA_CONFLICT, ERROR)

OPEN_STATUSES = ('ACTIVE', 'PENDING')
TERMINAL_STATUSES = ('PAID', 'CANCELLED', 'EXPIRED')


class BackfillSourceError(Exception):
    """A source (Camunda, FOI database, n8n) failed. The run is aborted instead of guessing."""


def _clean(value):
    text = '' if value is None else str(value).strip()
    return '' if text.lower() in ('undefined', 'null', 'none') else text


def _to_int(value):
    try:
        text = _clean(value)
        return int(text) if text else None
    except (TypeError, ValueError):
        return None


def _to_bool(value):
    if isinstance(value, bool):
        return value
    return _clean(value).lower() == 'true'


def parse_payment_url(url):
    """Return ``(form_id, submission_id)`` from a payment URL, or ``(None, None)``."""
    match = PAYMENT_URL_IDS.search(url or '')
    return (match.group(1).lower(), match.group(2).lower()) if match else (None, None)


def compute_expires_at(expiry_date):
    """Same rule as the ``Build Payment SLA`` node: the end of the expiry day in America/Vancouver, as UTC.

    A date-only value means 23:59:59.999 local time. Returns ``None`` for a missing or invalid date. There is
    no 20 day fallback: a payment whose deadline is unknown is reported, not given an invented one.
    """
    raw = _clean(expiry_date)
    if not raw:
        return None
    try:
        parsed = datetime.fromisoformat(raw.replace('Z', '+00:00'))
    except ValueError:
        return None
    if len(raw) <= 10:
        parsed = parsed.replace(hour=23, minute=59, second=59, microsecond=999000)
    if parsed.tzinfo is None:
        parsed = VANCOUVER.localize(parsed)  # after the end-of-day replace, so a DST change day stays right
    utc = parsed.astimezone(timezone.utc)
    return utc.strftime('%Y-%m-%dT%H:%M:%S.') + '%03dZ' % (utc.microsecond // 1000)


def _initiate_metadata(variables):
    """The ``foiRequestMetaData`` Camunda kept from the initiate event, as a dict (``{}`` when absent/unreadable).

    n8n reads it back from the row's ``metadata`` to post ``foi-iao-complete`` after a PAID outcome (the
    Camunda 'Sync FOI Status in WF' step), so it must be the same data the ``Build Payment SLA`` node stores.
    """
    raw = variables.get('foiRequestMetaData')
    if isinstance(raw, dict):
        return raw
    text = _clean(raw)
    for candidate in (text, text.replace("'", '"')):  # Camunda's BPMN itself reads it with this quote fix
        try:
            parsed = json.loads(candidate)
        except ValueError:
            continue
        if isinstance(parsed, dict):
            return parsed
    return {}


def payment_expiry_reached(payment_expiry_date, expires_at, now):
    """Same test as the ``Apply BPMN Expiry Window`` node of the FOI Payment Expiry SLA Job.

    The job expires an ACTIVE row once ``now - expiry > -1 day`` (Camunda's first daily run inside the one-day
    window around the expiry date, and every run after it), where ``expiry`` is ``payment_expiry_date`` parsed
    like JavaScript ``new Date()`` (a date-only value is midnight UTC) and ``expires_at`` is only the fallback.
    """
    raw = _clean(payment_expiry_date) or _clean(expires_at)
    expiry = _parse_utc(raw if len(raw) > 10 else raw + 'T00:00:00+00:00') if raw else None
    return expiry is not None and (now - expiry).total_seconds() > -86400


def _parse_utc(value):
    try:
        return datetime.fromisoformat(str(value).replace('Z', '+00:00')).astimezone(timezone.utc)
    except (TypeError, ValueError):
        return None


def service_key_for(variables):
    """Same choice as the ``Plan Payment SLA`` node."""
    if _clean(variables.get('servicekey')) == 'correspondence':
        return 'correspondence'
    return 'payoutstanding' if _clean(variables.get('prevStatus')) == 'Response' else 'payonline'


# --------------------------------------------------------------------------------------------------------------
# Sources
# --------------------------------------------------------------------------------------------------------------

class CamundaFeeSource:
    """Reads ``foi-fee-processing`` instances, where they wait and a whitelist of their variables."""

    def __init__(self, base_url=None, token_provider=None, session=None, page_size=500, timeout=60):
        self.base_url = (base_url or os.getenv('BPM_ENGINE_REST_URL') or '').rstrip('/')
        self._token_provider = token_provider
        self.session = session or requests.Session()
        self.page_size = page_size
        self.timeout = timeout

    def _headers(self):
        if self._token_provider is None:
            from request_api.services.external.camundaservice import camundaservice  # pylint: disable=import-outside-toplevel
            self._token_provider = camundaservice()._getserviceaccounttoken_  # pylint: disable=protected-access
        return {'Authorization': 'Bearer ' + self._token_provider(), 'Content-Type': 'application/json'}

    def _post(self, path, body, params=None):
        response = self.session.post(self.base_url + path, data=json.dumps(body), params=params,
                                     headers=self._headers(), timeout=self.timeout)
        if not response.ok:
            raise BackfillSourceError('Camunda %s answered HTTP %s' % (path, response.status_code))
        return response.json()

    def _paged(self, path, body):
        items, first = [], 0
        while True:
            page = self._post(path, body, {'firstResult': first, 'maxResults': self.page_size})
            items.extend(page)
            if len(page) < self.page_size:
                return items
            first += self.page_size

    def fetch(self):
        """Return ``[{'id', 'suspended', 'waiting', 'variables'}]`` for every fee-processing instance."""
        if not self.base_url:
            raise BackfillSourceError('BPM_ENGINE_REST_URL is not set')
        order = [{'sortBy': 'instanceId', 'sortOrder': 'asc'}]
        instances = self._paged('/process-instance', {'processDefinitionKey': FEE_PROCESS_KEY, 'sorting': order})
        waiting = {e['processInstanceId'] for e in self._paged(
            '/execution', {'processDefinitionKey': FEE_PROCESS_KEY, 'activityId': PAYMENT_WAIT_ACTIVITY,
                           'sorting': order})}
        ids = [i['id'] for i in instances]
        variables = {i: {} for i in ids}
        for start in range(0, len(ids), 50):
            chunk = ids[start:start + 50]
            for var in self._post('/variable-instance', {'processInstanceIdIn': chunk,
                                                         'variableNameIn': list(CAMUNDA_VARIABLES)},
                                  {'deserializeValues': 'false'}):
                scope_is_process = var.get('executionId') == var.get('processInstanceId')
                if var['name'] not in variables[var['processInstanceId']] or scope_is_process:
                    variables[var['processInstanceId']][var['name']] = var.get('value')
        return [{'id': i['id'], 'suspended': bool(i.get('suspended')), 'waiting': i['id'] in waiting,
                 'variables': variables[i['id']]} for i in instances]


class FoiPaymentSource:
    """Reads payments and requests from the FOI database. Read only."""

    # Mirrors FOIRequestPayment.getactivepayment: latest version of each payment, not System_Cancel, with a
    # payment URL and nothing paid.
    ACTIVE_SQL = """
        SELECT fp1.ministryrequestid, fp1.paymentid, fp1.version, fp1.paymenturl, fp1.paymentexpirydate
        FROM "FOIRequestPayments" fp1
        JOIN (SELECT DISTINCT ON (paymentid) paymentid, version FROM "FOIRequestPayments"
              {scope} ORDER BY paymentid, version DESC) fp2
          ON fp1.paymentid = fp2.paymentid AND fp1.version = fp2.version
        WHERE fp1.createdby <> 'System_Cancel' AND fp1.paymenturl IS NOT NULL AND fp1.paidamount IS NULL"""
    REQUEST_SQL = """
        SELECT DISTINCT ON (foiministryrequestid) foiministryrequestid, foirequest_id, filenumber
        FROM "FOIMinistryRequests" WHERE foiministryrequestid = ANY(:ids)
        ORDER BY foiministryrequestid, version DESC"""

    def __init__(self, session=None):
        self._session = session
        self._engine = None

    @property
    def session(self):
        """A private session on the configured FOI database (no Flask app needed)."""
        if self._session is None:
            from sqlalchemy import create_engine  # pylint: disable=import-outside-toplevel
            from sqlalchemy.orm import Session  # pylint: disable=import-outside-toplevel
            import request_api.config as config  # pylint: disable=import-outside-toplevel
            from werkzeug.utils import import_string  # pylint: disable=import-outside-toplevel
            settings = import_string(config.CONFIGURATION[os.getenv('FLASK_ENV', 'development')])
            self._engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
            self._session = Session(self._engine)
        return self._session

    def close(self):
        if self._session is not None:
            self._session.rollback()
            self._session.close()
        if self._engine is not None:
            self._engine.dispose()

    def _execute(self, sql, params=None):
        from sqlalchemy import text  # pylint: disable=import-outside-toplevel
        try:
            if not self.session.in_transaction():
                self.session.execute(text('SET TRANSACTION READ ONLY'))  # the backfill never writes to the FOI database
            return [dict(row._mapping) for row in self.session.execute(text(sql), params or {})]
        except Exception as exc:
            self.session.rollback()
            raise BackfillSourceError('FOI database query failed: %s' % type(exc).__name__) from exc

    def active_payments(self, ministry_request_ids):
        """``{ministry_request_id: [{'paymentid', 'form_id', 'submission_id', 'expiry'}]}``."""
        scope = 'WHERE ministryrequestid = ANY(:ids)'
        rows = self._execute(self.ACTIVE_SQL.format(scope=scope), {'ids': sorted(ministry_request_ids)})
        return self._group(rows)

    def active_payment_request_ids(self):
        """Every ministry request that has an active payment (used to report payments Camunda does not hold)."""
        return {row['ministryrequestid'] for row in self._execute(self.ACTIVE_SQL.format(scope=''))}

    def requests(self, ministry_request_ids):
        rows = self._execute(self.REQUEST_SQL, {'ids': sorted(ministry_request_ids)})
        return {row['foiministryrequestid']: {'foi_request_id': row['foirequest_id'], 'file_number': row['filenumber']}
                for row in rows}

    @staticmethod
    def _group(rows):
        grouped = {}
        for row in rows:
            form_id, submission_id = parse_payment_url(row['paymenturl'])
            expiry = row['paymentexpirydate']
            grouped.setdefault(row['ministryrequestid'], []).append({
                'paymentid': row['paymentid'], 'form_id': form_id, 'submission_id': submission_id,
                'payment_url': row['paymenturl'],
                'expiry': expiry.strftime('%Y-%m-%d') if hasattr(expiry, 'strftime') else _clean(expiry)[:10],
            })
        return grouped


class N8NStoreError(BackfillSourceError):
    """The n8n Data Table API failed."""


class N8NPaymentSlaStore:
    """The ``foi-payment-sla`` Data Table through the n8n public API (``/api/v1/data-tables``)."""

    def __init__(self, base_url=None, api_key=None, table_name=SLA_TABLE_NAME, table_id=None, session=None,
                 timeout=30):
        self.base_url = (base_url or os.getenv('N8N_BASE_URL') or '').rstrip('/')
        self._api_key = api_key or os.getenv('N8N_API_KEY')
        self.table_name = table_name
        self._table_id = table_id or os.getenv('N8N_PAYMENT_SLA_TABLE_ID')
        self.session = session or requests.Session()
        self.timeout = timeout

    def _call(self, method, path, params=None, **kwargs):
        if not self.base_url or not self._api_key:
            raise N8NStoreError('N8N_BASE_URL and N8N_API_KEY must be set')
        url = self.base_url + '/api/v1' + path
        if params:  # n8n rejects a filter whose ':' ',' '{' are not percent-encoded, which requests would leave raw
            url += '?' + urlencode(params, quote_via=quote, safe='')
        response = self.session.request(method, url, timeout=self.timeout,
                                        headers={'X-N8N-API-KEY': self._api_key, 'Accept': 'application/json'},
                                        **kwargs)
        if not response.ok:
            raise N8NStoreError('n8n %s %s answered HTTP %s' % (method, path, response.status_code))
        return response.json() if response.content else None

    @staticmethod
    def _filter(**equals):
        return json.dumps({'type': 'and', 'filters': [
            {'columnName': k, 'condition': 'eq', 'value': v} for k, v in equals.items()]})

    def table_id(self):
        if not self._table_id:
            matches = [t for t in self._pages('/data-tables') if t.get('name') == self.table_name]
            if len(matches) != 1:
                raise N8NStoreError('Expected exactly one data table named %s, found %d'
                                    % (self.table_name, len(matches)))
            self._table_id = matches[0]['id']
        return self._table_id

    def _pages(self, path, params=None):
        rows, cursor = [], None
        while True:
            query = dict(params or {}, limit=250)
            if cursor:
                query['cursor'] = cursor
            page = self._call('GET', path, params=query) or {}
            rows.extend(page.get('data', []))
            cursor = page.get('nextCursor')
            if not cursor:
                return rows

    def list_rows(self, ministry_request_id=None):
        """Every ``payment-expiry`` row, or only those of one ministry request."""
        filters = {'sla_type': SLA_TYPE}
        if ministry_request_id is not None:
            filters['ministry_request_id'] = str(ministry_request_id)
        return self._pages('/data-tables/%s/rows' % self.table_id(), {'filter': self._filter(**filters)})

    def insert(self, row):
        result = self._call('POST', '/data-tables/%s/rows' % self.table_id(),
                            json={'data': [row], 'returnType': 'all'})
        inserted = result.get('data', result) if isinstance(result, dict) else result
        if not inserted:
            raise N8NStoreError('n8n returned no inserted row')
        return inserted[0]

    def delete(self, row_id):
        self._call('DELETE', '/data-tables/%s/rows/delete' % self.table_id(),
                   params={'filter': self._filter(id=row_id)})


# --------------------------------------------------------------------------------------------------------------
# Backfill
# --------------------------------------------------------------------------------------------------------------

class PaymentSlaBackfill:
    """Classifies every Camunda fee instance, plans the missing SLA rows and (optionally) writes them."""

    def __init__(self, camunda, foi, store, apply=False, include_expired=False, ministry_request_ids=None,
                 run_id=None, operator=None, clock=None):
        self.camunda, self.foi, self.store = camunda, foi, store
        self.apply = apply
        self.include_expired = include_expired
        self.only = set(ministry_request_ids or [])
        self.run_id = run_id or uuid.uuid4().hex[:12]
        self.operator = operator or os.getenv('USERNAME') or os.getenv('USER') or 'unknown'
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    # -- public ----------------------------------------------------------------------------------------------

    def run(self):
        started = self.clock()
        instances = self.camunda.fetch()
        records = [self._record(i) for i in instances]
        pending = []
        for record in records:
            if not record['_waiting']:
                self._mark(record, SKIPPED, 'not_waiting_for_payment')
                continue
            self._screen(record)
            if not record['outcome']:
                pending.append(record)
        self._match_database(pending)
        pending = [r for r in pending if not r['outcome']]
        self._resolve_groups(pending)
        pending = [r for r in pending if not r['outcome']]
        self._check_expiry(pending)
        pending = [r for r in pending if not r['outcome']]
        self._plan(pending)
        for record in records:
            if record['outcome'] == CREATE and self.apply:
                self._write(record)
        report = self._report(records, len(instances), started)
        for record in records:  # internal fields never leave this object
            for key in [k for k in record if k.startswith('_')]:
                del record[key]
        return report

    # -- classification ---------------------------------------------------------------------------------------

    def _record(self, instance):
        v = instance['variables']
        return {
            'process_instance_id': instance['id'], 'suspended': instance['suspended'],
            'ministry_request_id': _to_int(v.get('ministryRequestID')), 'foi_request_id': _to_int(v.get('foiRequestID')),
            'file_number': _clean(v.get('fileNumber')) or None, 'outcome': None, 'reason': None, 'detail': None,
            '_waiting': instance['waiting'], '_vars': v,
        }

    @staticmethod
    def _mark(record, outcome, reason, detail=None):
        record['outcome'], record['reason'], record['detail'] = outcome, reason, detail

    def _screen(self, record):
        """Cheap checks on Camunda data alone."""
        v = record['_vars']
        status = _clean(v.get('paymentstatus')).upper()
        if self.only and record['ministry_request_id'] not in self.only:
            return self._mark(record, SKIPPED, 'outside_requested_scope')
        if status in ('PAID', 'CANCELLED'):
            return self._mark(record, SKIPPED, 'camunda_payment_%s' % status.lower())
        if status not in ('NOT PAID', 'NA', ''):
            return self._mark(record, SLA_CONFLICT, 'unexpected_camunda_payment_status', status)
        if _to_bool(v.get('isofflinepayment')):
            return self._mark(record, SKIPPED, 'offline_payment')
        if record['ministry_request_id'] is None:
            return self._mark(record, INVALID_IDS, 'missing_or_invalid_ministry_request_id')
        form_id, submission_id = _clean(v.get('formId')).lower(), _clean(v.get('submissionId')).lower()
        if not form_id:
            return self._mark(record, INVALID_IDS, 'missing_form_id')
        if not submission_id:
            return self._mark(record, INVALID_IDS, 'missing_submission_id')
        if not OBJECT_ID.match(form_id):
            return self._mark(record, INVALID_IDS, 'invalid_form_id')
        if not OBJECT_ID.match(submission_id):
            return self._mark(record, INVALID_IDS, 'invalid_submission_id')
        url_ids = re.search(r'/form/([0-9a-fA-F]{24})/submission/([0-9a-fA-F]{24})', _clean(v.get('formUrl')))
        if url_ids and (url_ids.group(1).lower(), url_ids.group(2).lower()) != (form_id, submission_id):
            return self._mark(record, INVALID_IDS, 'form_url_disagrees_with_variables')
        record['_ids'] = (form_id, submission_id)
        return None

    def _match_database(self, records):
        """Keep the instances whose Form.io ids belong to a payment the FOI database still shows as unpaid."""
        if not records:
            return
        request_ids = {r['ministry_request_id'] for r in records}
        payments = self.foi.active_payments(request_ids)
        requests_info = self.foi.requests(request_ids)
        for record in records:
            info = requests_info.get(record['ministry_request_id'], {})
            record['foi_request_id'] = record['foi_request_id'] or info.get('foi_request_id')
            record['file_number'] = record['file_number'] or info.get('file_number')
            active = payments.get(record['ministry_request_id'], [])
            if not active:
                self._mark(record, SKIPPED, 'database_shows_no_unpaid_payment')
                continue
            match = [p for p in active if (p['form_id'], p['submission_id']) == record['_ids']]
            record['_payment'] = match[0] if match else None
        # an unmatched instance is stale when a sibling instance for the same request does match
        matched_requests = {r['ministry_request_id'] for r in records if not r['outcome'] and r['_payment']}
        for record in records:
            if record['outcome'] or record['_payment']:
                continue
            if record['ministry_request_id'] in matched_requests:
                self._mark(record, SKIPPED, 'superseded_instance')
            else:
                self._mark(record, INVALID_IDS, 'ids_not_found_in_database_payment_url')

    def _resolve_groups(self, records):
        """One payment, one row: duplicate instances collapse, several active payments for a request do not."""
        by_request = {}
        for record in records:
            by_request.setdefault(record['ministry_request_id'], []).append(record)
        for group in by_request.values():
            if len({r['_ids'] for r in group}) > 1:
                for record in group:
                    self._mark(record, SLA_CONFLICT, 'multiple_active_payments_for_request',
                               'one SLA row per request; review which payment is current')
                continue
            group.sort(key=lambda r: (r['suspended'], r['process_instance_id']))
            primary, duplicates = group[0], group[1:]
            same = all(self._expiry_signature(d) == self._expiry_signature(primary) for d in duplicates)
            for duplicate in duplicates:
                if same:
                    self._mark(duplicate, SKIPPED, 'duplicate_instance_for_same_payment',
                               'kept instance %s' % primary['process_instance_id'])
                else:
                    self._mark(duplicate, EXPIRY_UNRESOLVED, 'duplicate_instances_disagree_on_expiry')
            if not same:
                self._mark(primary, EXPIRY_UNRESOLVED, 'duplicate_instances_disagree_on_expiry')

    @staticmethod
    def _expiry_signature(record):
        v = record['_vars']
        return _clean(v.get('paymentExpiryDate')), (_to_int(v.get('expirycounter')) or 0) > 0

    def _check_expiry(self, records):
        for record in records:
            v = record['_vars']
            raw = _clean(v.get('paymentExpiryDate'))
            expires_at = compute_expires_at(raw)
            if not raw:
                self._mark(record, EXPIRY_UNRESOLVED, 'missing_payment_expiry_date')
            elif not expires_at:
                self._mark(record, EXPIRY_UNRESOLVED, 'invalid_payment_expiry_date', raw)
            elif _to_int(v.get('expirycounter')) is None:
                self._mark(record, EXPIRY_UNRESOLVED, 'missing_expirycounter',
                           'cannot tell whether the expiry notification was already sent')
            elif record['_payment']['expiry'] and record['_payment']['expiry'] != raw[:10]:
                self._mark(record, EXPIRY_UNRESOLVED, 'expiry_date_differs_from_database',
                           'camunda %s, database %s' % (raw[:10], record['_payment']['expiry']))
            else:
                record['_expires_at'], record['_raw_expiry'] = expires_at, raw[:10]
                record['expired_in_camunda'] = _to_int(v.get('expirycounter')) >= 1

    # -- planning and writing ---------------------------------------------------------------------------------

    def _plan(self, records):
        if not records:
            return
        existing = {}
        for row in self.store.list_rows():
            existing.setdefault(_to_int(row.get('ministry_request_id')), []).append(row)
        for record in records:
            wanted = 'EXPIRED' if record['expired_in_camunda'] else 'ACTIVE'
            record['expiry_state'] = 'expired_and_notified_in_camunda' if record['expired_in_camunda'] else 'not_yet_expired'
            record['expires_at'] = record['_expires_at']
            rows = existing.get(record['ministry_request_id'], [])
            conflict = self._conflict(record, rows, wanted)
            if conflict == ALREADY_VALID:
                valid = [r for r in rows if self._same_payment(r, record) and r.get('sla_status') == wanted][0]
                record['sla_row_id'] = valid.get('id')
                self._mark(record, ALREADY_VALID, 'valid_%s_row_present' % wanted.lower())
            elif conflict:
                self._mark(record, SLA_CONFLICT, conflict)
            elif wanted == 'EXPIRED' and not self.include_expired:
                self._mark(record, EXPIRED_NOTIFIED, 'expired_and_notified_in_camunda',
                           'no row written; use include_expired to write an EXPIRED row')
            else:
                record['_row'] = self._build_row(record, wanted)
                self._mark(record, CREATE, 'insert_%s_row' % wanted.lower())

    @staticmethod
    def _same_payment(row, record):
        return (_clean(row.get('submission_id')).lower(), _clean(row.get('form_id')).lower()) == (
            record['_ids'][1], record['_ids'][0])

    def _conflict(self, record, rows, wanted):
        """Returns ALREADY_VALID, a conflict reason, or None when a row can be written."""
        same = [r for r in rows if self._same_payment(r, record)]
        others_open = [r for r in rows if r.get('sla_status') in OPEN_STATUSES and not self._same_payment(r, record)]
        if any(not (_clean(r.get('form_id')) and _clean(r.get('submission_id'))) for r in others_open):
            return 'open_sla_row_without_form_ids'
        if others_open:
            return 'open_sla_row_for_a_different_payment'
        if len([r for r in same if r.get('sla_status') in OPEN_STATUSES]) > 1:
            return 'duplicate_open_sla_rows_for_same_payment'
        statuses = [r.get('sla_status') for r in same]
        if wanted in statuses:
            row = [r for r in same if r.get('sla_status') == wanted][0]
            if wanted == 'ACTIVE' and not _clean(row.get('expires_at')):
                return 'existing_active_row_has_no_expires_at'
            return ALREADY_VALID
        if 'PENDING' in statuses:
            return 'pending_row_for_same_payment'
        if statuses:  # the same payment already ended (or is ACTIVE while Camunda says expired): never revive it
            return 'existing_%s_row_for_same_payment' % statuses[0].lower()
        return None

    def _build_row(self, record, status):
        v, ids = record['_vars'], record['_ids']
        correspondence_id = _to_int(v.get('applicantCorrespondenceId'))
        initiate = _initiate_metadata(v)
        metadata = {'source': 'camunda-backfill', 'backfill_run_id': self.run_id,
                    'camunda_process_instance_id': record['process_instance_id']}
        if initiate:  # same shape as 'Build Payment SLA': the event body with foiRequestMetaData as a JSON string
            metadata['foiRequestMetaData'] = json.dumps(initiate)
        note = 'BACKFILL(camunda) run %s: instance %s, %s expirycounter=%s' % (
            self.run_id, record['process_instance_id'],
            'expired and notified in Camunda,' if status == 'EXPIRED' else 'waiting for payment,',
            _to_int(v.get('expirycounter')))
        row = {
            'sla_type': SLA_TYPE, 'sla_status': status,
            'foi_request_id': str(record['foi_request_id'] or ''),
            'ministry_request_id': str(record['ministry_request_id']),
            'file_number': record['file_number'] or '', 'service_key': service_key_for(v),
            'template_name': _clean(v.get('templateName')), 'prev_status': _clean(v.get('prevStatus')),
            'next_state_name': _clean(initiate.get('nextStateName')), 'applicant_correspondence_id': str(correspondence_id) if correspondence_id else '',
            'payment_status': 'EXPIRED' if status == 'EXPIRED' else 'NOT PAID',
            'payment_url': record['_payment']['payment_url'], 'form_id': ids[0], 'submission_id': ids[1],
            'payment_expiry_date': record['_raw_expiry'], 'expires_at': record['_expires_at'],
            'metadata': json.dumps(metadata),
            'comments': note,
        }
        if status == 'EXPIRED':
            row['completed_at'] = self.clock().strftime('%Y-%m-%dT%H:%M:%S.000Z')
        return row

    def _write(self, record):
        """Insert one row. A failure is recorded and the run continues; a rerun picks the record up again."""
        row = record['_row']
        try:
            inserted = self.store.insert(row)
            record['sla_row_id'] = inserted.get('id')
            clash = self._clash(row, inserted)
            if clash:
                self.store.delete(inserted['id'])
                record['sla_row_id'] = None
                self._mark(record, SLA_CONFLICT, 'concurrent_run_created_a_row_first',
                           'own row %s removed; kept row %s' % (inserted['id'], clash['id']))
        except Exception as exc:  # pylint: disable=broad-except
            logging.error('payment SLA backfill: write failed for instance %s: %s',
                          record['process_instance_id'], type(exc).__name__)
            self._mark(record, ERROR, 'write_failed', '%s: %s' % (type(exc).__name__, exc))

    def _clash(self, row, inserted):
        """An older row that makes the one just inserted a duplicate (another run won the race), else None."""
        rows = self.store.list_rows(row['ministry_request_id'])
        older = [r for r in rows if r['id'] < inserted['id'] and (
            r.get('sla_status') in OPEN_STATUSES if row['sla_status'] == 'ACTIVE' else
            (r.get('sla_status') == 'EXPIRED' and r.get('submission_id') == row['submission_id']))]
        return min(older, key=lambda r: r['id']) if older else None

    # -- reporting --------------------------------------------------------------------------------------------

    def _report(self, records, examined, started):
        by_outcome, by_reason = {}, {}
        for record in records:
            by_outcome[record['outcome']] = by_outcome.get(record['outcome'], 0) + 1
            key = '%s/%s' % (record['outcome'], record['reason'])
            by_reason[key] = by_reason.get(key, 0) + 1
        written = self.apply
        # eligible = verified unpaid online payments: valid ids, resolved deadline, the database agrees
        eligible = [r for r in records if r.get('expiry_state')]
        active_needed = [r for r in eligible if r['expiry_state'] == 'not_yet_expired']
        covered = (ALREADY_VALID, CREATE)  # CREATE means written when applying, planned in a dry run
        missing_now = [r for r in active_needed if r['outcome'] != ALREADY_VALID
                       and not (written and r['outcome'] == CREATE)]
        missing_after_apply = [r for r in active_needed if r['outcome'] not in covered]
        now = self.clock()
        overdue = [r for r in active_needed if r['outcome'] in covered
                   and payment_expiry_reached(r['_raw_expiry'], r['expires_at'], now)]
        covered_ids = {r['ministry_request_id'] for r in records if r['_waiting']}
        db_only = None
        try:
            db_only = len(self.foi.active_payment_request_ids() - covered_ids)
        except BackfillSourceError as exc:
            logging.warning('payment SLA backfill: population B count unavailable: %s', exc)
        summary = {
            'camunda_instances_examined': examined,
            'candidate_payments_waiting_in_camunda': sum(1 for r in records if r['_waiting']),
            'eligible_unpaid_online_payments': len(eligible),
            'eligible_not_yet_expired_needing_active_row': len(active_needed),
            'eligible_expired_and_notified_in_camunda': len(eligible) - len(active_needed),
            'sla_rows_already_present_valid': by_outcome.get(ALREADY_VALID, 0),
            'sla_rows_created' if written else 'sla_rows_would_be_created': by_outcome.get(CREATE, 0),
            'active_rows_created' if written else 'active_rows_would_be_created':
                sum(1 for r in records if r['outcome'] == CREATE and r['reason'] == 'insert_active_row'),
            'expired_rows_created' if written else 'expired_rows_would_be_created':
                sum(1 for r in records if r['outcome'] == CREATE and r['reason'] == 'insert_expired_row'),
            'expired_and_notified_not_written': by_outcome.get(EXPIRED_NOTIFIED, 0),
            'skipped_ineligible': by_outcome.get(SKIPPED, 0),
            'missing_or_invalid_form_or_submission_id': by_outcome.get(INVALID_IDS, 0),
            'missing_or_ambiguous_expiry': by_outcome.get(EXPIRY_UNRESOLVED, 0),
            'conflicting_or_terminal_sla_state': by_outcome.get(SLA_CONFLICT, 0),
            'errors': by_outcome.get(ERROR, 0),
            'eligible_active_payments_still_missing_active_row': len(missing_now),
            'eligible_active_payments_missing_active_row_after_apply': len(missing_after_apply),
            'active_rows_past_deadline_notified_at_next_expiry_run': len(overdue),
            'database_unpaid_payments_without_camunda_instance': db_only,
        }
        review = [r for r in records if r['outcome'] in MANUAL_REVIEW]
        return {
            'run': {'id': self.run_id, 'mode': 'apply' if written else 'dry-run',
                    'include_expired': self.include_expired, 'operator': self.operator,
                    'started_at': started.isoformat(), 'finished_at': self.clock().isoformat()},
            'summary': summary,
            'by_outcome_and_reason': dict(sorted(by_reason.items())),
            'manual_review_required': len(review),
            'records': [self._public(r) for r in records],
        }

    @staticmethod
    def _public(record):
        out = {k: v for k, v in record.items() if not k.startswith('_')}
        if record['outcome'] in (CREATE, ALREADY_VALID):  # Form.io ids only where a row exists or is planned
            out['form_id'], out['submission_id'] = record['_ids']
        return out


def format_summary(report):
    """Plain text for the console. Counts and references only; record detail is in the report file."""
    run, summary = report['run'], report['summary']
    lines = ['Payment SLA backfill  run=%s  mode=%s  include_expired=%s' % (run['id'], run['mode'].upper(),
                                                                             run['include_expired'])]
    lines += ['  %-72s %s' % (key, value) for key, value in summary.items()]
    lines.append('Outcome / reason')
    lines += ['  %-72s %s' % (key, value) for key, value in report['by_outcome_and_reason'].items()]
    review = [r for r in report['records'] if r['outcome'] in MANUAL_REVIEW]
    lines.append('Manual review required: %d' % len(review))
    for r in review:
        lines.append('  instance=%s ministry_request=%s foi_request=%s file=%s  %s: %s%s' % (
            r['process_instance_id'], r['ministry_request_id'], r['foi_request_id'], r['file_number'],
            r['outcome'], r['reason'], ' (%s)' % r['detail'] if r['detail'] else ''))
    return '\n'.join(lines)
