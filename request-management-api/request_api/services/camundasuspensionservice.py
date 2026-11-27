"""Suspend and reactivate Camunda process instances as part of the Camunda to n8n migration.

After cutover n8n owns the online payments. A ``foi-fee-processing`` instance that stays active would run its own
daily 13:00 UTC timer and call the expiry and cancel APIs a second time (and the expiry API does not check that the
payment is still unpaid). Suspending the instance stops its timers and keeps it, so a rollback can reactivate it.

Scope
- Default: ``foi-fee-processing`` instances only, waiting at the payment gateway, with no open incident, and only when
  n8n owns the payment (a ``foi-payment-sla`` row for the same ministry request, form and submission).
- Optional: ``foi-request`` and ``foi-request-processing`` (inert; they do nothing on their own).
- Never: ``foi-email-processing`` (drain it instead), ``cache_refresh``, ``due_reminder_notifications`` and
  ``foi-rawrequest-api-manager``.

Nothing is ever suspended by definition and no instance is deleted or started. Every instance this tool suspends is
tagged with a marker process variable, so ``status`` and ``reactivate`` only touch what this tool suspended and a
suspension made by someone else is left alone. An append-only JSONL ledger records each step; the marker in Camunda
is the authority, the ledger is the audit trail.
"""

import csv
import hashlib
import io
import json
import logging
import os
import re
import time
import uuid
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Callable, Optional, Sequence

import requests

from request_api.services.paymentslabackfillservice import _clean, _to_int  # pylint: disable=protected-access

FEE_KEY = 'foi-fee-processing'
PAYMENT_WAIT_ACTIVITY = 'Gateway_1771ld6'
LIFECYCLE_KEYS = ('foi-request', 'foi-request-processing')
EMAIL_KEY = 'foi-email-processing'
OPTIONAL_KEYS = LIFECYCLE_KEYS
DENIED_KEYS = (EMAIL_KEY, 'cache_refresh', 'due_reminder_notifications', 'foi-rawrequest-api-manager')
DENIED_REASON = {
    EMAIL_KEY: 'short-lived and calls APIs: wait until none are in flight instead of suspending it',
    'cache_refresh': 'no n8n schedule replaces it yet; it is stopped by a separate explicit step',
    'due_reminder_notifications': 'no n8n schedule replaces it yet; it is stopped by a separate explicit step',
    'foi-rawrequest-api-manager': 'it stores wfinstanceid and must stay active',
}
REACTIVATION_ORDER = LIFECYCLE_KEYS + (FEE_KEY,)  # raw request, then its child, then the payments

MARKER_VARIABLE = 'foiMigrationSuspension'
MARKER_VERSION = 1
VARIABLE_PATH = '/process-instance/%s/variables/%s'
GONE_DETAIL = 'the instance no longer exists'
CONCURRENT_RUN_WINDOW = timedelta(minutes=5)

# Connection handling: one token is reused for TOKEN_TTL_SECONDS, every call is retried on a network failure, and a
# run stops after MAX_CONSECUTIVE_FAILURES instances in a row failed (Keycloak or Camunda is down: do not wait for
# a timeout on every remaining instance).
TOKEN_TTL_SECONDS = 120
TOKEN_TIMEOUT_SECONDS = 30
RETRY_ATTEMPTS = 3
RETRY_PAUSE_SECONDS = 2.0
RETRY_STATUSES = (502, 503, 504)
MAX_CONSECUTIVE_FAILURES = 3

# Only these variables are requested. The instances also hold credentials and tokens.
FEE_VARIABLES = ('ministryRequestID', 'foiRequestID', 'fileNumber', 'formId', 'submissionId', 'paymentstatus',
                 'expirycounter', 'axisRequestId', 'isofflinepayment')
LIFECYCLE_VARIABLES = ('foiRequestID', 'rawRequestID', 'id', 'status')

# n8n payment rows that mean "n8n owns this payment" (it created or closed the row)
N8N_OWNED_STATUSES = ('ACTIVE', 'EXPIRED', 'PAID', 'CANCELLED', 'PAID_PENDING_SIDE_EFFECTS',
                      'CANCEL_PENDING_SIDE_EFFECTS')
BACKFILL_COMMENT = 'BACKFILL(camunda)'

# Outcomes
SUSPEND = 'suspend'
ALREADY_HELD = 'already_held'
SKIPPED = 'skipped'
REVIEW = 'manual_review'
ERROR = 'error'
REACTIVATE = 'reactivate'
CLEAR_MARKER = 'clear_stray_marker'
BLOCKED = 'blocked'
MANUAL_REVIEW = (REVIEW, ERROR, BLOCKED)

CSV_COLUMNS = ('process_instance_id', 'definition_key', 'definition_version', 'ministry_request_id',
               'foi_request_id', 'file_number', 'suspended', 'marker_run', 'outcome', 'reason', 'detail',
               'n8n_row_status')
PLAN_HASH = re.compile(r'^[0-9a-f]{16}$')


class SuspensionSourceError(Exception):
    """Camunda or n8n failed. The run is aborted instead of guessing; a rerun is safe."""


class PlanChangedError(Exception):
    """The instances an apply would change differ from the plan the operator reviewed. Nothing was changed."""

    def __init__(self, expected, report):
        super().__init__('The plan changed since it was reviewed: expected %s, now %s'
                         % (expected, report['run']['plan_hash']))
        self.expected, self.report = expected, report


class PlanTooLargeError(Exception):
    """The plan has more instances than --max-instances. Nothing was changed."""

    def __init__(self, size, limit, report):
        super().__init__('The plan has %d instances, more than --max-instances %d' % (size, limit))
        self.report = report


# --------------------------------------------------------------------------------------------------------------
# Camunda REST client
# --------------------------------------------------------------------------------------------------------------

class CamundaClient:
    """The few Camunda REST calls this tool needs. Credentials come from the same BPM_* environment as the API."""

    def __init__(self, base_url=None, token_provider=None, session=None, page_size=500, timeout=60,
                 retries=RETRY_ATTEMPTS, retry_pause=RETRY_PAUSE_SECONDS, sleep=time.sleep, clock=time.monotonic):
        self.base_url = (base_url or os.getenv('BPM_ENGINE_REST_URL') or '').rstrip('/')
        self._token_provider = token_provider
        self.session = session or requests.Session()
        self.page_size = page_size
        self.timeout = timeout
        self.retries, self.retry_pause = max(1, retries), retry_pause
        self._sleep, self._clock = sleep, clock
        self._token, self._token_at = None, None

    @staticmethod
    def _fetch_token():
        """One client-credentials token from the BPM_* settings the API uses, with a timeout (the API's own helper has none).

        A network failure is raised as is (``requests.RequestException``) so the caller can retry it.
        """
        from request_api.services.external.camundaservice import camundaservice  # pylint: disable=import-outside-toplevel
        settings = camundaservice()
        if not settings.bpmtokenurl:
            raise SuspensionSourceError('BPM_TOKEN_URL is not set')
        response = requests.post(settings.bpmtokenurl, auth=(settings.bpmclientid, settings.bpmclientsecret),
                                 headers={'Content-Type': 'application/x-www-form-urlencoded'},
                                 data='grant_type=client_credentials', timeout=TOKEN_TIMEOUT_SECONDS)
        token = response.json().get('access_token') if response.ok else None
        if not token:
            raise SuspensionSourceError('The token endpoint answered HTTP %s without an access token' % response.status_code)
        return token

    def _bearer(self):
        """The cached token, fetched again after TOKEN_TTL_SECONDS (the old code asked Keycloak on every call)."""
        now = self._clock()
        if self._token is None or now - self._token_at >= TOKEN_TTL_SECONDS:
            self._token = (self._token_provider or self._fetch_token)()
            self._token_at = now
        return self._token

    def _headers(self):
        return {'Authorization': 'Bearer ' + self._bearer(), 'Content-Type': 'application/json'}

    def _call(self, method, path, body=None, params=None, ok=(), what=None):
        """One REST call. Every call here is idempotent, so a network failure or a 502/503/504 is retried a few
        times, and a 401 gets one fresh token. Other failures are raised as ``SuspensionSourceError``."""
        if not self.base_url:
            raise SuspensionSourceError('BPM_ENGINE_REST_URL is not set')
        what = what or path
        response = self._send(method, path, body, params, what)
        if response.status_code in ok:
            return None
        if not response.ok:
            raise SuspensionSourceError('Camunda %s %s answered HTTP %s' % (method, what, response.status_code))
        return response.json() if response.content else None

    def _send(self, method, path, body, params, what):
        """The response of the first attempt that is worth keeping, retrying as ``_call`` describes."""
        refreshed, response = False, None
        for attempt in range(1, self.retries + 1):
            response = self._attempt(method, path, body, params, what, attempt)
            if response is None:  # a network failure with attempts left
                continue
            if response.status_code == 401 and not refreshed:
                refreshed, self._token = True, None  # an expired token: get a new one and repeat the call once
            elif response.status_code in RETRY_STATUSES and attempt < self.retries:
                self._sleep(self.retry_pause * attempt)
            else:
                break
        return response

    def _attempt(self, method, path, body, params, what, attempt):
        """One request. ``None`` after a network failure that will be retried; raises after the last one."""
        try:
            return self.session.request(method, self.base_url + path, params=params, timeout=self.timeout,
                                        data=None if body is None else json.dumps(body), headers=self._headers())
        except requests.RequestException as exc:
            self._token = None  # the failure may have been the token call itself
            if attempt >= self.retries:
                raise SuspensionSourceError('Camunda %s %s failed after %d attempts: %s'
                                            % (method, what, attempt, type(exc).__name__)) from exc
            logging.warning('camunda suspension: %s %s failed (%s), retrying', method, what, type(exc).__name__)
            self._sleep(self.retry_pause * attempt)
            return None

    def _paged(self, method, path, body=None):
        items, first = [], 0
        while True:
            page = self._call(method, path, body, {'firstResult': first, 'maxResults': self.page_size}) or []
            items.extend(page)
            if len(page) < self.page_size:
                return items
            first += self.page_size

    def instances(self, definition_key):
        """Every instance of the definition, active or suspended, as ``[{id, suspended, definitionId}]``."""
        return self._paged('POST', '/process-instance', {
            'processDefinitionKey': definition_key, 'sorting': [{'sortBy': 'instanceId', 'sortOrder': 'asc'}]})

    def instances_by_id(self, ids):
        found = []
        ids = list(ids)
        for start in range(0, len(ids), 100):
            found.extend(self._call('POST', '/process-instance', {'processInstanceIds': ids[start:start + 100]}) or [])
        return found

    def waiting_ids(self, definition_key, activity_id):
        """Instances with an execution at the activity."""
        return {e['processInstanceId'] for e in self._paged('POST', '/execution', {
            'processDefinitionKey': definition_key, 'activityId': activity_id,
            'sorting': [{'sortBy': 'instanceId', 'sortOrder': 'asc'}]})}

    def variables(self, ids, names):
        """``{instance id: {name: value}}`` for the whitelisted names, values as stored (not deserialised)."""
        ids = list(ids)
        out = {i: {} for i in ids}
        for start in range(0, len(ids), 50):
            chunk = ids[start:start + 50]
            for var in self._call('POST', '/variable-instance', {'processInstanceIdIn': chunk,
                                                                 'variableNameIn': list(names)},
                                  {'deserializeValues': 'false'}) or []:
                slot = out.setdefault(var['processInstanceId'], {})
                if var['name'] not in slot or var.get('executionId') == var.get('processInstanceId'):
                    slot[var['name']] = var.get('value')
        return out

    def open_incident_instances(self):
        """The ids of instances with an open incident."""
        return {i['processInstanceId'] for i in self._paged('GET', '/incident') if i.get('processInstanceId')}

    def marker_holders(self):
        """``{instance id: marker text}`` for every instance carrying the marker variable."""
        found = self._call('POST', '/variable-instance', {'variableName': MARKER_VARIABLE},
                           {'deserializeValues': 'false', 'maxResults': 100000}) or []
        return {v['processInstanceId']: v.get('value') for v in found}

    def instance(self, instance_id):
        """One instance, or ``None`` when it no longer exists."""
        found = self.instances_by_id([instance_id])
        return found[0] if found else None

    def marker(self, instance_id):
        text = self._call('GET', VARIABLE_PATH % (instance_id, MARKER_VARIABLE),
                          params={'deserializeValue': 'false'}, ok=(404,), what='read marker')
        return None if text is None else text.get('value')

    def set_marker(self, instance_id, text):
        self._call('PUT', VARIABLE_PATH % (instance_id, MARKER_VARIABLE), {'value': text, 'type': 'String'},
                   what='set marker')

    def delete_marker(self, instance_id):
        self._call('DELETE', VARIABLE_PATH % (instance_id, MARKER_VARIABLE), ok=(404,), what='delete marker')

    def set_suspended(self, instance_id, suspended):
        self._call('PUT', '/process-instance/%s/suspended' % instance_id, {'suspended': bool(suspended)},
                   what='suspend' if suspended else 'activate')


# --------------------------------------------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------------------------------------------

def parse_marker(text):
    """The marker as a dict, or ``{}`` when it is absent or not ours."""
    try:
        value = json.loads(text) if text else {}
    except (TypeError, ValueError):
        return {}
    return value if isinstance(value, dict) and 'run' in value else {}


def definition_version(definition_id):
    parts = _clean(definition_id).split(':')
    return _to_int(parts[1]) if len(parts) >= 2 else None


def _ids(variables):
    """``(ministry_request_id, form_id, submission_id)`` of a fee instance, ids lower-cased."""
    return (_to_int(variables.get('ministryRequestID')), _clean(variables.get('formId')).lower(),
            _clean(variables.get('submissionId')).lower())


def _same_payment(row, form_id, submission_id):
    return (_clean(row.get('form_id')).lower(), _clean(row.get('submission_id')).lower()) == (form_id, submission_id)


class Ledger:
    """Append-only JSONL audit file, flushed per line. Not the authority: Camunda's marker is."""

    def __init__(self, directory, run_id, command, enabled=True):
        self.path = None
        self._handle = None
        if enabled:
            os.makedirs(directory or '.', exist_ok=True)
            self.path = os.path.join(directory or '.', 'camunda_suspension_ledger_%s_%s.jsonl' % (command, run_id))

    def write(self, event, **fields):
        if self.path is None:
            return
        if self._handle is None:
            self._handle = open(self.path, 'a', encoding='utf-8')  # pylint: disable=consider-using-with
        self._handle.write(json.dumps(dict(event=event, at=datetime.now(timezone.utc).isoformat(), **fields)) + '\n')
        self._handle.flush()

    def close(self):
        if self._handle is not None:
            self._handle.close()
            self._handle = None


# --------------------------------------------------------------------------------------------------------------
# The tool
# --------------------------------------------------------------------------------------------------------------

@dataclass
class SuspensionOptions:
    """The settings of one run. All are optional; the defaults are a dry run of the fee instances."""

    definitions: Optional[Sequence[str]] = None  # optional lifecycle definitions to add to the fee instances
    ministry_request_ids: Optional[Sequence[int]] = None
    process_instance_ids: Optional[Sequence[str]] = None
    apply: bool = False
    confirm_plan: Optional[str] = None
    reason: Optional[str] = None
    max_instances: Optional[int] = None
    allow_no_n8n_row: bool = False
    n8n_check: bool = True
    only_run_id: Optional[str] = None
    run_id: Optional[str] = None
    operator: Optional[str] = None
    clock: Optional[Callable] = None
    ledger: Optional[Ledger] = None
    pace_seconds: float = 0.0
    sleep: Callable = time.sleep
    command: Optional[str] = None
    max_consecutive_failures: int = MAX_CONSECUTIVE_FAILURES


class CamundaSuspension:
    """Plans, and optionally performs, a suspension or reactivation. A dry run (``apply=False``) writes nothing."""

    def __init__(self, camunda, store_factory=None, **settings):
        """``settings`` are the fields of ``SuspensionOptions``; an unknown one raises ``TypeError``."""
        options = SuspensionOptions(**settings)
        self.camunda = camunda
        self.command = options.command
        self.max_consecutive_failures, self.aborted = options.max_consecutive_failures, False
        self._store_factory, self._store, self._rows = store_factory, None, None
        self.definitions = self._selected_definitions(options.definitions)
        self.only_requests = set(options.ministry_request_ids or [])
        self.only_instances = set(options.process_instance_ids or [])
        self.apply, self.confirm_plan, self.reason = options.apply, options.confirm_plan, _clean(options.reason)
        self.max_instances, self.n8n_check = options.max_instances, options.n8n_check
        self.allow_no_n8n_row, self.only_run_id = options.allow_no_n8n_row, options.only_run_id
        self.run_id = options.run_id or uuid.uuid4().hex[:12]
        self.operator = options.operator or os.getenv('USERNAME') or os.getenv('USER') or 'unknown'
        self.clock = options.clock or (lambda: datetime.now(timezone.utc))
        self.ledger = options.ledger or Ledger(None, self.run_id, 'run', enabled=False)
        self.pace_seconds, self._sleep = options.pace_seconds, options.sleep

    @staticmethod
    def _selected_definitions(optional):
        keys = list(optional or [])
        for key in keys:
            if key not in OPTIONAL_KEYS:
                raise ValueError('%s cannot be selected: %s' % (key, DENIED_REASON.get(key, 'not on the allow list')))
        return [FEE_KEY] + [k for k in LIFECYCLE_KEYS if k in keys]

    # -- n8n -------------------------------------------------------------------------------------------------

    def _n8n_rows(self):
        """Every ``payment-expiry`` row, grouped by ministry request id. Read once per run."""
        if self._rows is None:
            if self._store is None:
                self._store = self._store_factory()
            grouped = {}
            try:
                rows = self._store.list_rows()
            except requests.RequestException as exc:  # the n8n store does not wrap network errors
                raise SuspensionSourceError(
                    'n8n could not be reached (%s). Check N8N_BASE_URL is reachable from where the CLI runs '
                    '(host.docker.internal only works inside a container), or use --n8n-check skip'
                    % type(exc).__name__) from exc
            for row in rows:
                grouped.setdefault(_to_int(row.get('ministry_request_id')), []).append(row)
            self._rows = grouped
        return self._rows

    def _payment_rows(self, ministry_id, form_id, submission_id):
        return [r for r in self._n8n_rows().get(ministry_id, []) if _same_payment(r, form_id, submission_id)]

    # -- public: suspend and preview ---------------------------------------------------------------------------

    def suspend(self):
        """Plan the suspension and, when ``apply``, carry it out. Returns the report."""
        started = self.clock()
        records, email_in_flight = self._plan_suspend()
        plan_hash = self._plan_hash(records)
        planned = [r for r in records if r['outcome'] == SUSPEND]
        if self.apply:
            if self.confirm_plan is not None and _clean(self.confirm_plan).lower() != plan_hash:
                self.apply = False
                raise PlanChangedError(_clean(self.confirm_plan),
                                       self._report(self.command or 'suspend', records, started, plan_hash, email_in_flight))
            if self.max_instances is not None and len(planned) > self.max_instances:
                self.apply = False
                raise PlanTooLargeError(len(planned), self.max_instances,
                                        self._report(self.command or 'suspend', records, started, plan_hash, email_in_flight))
            self.ledger.write('plan', run=self.run_id, plan_hash=plan_hash, operator=self.operator, reason=self.reason,
                              instances=[r['process_instance_id'] for r in planned])
            self._apply_each(planned, self._suspend_one)
        return self._report(self.command or 'suspend', records, started, plan_hash, email_in_flight)

    def _apply_each(self, planned, action):
        """Apply ``action`` to each planned record. After ``max_consecutive_failures`` failures in a row the run
        stops (Camunda or Keycloak is down: waiting for a timeout on every remaining instance helps nobody) and the
        rest are recorded as not attempted. A rerun picks them up."""
        failures = 0
        for index, record in enumerate(planned):
            action(record)
            failures = failures + 1 if record['outcome'] == ERROR else 0
            if self.max_consecutive_failures and failures >= self.max_consecutive_failures:
                rest = planned[index + 1:]
                for pending in rest:
                    self._mark(pending, ERROR, 'not_attempted_run_aborted',
                               'stopped after %d failures in a row: fix the cause, then rerun' % failures)
                self.aborted = True
                self.ledger.write('aborted', after=index + 1, not_attempted=len(rest))
                return
            if self.pace_seconds:
                self._sleep(self.pace_seconds)

    def _plan_suspend(self):
        """``(records, number of email instances in flight)``."""
        held = self.camunda.marker_holders()
        records = []
        for key in self.definitions:
            records.extend(self._plan_definition(key, held))
        email = self._plan_email()
        return records + email, len(email)

    def _plan_definition(self, key, held):
        instances = self.camunda.instances(key)
        if not instances:
            return []
        is_fee = key == FEE_KEY
        variables = self.camunda.variables([i['id'] for i in instances],
                                           FEE_VARIABLES if is_fee else LIFECYCLE_VARIABLES)
        waiting = self.camunda.waiting_ids(key, PAYMENT_WAIT_ACTIVITY) if is_fee else set()
        incidents = self.camunda.open_incident_instances() if is_fee else set()
        records = []
        for instance in instances:
            record = self._record(key, instance, variables.get(instance['id'], {}), held.get(instance['id']))
            if is_fee:
                self._classify_fee(record, instance['id'] in waiting, incidents)
            else:
                self._classify_lifecycle(record)
            records.append(record)
        return records

    def _plan_email(self):
        """The email instances in flight: reported, never suspended."""
        records = []
        for instance in self.camunda.instances(EMAIL_KEY):
            record = self._record(EMAIL_KEY, instance, {}, None)
            self._mark(record, SKIPPED, 'email_in_flight_wait_for_drain', DENIED_REASON[EMAIL_KEY])
            records.append(record)
        return records

    def _record(self, key, instance, variables, marker_text):
        marker = parse_marker(marker_text)
        return {
            'process_instance_id': instance['id'], 'definition_key': key,
            'definition_version': definition_version(instance.get('definitionId')),
            'ministry_request_id': _to_int(variables.get('ministryRequestID')),
            'foi_request_id': _to_int(variables.get('foiRequestID')) or _to_int(variables.get('id')),
            'file_number': _clean(variables.get('fileNumber')) or None,
            'suspended': bool(instance.get('suspended')), 'marker_run': marker.get('run'),
            'outcome': None, 'reason': None, 'detail': None, 'n8n_row_status': None,
            '_vars': variables, '_marker': marker,
        }

    @staticmethod
    def _mark(record, outcome, reason, detail=None):
        record['outcome'], record['reason'], record['detail'] = outcome, reason, detail

    def _scope_check(self, record):
        if self.only_instances and record['process_instance_id'] not in self.only_instances:
            return 'outside_requested_scope'
        if self.only_requests and record['ministry_request_id'] not in self.only_requests:
            return 'outside_requested_scope'
        return None

    def _state_check(self, record):
        """Common checks on the current state. Returns True when the record is settled (outcome set)."""
        marker = record['_marker']
        if record['suspended']:
            if marker:
                self._mark(record, ALREADY_HELD, 'suspended_by_this_tool', 'run %s' % marker.get('run'))
            else:
                self._mark(record, SKIPPED, 'suspended_by_someone_else', 'no marker: never touched by this tool')
            return True
        if marker and marker.get('run') != self.run_id and self._recent(marker):
            self._mark(record, SKIPPED, 'claimed_by_other_run', 'run %s tagged it moments ago' % marker.get('run'))
            return True
        return False

    def _recent(self, marker):
        try:
            tagged = datetime.fromisoformat(str(marker.get('at')).replace('Z', '+00:00'))
        except ValueError:
            return False
        return self.clock() - tagged < CONCURRENT_RUN_WINDOW

    def _classify_lifecycle(self, record):
        scope = self._scope_check(record)
        if scope:
            return self._mark(record, SKIPPED, scope)
        if self._state_check(record):
            return None
        return self._mark(record, SUSPEND, 'resume_interrupted_run' if record['_marker'] else 'lifecycle_inert',
                          'does nothing on its own' if not record['_marker'] else 'tagged earlier, not yet suspended')

    def _classify_fee(self, record, waiting, incidents):
        scope = self._scope_check(record)
        if scope:
            return self._mark(record, SKIPPED, scope)
        if self._state_check(record):
            return None
        if not waiting:
            return self._mark(record, SKIPPED, 'not_waiting_at_payment_gateway', 'mid-retry or mid-creation: left alone')
        if record['process_instance_id'] in incidents:
            return self._mark(record, REVIEW, 'open_incident', 'resolve the incident, then rerun')
        resumed = bool(record['_marker'])
        if not self.n8n_check:
            return self._mark(record, SUSPEND, 'n8n_check_skipped' if not resumed else 'resume_interrupted_run',
                              'the operator skipped the n8n ownership check')
        return self._classify_fee_owner(record, resumed)

    def _classify_fee_owner(self, record, resumed):
        ministry_id, form_id, submission_id = _ids(record['_vars'])
        if ministry_id is None or not form_id or not submission_id:
            return self._mark(record, REVIEW, 'missing_ministry_request_or_form_ids')
        rows = self._payment_rows(ministry_id, form_id, submission_id)
        if not rows:
            if self.allow_no_n8n_row:
                return self._mark(record, SUSPEND, 'no_n8n_row_allowed', 'n8n has no row; suspended on request')
            return self._mark(record, SKIPPED, 'no_n8n_row', 'n8n does not own this payment; use --allow-no-n8n-row to suspend it')
        statuses = sorted({_clean(r.get('sla_status')) for r in rows})
        record['n8n_row_status'] = ','.join(statuses)
        if 'PENDING' in statuses:
            return self._mark(record, REVIEW, 'n8n_row_pending', 'initiation interrupted: decide by hand')
        if not any(s in N8N_OWNED_STATUSES for s in statuses):
            return self._mark(record, REVIEW, 'unexpected_n8n_row_status', record['n8n_row_status'])
        return self._mark(record, SUSPEND, 'resume_interrupted_run' if resumed else 'n8n_owns_payment',
                          'n8n row %s' % record['n8n_row_status'])

    @staticmethod
    def _plan_hash(records, outcomes=(SUSPEND,)):
        """A fingerprint of the instances a run would change, so an apply is tied to the plan that was reviewed."""
        planned = sorted((str(r['definition_key']), r['process_instance_id']) for r in records if r['outcome'] in outcomes)
        return hashlib.sha256(json.dumps(planned).encode('utf-8')).hexdigest()[:16]

    def _marker_text(self):
        return json.dumps({'run': self.run_id, 'at': self.clock().isoformat(), 'by': self.operator,
                           'reason': self.reason, 'v': MARKER_VERSION}, sort_keys=True)

    def _suspend_one(self, record):
        """Tag, suspend, read back. A failure is recorded and the run continues; a rerun picks the instance up again."""
        instance_id = record['process_instance_id']
        tagged_here = False
        try:
            self.ledger.write('intent', instance=instance_id, definition=record['definition_key'])
            current = self.camunda.instance(instance_id)
            if current is None:
                self._mark(record, SKIPPED, 'gone_before_suspension', 'completed or deleted meanwhile')
                return
            if current.get('suspended'):
                self._mark(record, SKIPPED, 'suspended_meanwhile', 'someone suspended it after the plan was made')
                return
            existing = parse_marker(self.camunda.marker(instance_id))
            if existing and existing.get('run') != self.run_id and self._recent(existing):
                self._mark(record, SKIPPED, 'claimed_by_other_run', 'run %s' % existing.get('run'))
                return
            self.camunda.set_marker(instance_id, self._marker_text())
            tagged_here = True
            self.ledger.write('tagged', instance=instance_id)
            self.camunda.set_suspended(instance_id, True)
            after = self.camunda.instance(instance_id)
            if after is None or not after.get('suspended'):
                raise SuspensionSourceError('read back: the instance is not suspended')
            record['suspended'], record['marker_run'] = True, self.run_id
            self.ledger.write('suspended', instance=instance_id)
        except Exception as exc:  # pylint: disable=broad-except
            logging.exception('camunda suspension: failed for instance %s: %s', instance_id, type(exc).__name__)
            self.ledger.write('failed', instance=instance_id, error=type(exc).__name__)
            if tagged_here:
                self._try_untag(instance_id)
            self._mark(record, ERROR, 'suspend_failed', '%s: %s' % (type(exc).__name__, exc))

    def _try_untag(self, instance_id):
        try:
            self.camunda.delete_marker(instance_id)
        except Exception:  # pylint: disable=broad-except
            logging.error('camunda suspension: could not remove the marker of %s', instance_id)

    # -- public: status --------------------------------------------------------------------------------------------

    def status(self):
        """What this tool holds suspended right now. Read only."""
        started = self.clock()
        holders = self.camunda.marker_holders()
        found = {i['id']: i for i in self.camunda.instances_by_id(list(holders))}
        records = []
        for instance_id, text in sorted(holders.items()):
            marker = parse_marker(text)
            if self.only_run_id and marker.get('run') != self.only_run_id:
                continue
            instance = found.get(instance_id)
            record = self._record(self._key_of(instance), instance or {'id': instance_id}, {}, text)
            record['process_instance_id'] = instance_id
            if instance is None:
                self._mark(record, SKIPPED, 'gone', GONE_DETAIL)
            elif instance.get('suspended'):
                self._mark(record, ALREADY_HELD, 'suspended_by_this_tool', 'run %s by %s' % (marker.get('run'), marker.get('by')))
            else:
                self._mark(record, REVIEW, 'marker_on_active_instance', 'interrupted after tagging: suspend resumes it, reactivate clears it')
            records.append(record)
        return self._report(self.command or 'status', records, started, self._plan_hash(records, (ALREADY_HELD,)), 0)

    @staticmethod
    def _key_of(instance):
        parts = _clean((instance or {}).get('definitionId')).split(':')
        return parts[0] if parts and parts[0] else None

    # -- public: reactivate ------------------------------------------------------------------------------------------

    def reactivate(self):
        """Plan the reactivation of what this tool suspended and, when ``apply``, carry it out."""
        started = self.clock()
        records = self._plan_reactivate()
        plan_hash = self._plan_hash(records, (REACTIVATE, CLEAR_MARKER))
        planned = [r for r in records if r['outcome'] in (REACTIVATE, CLEAR_MARKER)]
        if self.apply:
            if self.confirm_plan is not None and _clean(self.confirm_plan).lower() != plan_hash:
                self.apply = False
                raise PlanChangedError(_clean(self.confirm_plan), self._report(self.command or 'reactivate', records, started, plan_hash, 0))
            self.ledger.write('plan', run=self.run_id, plan_hash=plan_hash, operator=self.operator,
                              instances=[r['process_instance_id'] for r in planned])
            self._apply_each(planned, self._reactivate_one)
        return self._report(self.command or 'reactivate', records, started, plan_hash, 0)

    def _plan_reactivate(self):
        holders = self.camunda.marker_holders()
        found = {i['id']: i for i in self.camunda.instances_by_id(list(holders))}
        keys = {i: self._key_of(found.get(i)) for i in holders}
        fee_ids = [i for i in holders if keys[i] == FEE_KEY and i in found]
        variables = self.camunda.variables(fee_ids, FEE_VARIABLES) if fee_ids else {}
        records = []
        for instance_id, text in holders.items():
            marker = parse_marker(text)
            if self.only_run_id and marker.get('run') != self.only_run_id:
                continue
            instance = found.get(instance_id)
            record = self._record(keys[instance_id], instance or {'id': instance_id}, variables.get(instance_id, {}), text)
            record['process_instance_id'] = instance_id
            self._classify_marked(record, instance)
            records.append(record)
        order = {k: n for n, k in enumerate(REACTIVATION_ORDER)}
        records.sort(key=lambda r: (order.get(r['definition_key'], 99), r['process_instance_id']))
        return records

    def _classify_marked(self, record, instance):
        """What ``reactivate`` does with one instance that carries a marker."""
        if not record['_marker']:
            return self._mark(record, SKIPPED, 'marker_not_ours', 'the variable is not a valid marker: never touched')
        scope = self._scope_check(record)
        if scope:
            return self._mark(record, SKIPPED, scope)
        if instance is None:
            return self._mark(record, SKIPPED, 'gone', GONE_DETAIL)
        if not instance.get('suspended'):
            return self._mark(record, CLEAR_MARKER, 'stale_marker_on_active_instance', 'no activate call')
        is_fee = record['definition_key'] == FEE_KEY
        if is_fee and self.n8n_check:
            return self._classify_reactivation(record)
        return self._mark(record, REACTIVATE, 'n8n_check_skipped' if is_fee else 'lifecycle')

    def _classify_reactivation(self, record):
        ministry_id, form_id, submission_id = _ids(record['_vars'])
        if ministry_id is None or not form_id or not submission_id:
            return self._mark(record, BLOCKED, 'missing_ministry_request_or_form_ids', 'use --n8n-check skip if n8n is unreachable')
        rows = self._payment_rows(ministry_id, form_id, submission_id)
        if not rows:
            return self._mark(record, REACTIVATE, 'no_n8n_row', 'n8n never owned this payment')
        record['n8n_row_status'] = ','.join(sorted({_clean(r.get('sla_status')) for r in rows}))
        verdicts = [self._row_verdict(r) for r in rows]
        if all(v == 'untouched' for v in verdicts):
            return self._mark(record, REACTIVATE, 'n8n_row_untouched_backfill',
                              'close the n8n row (rollback marker) once reactivated, so n8n cannot act on it')
        statuses = record['n8n_row_status']
        if any(s in statuses for s in ('PAID', 'CANCELLED')):  # also matches the *_PENDING_SIDE_EFFECTS values
            return self._mark(record, BLOCKED, 'n8n_owns_payment',
                              'closed in n8n (%s): delete the instance instead of reactivating it' % statuses)
        if 'EXPIRED' in statuses:
            return self._mark(record, BLOCKED, 'expired_by_n8n',
                              'n8n expired it: set expirycounter=1 and paymentstatus=NA before reactivating')
        return self._mark(record, BLOCKED, 'n8n_owns_payment', 'row %s: review by hand' % statuses)

    @staticmethod
    def _row_verdict(row):
        """``untouched`` for a row written by the backfill that n8n has not acted on since."""
        status = _clean(row.get('sla_status'))
        if status not in ('ACTIVE', 'EXPIRED'):
            return 'changed'
        if not _clean(row.get('comments')).startswith(BACKFILL_COMMENT):
            return 'changed'  # started or closed by n8n itself
        if _clean(row.get('started_execution_id')) or _clean(row.get('completed_execution_id')):
            return 'changed'
        return 'untouched'

    def _reactivate_one(self, record):
        instance_id = record['process_instance_id']
        activated = False
        try:
            self.ledger.write('reactivate_intent', instance=instance_id, outcome=record['outcome'])
            current = self.camunda.instance(instance_id)
            if current is None:
                self._mark(record, SKIPPED, 'gone', GONE_DETAIL)
                return
            if record['outcome'] == REACTIVATE:
                if current.get('suspended'):
                    self.camunda.set_suspended(instance_id, False)
                    after = self.camunda.instance(instance_id)
                    if after is None or after.get('suspended'):
                        raise SuspensionSourceError('read back: the instance is still suspended')
                record['suspended'] = False
                activated = True
            self.camunda.delete_marker(instance_id)
            self.ledger.write('reactivated', instance=instance_id, outcome=record['outcome'])
        except Exception as exc:  # pylint: disable=broad-except
            logging.exception('camunda suspension: reactivation failed for %s: %s', instance_id, type(exc).__name__)
            self.ledger.write('failed', instance=instance_id, error=type(exc).__name__, activated=activated)
            if activated:  # the instance is active again; only the marker is left, and a rerun clears it
                self._mark(record, ERROR, 'marker_not_removed_after_activation',
                           'the instance is ACTIVE; rerun reactivate to clear its marker (%s: %s)' % (type(exc).__name__, exc))
            else:
                self._mark(record, ERROR, 'reactivate_failed', '%s: %s' % (type(exc).__name__, exc))

    # -- reporting ---------------------------------------------------------------------------------------------------

    def _summary(self, command, records, by_outcome, email_in_flight):
        by_definition = Counter(str(r['definition_key']) for r in records)
        summary = {'instances_examined': len(records)}
        summary.update({'instances_' + k.replace('-', '_'): v for k, v in sorted(by_definition.items())})
        if command in ('suspend', 'preview'):
            summary['suspended' if self.apply else 'would_suspend'] = by_outcome[SUSPEND]
            summary['already_suspended_by_this_tool'] = by_outcome[ALREADY_HELD]
            summary['skipped'] = by_outcome[SKIPPED]
            summary['email_instances_in_flight'] = email_in_flight
        elif command == 'reactivate':
            summary['reactivated' if self.apply else 'would_reactivate'] = by_outcome[REACTIVATE]
            summary['stray_markers_cleared' if self.apply else 'stray_markers_to_clear'] = by_outcome[CLEAR_MARKER]
            summary['blocked'] = by_outcome[BLOCKED]
            summary['skipped'] = by_outcome[SKIPPED]
        else:
            summary['held_suspended_by_this_tool'] = by_outcome[ALREADY_HELD]
        summary['manual_review_required'] = sum(by_outcome[outcome] for outcome in MANUAL_REVIEW)
        summary['errors'] = by_outcome[ERROR]
        return summary

    def _report(self, command, records, started, plan_hash, email_in_flight):
        by_outcome = Counter(r['outcome'] for r in records)
        by_reason = Counter('%s/%s' % (r['outcome'], r['reason']) for r in records)
        summary = self._summary(command, records, by_outcome, email_in_flight)
        applied = self.apply
        for record in records:  # internal fields never leave this object
            for key in [k for k in record if k.startswith('_')]:
                del record[key]
        return {
            'run': {'id': self.run_id, 'command': command, 'mode': 'apply' if applied else 'dry-run',
                    'operator': self.operator, 'reason': self.reason or None, 'definitions': self.definitions,
                    'plan_hash': plan_hash, 'aborted': self.aborted, 'ledger': self.ledger.path, 'started_at': started.isoformat(),
                    'finished_at': self.clock().isoformat()},
            'summary': summary,
            'by_outcome_and_reason': dict(sorted(by_reason.items())),
            'manual_review_required': summary['manual_review_required'],
            'records': records,
        }


def report_csv_text(report, bom=True):
    """The per-record results as CSV text. The BOM makes Excel read it as UTF-8."""
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=CSV_COLUMNS, extrasaction='ignore', lineterminator='\r\n')
    writer.writeheader()
    writer.writerows(report['records'])
    return ('﻿' if bom else '') + out.getvalue()


def format_summary(report):
    """Plain text for the console. Counts and references only; record detail is in the report file."""
    run, summary = report['run'], report['summary']
    lines = ['Camunda suspension  command=%s  run=%s  mode=%s  definitions=%s' % (
        run['command'], run['id'], run['mode'].upper(), ','.join(run['definitions']))]
    if run['command'] in ('suspend', 'preview', 'reactivate'):
        hint = ''
        if run['mode'] == 'dry-run' and run['command'] != 'preview':
            hint = '  (review the report, then --apply --confirm-plan %s)' % run['plan_hash']
        lines.append('Plan hash: %s%s' % (run['plan_hash'], hint))
    lines += ['  %-48s %s' % (key, value) for key, value in summary.items()]
    lines.append('Outcome / reason')
    lines += ['  %-72s %s' % (key, value) for key, value in report['by_outcome_and_reason'].items()]
    review = [r for r in report['records'] if r['outcome'] in MANUAL_REVIEW]
    lines.append('Manual review required: %d' % len(review))
    for r in review:
        lines.append('  instance=%s %s ministry_request=%s file=%s  %s: %s%s' % (
            r['process_instance_id'], r['definition_key'], r['ministry_request_id'], r['file_number'], r['outcome'],
            r['reason'], ' (%s)' % r['detail'] if r['detail'] else ''))
    if run.get('aborted'):
        lines.append('RUN STOPPED EARLY after repeated failures: the instances not attempted are listed as '
                     'error/not_attempted_run_aborted. Fix the cause (network, Keycloak, Camunda), then rerun.')
    if run['ledger'] and run['mode'] == 'apply':
        lines.append('Ledger: %s' % run['ledger'])
    return '\n'.join(lines)
