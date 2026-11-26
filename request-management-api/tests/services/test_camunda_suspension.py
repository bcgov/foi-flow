"""Camunda suspension tool: suspend and reactivate instances for the Camunda to n8n migration.

Pure tests: Camunda and the n8n Data Table are replaced by in-memory fakes, so nothing here needs a database or a
network.
"""

import csv
import json
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest

import camunda_suspension_cli as cli
from request_api.services import camundasuspensionservice as svc
from request_api.services.camundasuspensionservice import (
    ALREADY_HELD, BLOCKED, CLEAR_MARKER, ERROR, MARKER_VARIABLE, REACTIVATE, REVIEW, SKIPPED, SUSPEND, CamundaClient,
    CamundaSuspension, Ledger, PlanChangedError, PlanTooLargeError, SuspensionSourceError, format_summary,
    parse_marker, report_csv_text)

NOW = datetime(2026, 11, 19, 15, 0, tzinfo=timezone.utc)
FORM = '638a2faabfddffe844de095d'
SUB = '6ae11636bfaa24f7903a8c3d'
SUB2 = '65666dd639a8bd03526d6adf'


def fee(pid='f1', ministry=100, sub=SUB, waiting=True, suspended=False, incident=False, marker=None, version=5, **vars_):
    variables = {'ministryRequestID': ministry, 'foiRequestID': 10, 'fileNumber': 'EDU-2030-%d' % ministry,
                 'formId': FORM, 'submissionId': sub, 'paymentstatus': 'NOT PAID', 'expirycounter': 0}
    variables.update(vars_)
    return {'id': pid, 'key': 'foi-fee-processing', 'version': version, 'suspended': suspended, 'waiting': waiting,
            'incident': incident, 'marker': marker, 'vars': variables}


def lifecycle(pid='r1', key='foi-request-processing', suspended=False, marker=None):
    return {'id': pid, 'key': key, 'version': 3, 'suspended': suspended, 'waiting': False, 'incident': False,
            'marker': marker, 'vars': {'foiRequestID': 10}}


def email(pid='e1'):
    return {'id': pid, 'key': 'foi-email-processing', 'version': 3, 'suspended': False, 'waiting': False,
            'incident': False, 'marker': None, 'vars': {}}


def marker_text(run='old-run', at=None, reason='CCP-5801'):
    return json.dumps({'run': run, 'at': (at or NOW - timedelta(days=1)).isoformat(), 'by': 'tester', 'reason': reason, 'v': 1})


class FakeCamunda:
    """The Camunda REST calls the tool makes, over an in-memory set of instances."""

    def __init__(self, *instances):
        self.items = {i['id']: i for i in instances}
        self.calls = []
        self.fail_suspend = set()
        self.fail_marker = set()
        self.silent_suspend = set()  # the call "works" but the instance does not end up suspended
        self.fail_delete_marker = set()

    @staticmethod
    def _dto(item):
        return {'id': item['id'], 'suspended': item['suspended'],
                'definitionId': '%s:%s:uuid' % (item['key'], item['version'])}

    def instances(self, key):
        return [self._dto(i) for i in self.items.values() if i['key'] == key]

    def instances_by_id(self, ids):
        return [self._dto(self.items[i]) for i in ids if i in self.items]

    def waiting_ids(self, key, activity):
        return {i['id'] for i in self.items.values() if i['key'] == key and i['waiting']}

    def variables(self, ids, names):
        return {i: {k: v for k, v in self.items[i]['vars'].items() if k in names} for i in ids if i in self.items}

    def open_incident_instances(self):
        return {i['id'] for i in self.items.values() if i['incident']}

    def marker_holders(self):
        return {i['id']: i['marker'] for i in self.items.values() if i['marker'] is not None}

    def instance(self, instance_id):
        found = self.instances_by_id([instance_id])
        return found[0] if found else None

    def marker(self, instance_id):
        return self.items[instance_id]['marker']

    def set_marker(self, instance_id, text):
        self.calls.append(('set_marker', instance_id))
        if instance_id in self.fail_marker:
            raise SuspensionSourceError('Camunda PUT set marker answered HTTP 500')
        self.items[instance_id]['marker'] = text

    def delete_marker(self, instance_id):
        self.calls.append(('delete_marker', instance_id))
        if instance_id in self.fail_delete_marker:
            raise SuspensionSourceError('Camunda DELETE delete marker failed after 3 attempts: ConnectTimeout')
        self.items[instance_id]['marker'] = None

    def set_suspended(self, instance_id, suspended):
        self.calls.append(('suspend' if suspended else 'activate', instance_id))
        if instance_id in self.fail_suspend:
            raise SuspensionSourceError('Camunda PUT suspend answered HTTP 500')
        if instance_id not in self.silent_suspend:
            self.items[instance_id]['suspended'] = bool(suspended)

    def writes(self):
        return [c for c in self.calls]


class FakeStore:
    def __init__(self, rows=None):
        self.rows = rows or []
        self.reads = 0

    def list_rows(self, ministry_request_id=None):
        self.reads += 1
        return [dict(r) for r in self.rows]


def sla(status='ACTIVE', ministry=100, sub=SUB, comments='BACKFILL(camunda) run r: instance f1, waiting for payment, expirycounter=0',
        **extra):
    row = {'id': 1, 'sla_type': 'payment-expiry', 'sla_status': status, 'ministry_request_id': str(ministry),
           'form_id': FORM, 'submission_id': sub, 'comments': comments}
    row.update(extra)
    return row


def tool(camunda, rows=None, **kwargs):
    store = kwargs.pop('store', None) or FakeStore(rows if rows is not None else [sla()])
    kwargs.setdefault('store_factory', lambda: store)
    kwargs.setdefault('run_id', 'test-run')
    kwargs.setdefault('operator', 'tester')
    kwargs.setdefault('clock', lambda: NOW)
    return CamundaSuspension(camunda, **kwargs), store


def only(report):
    assert len(report['records']) == 1
    return report['records'][0]


def by_id(report, pid):
    return [r for r in report['records'] if r['process_instance_id'] == pid][0]


# --- suspend: dry run and apply ----------------------------------------------------------------------------------

def test_dry_run_plans_the_suspension_and_changes_nothing():
    camunda = FakeCamunda(fee())
    report = tool(camunda)[0].suspend()
    record = only(report)
    assert (record['outcome'], record['reason']) == (SUSPEND, 'n8n_owns_payment')
    assert (record['definition_key'], record['definition_version'], record['ministry_request_id']) == (
        'foi-fee-processing', 5, 100)
    assert report['run']['mode'] == 'dry-run'
    assert report['summary']['would_suspend'] == 1
    assert 'suspended' not in report['summary']
    assert camunda.calls == []
    assert camunda.items['f1']['suspended'] is False
    assert camunda.items['f1']['marker'] is None


def test_apply_suspends_tags_and_records_a_ledger(tmp_path):
    camunda = FakeCamunda(fee())
    plan = tool(camunda)[0].suspend()['run']['plan_hash']
    job, _ = tool(camunda, apply=True, confirm_plan=plan, reason='CCP-5801',
                  ledger=Ledger(str(tmp_path), 'test-run', 'suspend'))
    report = job.suspend()
    job.ledger.close()
    assert report['summary']['suspended'] == 1
    assert camunda.items['f1']['suspended'] is True
    marker = parse_marker(camunda.items['f1']['marker'])
    assert (marker['run'], marker['by'], marker['reason'], marker['v']) == ('test-run', 'tester', 'CCP-5801', 1)
    events = [json.loads(line)['event'] for line in open(job.ledger.path, encoding='utf-8')]
    assert events == ['plan', 'intent', 'tagged', 'suspended']
    # the marker is set before the suspension, so a crash in between leaves a recoverable state
    assert [c[0] for c in camunda.calls] == ['set_marker', 'suspend']


def test_a_second_apply_changes_nothing():
    camunda = FakeCamunda(fee())
    for _ in range(2):
        plan = tool(camunda)[0].suspend()['run']['plan_hash']
        report = tool(camunda, apply=True, confirm_plan=plan, reason='x')[0].suspend()
    assert only(report)['outcome'] == ALREADY_HELD
    assert [c[0] for c in camunda.calls] == ['set_marker', 'suspend']  # only the first run wrote


def test_apply_with_a_stale_plan_hash_changes_nothing_and_returns_the_new_plan():
    camunda = FakeCamunda(fee())
    plan = tool(camunda)[0].suspend()['run']['plan_hash']
    camunda.items['f2'] = fee('f2', 101, SUB2)  # a new instance appeared after the review
    store = FakeStore([sla(), sla(ministry=101, sub=SUB2)])
    job, _ = tool(camunda, store=store, apply=True, confirm_plan=plan, reason='x')
    with pytest.raises(PlanChangedError) as raised:
        job.suspend()
    assert raised.value.report['run']['plan_hash'] != plan
    assert raised.value.report['run']['mode'] == 'dry-run'
    assert camunda.calls == []


def test_max_instances_refuses_a_larger_plan():
    camunda = FakeCamunda(fee('f1', 100), fee('f2', 101, SUB2))
    store = FakeStore([sla(), sla(ministry=101, sub=SUB2)])
    plan = tool(camunda, store=store)[0].suspend()['run']['plan_hash']
    job, _ = tool(camunda, store=store, apply=True, confirm_plan=plan, reason='x', max_instances=1)
    with pytest.raises(PlanTooLargeError):
        job.suspend()
    assert camunda.calls == []


# --- which fee instances are suspended -----------------------------------------------------------------------------

@pytest.mark.parametrize('instance, rows, reason', [
    (fee(waiting=False), None, 'not_waiting_at_payment_gateway'),
    (fee(suspended=True), None, 'suspended_by_someone_else'),
    (fee(), [], 'no_n8n_row'),
    (fee(), [sla(ministry=999)], 'no_n8n_row'),  # a row for another request is not this payment
    (fee(), [sla(sub=SUB2)], 'no_n8n_row'),      # nor a row for another submission
])
def test_excluded_instances_are_left_alone(instance, rows, reason):
    camunda = FakeCamunda(instance)
    report = tool(camunda, rows=rows)[0].suspend()
    assert (only(report)['outcome'], only(report)['reason']) == (SKIPPED, reason)
    plan = report['run']['plan_hash']
    tool(camunda, rows=rows, apply=True, confirm_plan=plan, reason='x')[0].suspend()
    assert camunda.calls == []


def test_open_incident_and_pending_row_go_to_manual_review():
    camunda = FakeCamunda(fee('f1', 100, incident=True), fee('f2', 101, SUB2))
    store = FakeStore([sla(), sla(status='PENDING', ministry=101, sub=SUB2)])
    report = tool(camunda, store=store)[0].suspend()
    assert (by_id(report, 'f1')['outcome'], by_id(report, 'f1')['reason']) == (REVIEW, 'open_incident')
    assert (by_id(report, 'f2')['outcome'], by_id(report, 'f2')['reason']) == (REVIEW, 'n8n_row_pending')
    assert report['manual_review_required'] == 2


@pytest.mark.parametrize('status', ['ACTIVE', 'EXPIRED', 'PAID', 'CANCELLED', 'PAID_PENDING_SIDE_EFFECTS',
                                    'CANCEL_PENDING_SIDE_EFFECTS'])
def test_every_n8n_owned_status_allows_the_suspension(status):
    report = tool(FakeCamunda(fee()), rows=[sla(status=status)])[0].suspend()
    assert (only(report)['outcome'], only(report)['n8n_row_status']) == (SUSPEND, status)


def test_allow_no_n8n_row_suspends_a_payment_the_backfill_skipped():
    camunda = FakeCamunda(fee())
    report = tool(camunda, rows=[], allow_no_n8n_row=True)[0].suspend()
    assert (only(report)['outcome'], only(report)['reason']) == (SUSPEND, 'no_n8n_row_allowed')


def test_an_unreachable_n8n_is_a_clean_source_error_with_a_hint():
    class Unreachable:
        def list_rows(self):
            raise svc.requests.ConnectTimeout('host.docker.internal timed out')
    suspending, _ = tool(FakeCamunda(fee()), store=Unreachable())
    with pytest.raises(SuspensionSourceError, match='N8N_BASE_URL.*--n8n-check skip'):
        suspending.suspend()
    reactivating, _ = tool(FakeCamunda(held()), store=Unreachable())
    with pytest.raises(SuspensionSourceError, match='could not be reached'):
        reactivating.reactivate()


def test_n8n_check_skip_never_reads_n8n():
    def boom():
        raise AssertionError('n8n must not be read')
    report = tool(FakeCamunda(fee()), store_factory=boom, n8n_check=False)[0].suspend()
    assert (only(report)['outcome'], only(report)['reason']) == (SUSPEND, 'n8n_check_skipped')


def test_scope_filters_limit_the_run_to_a_canary():
    camunda = FakeCamunda(fee('f1', 100), fee('f2', 101, SUB2))
    store = FakeStore([sla(), sla(ministry=101, sub=SUB2)])
    report = tool(camunda, store=store, ministry_request_ids=[101])[0].suspend()
    assert (by_id(report, 'f1')['reason'], by_id(report, 'f2')['outcome']) == ('outside_requested_scope', SUSPEND)
    report = tool(camunda, store=store, process_instance_ids=['f1'])[0].suspend()
    assert (by_id(report, 'f1')['outcome'], by_id(report, 'f2')['reason']) == (SUSPEND, 'outside_requested_scope')


# --- optional lifecycle instances, never-suspended definitions -----------------------------------------------------

def test_lifecycle_instances_are_only_included_when_asked_for():
    camunda = FakeCamunda(fee(), lifecycle('r1', 'foi-request'), lifecycle('r2', 'foi-request-processing'))
    assert {r['definition_key'] for r in tool(camunda)[0].suspend()['records']} == {'foi-fee-processing'}
    report = tool(camunda, definitions=['foi-request-processing'])[0].suspend()
    assert by_id(report, 'r2')['outcome'] == SUSPEND
    assert 'r1' not in {r['process_instance_id'] for r in report['records']}
    plan = report['run']['plan_hash']
    tool(camunda, definitions=['foi-request-processing'], apply=True, confirm_plan=plan, reason='x')[0].suspend()
    assert camunda.items['r2']['suspended']
    assert not camunda.items['r1']['suspended']


def test_email_instances_are_reported_never_suspended():
    camunda = FakeCamunda(fee(), email())
    report = tool(camunda)[0].suspend()
    assert (by_id(report, 'e1')['outcome'], by_id(report, 'e1')['reason']) == (SKIPPED, 'email_in_flight_wait_for_drain')
    assert report['summary']['email_instances_in_flight'] == 1
    plan = report['run']['plan_hash']
    tool(camunda, apply=True, confirm_plan=plan, reason='x')[0].suspend()
    assert camunda.items['e1']['suspended'] is False


@pytest.mark.parametrize('key', ['foi-email-processing', 'cache_refresh', 'due_reminder_notifications',
                                 'foi-rawrequest-api-manager', 'unknown-key'])
def test_denied_and_unknown_definitions_cannot_be_selected(key):
    camunda = FakeCamunda()
    with pytest.raises(ValueError):
        CamundaSuspension(camunda, definitions=[key])


# --- interrupted and concurrent runs; failures ---------------------------------------------------------------------

def test_an_instance_tagged_but_not_suspended_is_resumed():
    camunda = FakeCamunda(fee(marker=marker_text()))
    report = tool(camunda)[0].suspend()
    assert (only(report)['outcome'], only(report)['reason']) == (SUSPEND, 'resume_interrupted_run')
    plan = report['run']['plan_hash']
    tool(camunda, apply=True, confirm_plan=plan, reason='x')[0].suspend()
    assert camunda.items['f1']['suspended'] is True


def test_an_instance_tagged_moments_ago_by_another_run_is_skipped():
    camunda = FakeCamunda(fee(marker=marker_text('other', at=NOW - timedelta(minutes=1))))
    report = tool(camunda)[0].suspend()
    assert (only(report)['outcome'], only(report)['reason']) == (SKIPPED, 'claimed_by_other_run')


def test_a_failed_suspension_is_recorded_the_marker_removed_and_the_run_continues():
    camunda = FakeCamunda(fee('f1', 100), fee('f2', 101, SUB2))
    camunda.fail_suspend.add('f1')
    store = FakeStore([sla(), sla(ministry=101, sub=SUB2)])
    plan = tool(camunda, store=store)[0].suspend()['run']['plan_hash']
    report = tool(camunda, store=store, apply=True, confirm_plan=plan, reason='x')[0].suspend()
    assert (by_id(report, 'f1')['outcome'], by_id(report, 'f1')['reason']) == (ERROR, 'suspend_failed')
    assert camunda.items['f1']['marker'] is None
    assert camunda.items['f1']['suspended'] is False
    assert by_id(report, 'f2')['outcome'] == SUSPEND
    assert camunda.items['f2']['suspended'] is True
    assert report['summary']['errors'] == 1


def test_a_suspension_that_does_not_read_back_is_an_error():
    camunda = FakeCamunda(fee())
    camunda.silent_suspend.add('f1')
    plan = tool(camunda)[0].suspend()['run']['plan_hash']
    report = tool(camunda, apply=True, confirm_plan=plan, reason='x')[0].suspend()
    assert only(report)['outcome'] == ERROR
    assert camunda.items['f1']['marker'] is None


def test_an_instance_suspended_or_gone_after_the_plan_is_not_touched():
    camunda = FakeCamunda(fee('f1', 100), fee('f2', 101, SUB2))
    store = FakeStore([sla(), sla(ministry=101, sub=SUB2)])
    plan = tool(camunda, store=store)[0].suspend()['run']['plan_hash']
    job, _ = tool(camunda, store=store, apply=True, confirm_plan=plan, reason='x')
    original = job._plan_suspend

    def plan_then_change():
        result = original()
        camunda.items['f1']['suspended'] = True  # someone suspended it by hand
        del camunda.items['f2']                  # and this one finished
        return result
    job._plan_suspend = plan_then_change
    report = job.suspend()
    assert by_id(report, 'f1')['reason'] == 'suspended_meanwhile'
    assert by_id(report, 'f2')['reason'] == 'gone_before_suspension'
    assert camunda.calls == []


# --- status and reactivate -------------------------------------------------------------------------------------------

def held(pid='f1', ministry=100, sub=SUB, key='fee', **extra):
    base = fee(pid, ministry, sub, suspended=True, marker=marker_text()) if key == 'fee' else lifecycle(pid, key, True, marker_text())
    base.update(extra)
    return base


def test_status_lists_only_what_this_tool_holds():
    camunda = FakeCamunda(held('f1'), fee('f2', suspended=True), fee('f3', marker=marker_text()))
    report = tool(camunda)[0].status()
    assert {r['process_instance_id']: r['outcome'] for r in report['records']} == {'f1': ALREADY_HELD, 'f3': REVIEW}
    assert report['summary']['held_suspended_by_this_tool'] == 1
    assert tool(camunda, only_run_id='nope')[0].status()['records'] == []


def test_reactivate_dry_run_then_apply_activates_and_removes_the_marker(tmp_path):
    camunda = FakeCamunda(held())
    report = tool(camunda)[0].reactivate()
    assert (only(report)['outcome'], only(report)['reason']) == (REACTIVATE, 'n8n_row_untouched_backfill')
    assert camunda.calls == []
    job, _ = tool(camunda, apply=True, confirm_plan=report['run']['plan_hash'],
                  ledger=Ledger(str(tmp_path), 'test-run', 'reactivate'))
    result = job.reactivate()
    job.ledger.close()
    assert result['summary']['reactivated'] == 1
    assert camunda.items['f1']['suspended'] is False
    assert camunda.items['f1']['marker'] is None
    assert [json.loads(line)['event'] for line in open(job.ledger.path, encoding='utf-8')] == [
        'plan', 'reactivate_intent', 'reactivated']
    again = tool(camunda)[0].reactivate()
    assert again['records'] == []  # a second run finds no markers


def test_reactivate_never_touches_an_instance_someone_else_suspended():
    camunda = FakeCamunda(fee('f9', suspended=True))
    report = tool(camunda, apply=True, confirm_plan=tool(camunda)[0].reactivate()['run']['plan_hash'])[0].reactivate()
    assert report['records'] == []
    assert camunda.calls == []


@pytest.mark.parametrize('row, outcome, reason', [
    (sla(status='PAID', comments='Closed by foi-manage-payment (paid) in execution 9.'), BLOCKED, 'n8n_owns_payment'),
    (sla(status='CANCELLED', comments='Closed by x'), BLOCKED, 'n8n_owns_payment'),
    (sla(status='PAID_PENDING_SIDE_EFFECTS', comments='x'), BLOCKED, 'n8n_owns_payment'),
    (sla(status='EXPIRED', comments='Closed by foi-payment-expired in execution 4.'), BLOCKED, 'expired_by_n8n'),
    (sla(status='PENDING', comments='PENDING: payment initiation started'), BLOCKED, 'n8n_owns_payment'),
    (sla(status='ACTIVE', comments='Online payment created', started_execution_id='7'), BLOCKED, 'n8n_owns_payment'),
    (sla(status='ACTIVE'), REACTIVATE, 'n8n_row_untouched_backfill'),
    (sla(status='EXPIRED', comments='BACKFILL(camunda) run r: instance f1, expired and notified in Camunda, expirycounter=1'),
     REACTIVATE, 'n8n_row_untouched_backfill'),
])
def test_a_fee_instance_n8n_has_acted_on_is_not_reactivated(row, outcome, reason):
    report = tool(FakeCamunda(held()), rows=[row])[0].reactivate()
    assert (only(report)['outcome'], only(report)['reason']) == (outcome, reason)


def test_no_n8n_row_means_n8n_never_owned_it_and_the_check_can_be_skipped():
    assert only(tool(FakeCamunda(held()), rows=[])[0].reactivate())['reason'] == 'no_n8n_row'

    def boom():
        raise AssertionError('n8n must not be read')
    report = tool(FakeCamunda(held()), store_factory=boom, n8n_check=False)[0].reactivate()
    assert (only(report)['outcome'], only(report)['reason']) == (REACTIVATE, 'n8n_check_skipped')


def test_reactivation_order_is_lifecycle_before_fee_and_a_stray_marker_is_only_cleared():
    camunda = FakeCamunda(held('f1'), held('r1', key='foi-request'), held('r2', key='foi-request-processing'),
                          fee('f3', marker=marker_text()))
    report = tool(camunda)[0].reactivate()
    assert [r['definition_key'] for r in report['records']][:3] == ['foi-request', 'foi-request-processing',
                                                                    'foi-fee-processing']
    assert by_id(report, 'f3')['outcome'] == CLEAR_MARKER
    plan = report['run']['plan_hash']
    tool(camunda, apply=True, confirm_plan=plan)[0].reactivate()
    assert [c for c in camunda.calls if c[0] == 'activate'] == [('activate', 'r1'), ('activate', 'r2'), ('activate', 'f1')]
    assert camunda.items['f3']['marker'] is None
    assert ('activate', 'f3') not in camunda.calls


def test_reactivate_with_a_stale_plan_hash_changes_nothing():
    camunda = FakeCamunda(held())
    plan = tool(camunda)[0].reactivate()['run']['plan_hash']
    camunda.items['f2'] = held('f2', 101, SUB2)
    job, _ = tool(camunda, rows=[sla(), sla(ministry=101, sub=SUB2)], apply=True, confirm_plan=plan)
    with pytest.raises(PlanChangedError):
        job.reactivate()
    assert camunda.calls == []


def test_run_id_limits_reactivation_to_one_run():
    camunda = FakeCamunda(held('f1'), held('f2', 101, SUB2, marker=marker_text('run-b')))
    report = tool(camunda, rows=[sla(), sla(ministry=101, sub=SUB2)], only_run_id='run-b')[0].reactivate()
    assert [r['process_instance_id'] for r in report['records']] == ['f2']


# --- reports ------------------------------------------------------------------------------------------------------------

def test_report_has_no_internal_fields_and_the_csv_and_summary_read_well():
    camunda = FakeCamunda(fee('f1', 100), fee('f2', 101, SUB2, waiting=False))
    report = tool(camunda, rows=[sla()])[0].suspend()
    assert all(not any(k.startswith('_') for k in r) for r in report['records'])
    text = report_csv_text(report)
    assert text.startswith('﻿')
    rows = list(csv.DictReader(text.lstrip('﻿').splitlines()))
    assert {r['process_instance_id']: r['outcome'] for r in rows} == {'f1': SUSPEND, 'f2': SKIPPED}
    summary = format_summary(report)
    assert 'Plan hash: %s' % report['run']['plan_hash'] in summary
    assert '--apply --confirm-plan' in summary
    assert 'formId' not in json.dumps(report)
    assert FORM not in json.dumps(report)  # no payment link material


def test_the_plan_hash_does_not_change_between_identical_runs():
    camunda = FakeCamunda(fee())
    assert tool(camunda)[0].suspend()['run']['plan_hash'] == tool(camunda, run_id='another')[0].suspend()['run']['plan_hash']


# --- the Camunda REST client ---------------------------------------------------------------------------------------------

class FakeResponse:
    def __init__(self, status=200, payload=None):
        self.status_code, self.payload = status, payload
        self.ok = status < 400
        self.content = b'' if payload is None else json.dumps(payload).encode()

    def json(self):
        return self.payload


class FakeSession:
    def __init__(self, *responses):
        self.responses, self.requests = list(responses), []

    def request(self, method, url, params=None, data=None, headers=None, timeout=None):
        self.requests.append(SimpleNamespace(method=method, url=url, params=params,
                                             body=json.loads(data) if data else None, headers=headers))
        return self.responses.pop(0)


def client(*responses, provider=None, **kwargs):
    session = FakeSession(*responses)
    kwargs.setdefault('sleep', lambda seconds: None)  # no real pauses in the tests
    return CamundaClient('http://camunda.test/engine-rest/', provider or (lambda: 'tok'), session, **kwargs), session


def test_client_pages_instances_and_sends_the_bearer_token():
    camunda, session = client(FakeResponse(200, [{'id': 'a'}, {'id': 'b'}]), FakeResponse(200, [{'id': 'c'}]), page_size=2)
    assert [i['id'] for i in camunda.instances('foi-fee-processing')] == ['a', 'b', 'c']
    first, second = session.requests
    assert first.url == 'http://camunda.test/engine-rest/process-instance'
    assert (first.params, second.params) == ({'firstResult': 0, 'maxResults': 2}, {'firstResult': 2, 'maxResults': 2})
    assert first.body['processDefinitionKey'] == 'foi-fee-processing'
    assert first.headers['Authorization'] == 'Bearer tok'


def test_client_marker_and_suspension_calls():
    camunda, session = client(FakeResponse(204), FakeResponse(204), FakeResponse(204), FakeResponse(404),
                              FakeResponse(200, {'value': 'text'}))
    camunda.set_marker('p1', 'text')
    camunda.set_suspended('p1', True)
    camunda.set_suspended('p1', False)
    camunda.delete_marker('p1')  # a 404 is fine: nothing to remove
    assert camunda.marker('p1') == 'text'
    marker_put, suspend, activate, delete, read = session.requests
    assert (marker_put.method, marker_put.url.endswith('/process-instance/p1/variables/%s' % MARKER_VARIABLE),
            marker_put.body) == ('PUT', True, {'value': 'text', 'type': 'String'})
    assert (suspend.url.endswith('/process-instance/p1/suspended'), suspend.body) == (True, {'suspended': True})
    assert activate.body == {'suspended': False}
    assert delete.method == 'DELETE'
    assert read.params == {'deserializeValue': 'false'}


def test_client_marker_read_of_an_absent_variable_is_none():
    camunda, _ = client(FakeResponse(404))
    assert camunda.marker('p1') is None


def test_client_failures_are_source_errors():
    camunda, _ = client(FakeResponse(500))
    with pytest.raises(SuspensionSourceError, match='HTTP 500'):
        camunda.set_suspended('p1', True)
    unconfigured = CamundaClient('', lambda: 'tok', FakeSession())
    with pytest.raises(SuspensionSourceError, match='BPM_ENGINE_REST_URL'):
        unconfigured.instances('x')


def test_client_variable_query_asks_only_for_the_whitelist():
    camunda, session = client(FakeResponse(200, [
        {'name': 'formId', 'value': 'F', 'processInstanceId': 'p1', 'executionId': 'e9'},
        {'name': 'formId', 'value': 'G', 'processInstanceId': 'p1', 'executionId': 'p1'}]))
    assert camunda.variables(['p1'], svc.FEE_VARIABLES) == {'p1': {'formId': 'G'}}  # the process-level value wins
    body = session.requests[0].body
    assert body['variableNameIn'] == list(svc.FEE_VARIABLES)
    assert not {'accessToken', 'base64userpass', 'formioRootPassword'} & set(body['variableNameIn'])


# --- the command line ----------------------------------------------------------------------------------------------------

def test_cli_apply_needs_a_confirm_plan_and_a_reason():
    for argv in (['suspend', '--apply'], ['suspend', '--apply', '--confirm-plan', 'a' * 16],
                 ['reactivate', '--apply']):
        with pytest.raises(SystemExit):
            cli.parse_args(argv)
    args = cli.parse_args(['suspend', '--apply', '--confirm-plan', 'A' * 16, '--reason', 'CCP-5801'])
    assert args.apply
    assert args.reason == 'CCP-5801'
    assert cli.parse_args(['reactivate', '--apply', '--confirm-plan', 'a' * 16]).apply


@pytest.mark.parametrize('argv', [
    ['suspend', '--confirm-plan', 'a' * 16],
    ['suspend', '--apply', '--confirm-plan', 'nothex', '--reason', 'x'],
    ['suspend', '--definition', 'cache_refresh'],
    ['suspend', '--definition', 'foi-email-processing'],
    ['preview', '--definition', 'foi-fee-processing'],
    ['bogus'],
])
def test_cli_rejects_bad_arguments(argv):
    with pytest.raises(SystemExit):
        cli.parse_args(argv)


def test_cli_dry_run_is_the_default_for_every_command():
    for command in ('preview', 'suspend', 'reactivate', 'status'):
        assert not getattr(cli.parse_args([command]), 'apply', False)


def run_cli(monkeypatch, tmp_path, argv, camunda, rows=None):
    monkeypatch.setattr(cli, 'CamundaClient', lambda: camunda)
    store = FakeStore(rows if rows is not None else [sla()])
    monkeypatch.setattr(cli, 'N8NPaymentSlaStore', lambda: store)
    monkeypatch.chdir(tmp_path)
    return cli.main(argv)


def test_cli_preview_writes_json_and_an_excel_readable_csv(monkeypatch, tmp_path, capsys):
    camunda = FakeCamunda(fee(), fee('f2', 101, SUB2, waiting=False))
    code = run_cli(monkeypatch, tmp_path, ['preview', '--report-file', 'p.json', '--report-csv', 'p.csv', '--strict'], camunda)
    assert code == 0
    assert json.loads((tmp_path / 'p.json').read_text(encoding='utf-8'))['run']['command'] == 'preview'
    assert (tmp_path / 'p.csv').read_bytes().startswith(b'\xef\xbb\xbf')
    assert 'Plan hash' in capsys.readouterr().out
    assert camunda.calls == []


def test_cli_dry_run_then_apply_with_the_reviewed_hash(monkeypatch, tmp_path, capsys):
    camunda = FakeCamunda(fee())
    run_cli(monkeypatch, tmp_path, ['suspend', '--report-file', 'dry.json'], camunda)
    plan = json.loads((tmp_path / 'dry.json').read_text(encoding='utf-8'))['run']['plan_hash']
    assert camunda.calls == []
    code = run_cli(monkeypatch, tmp_path, ['suspend', '--apply', '--confirm-plan', plan, '--reason', 'CCP-5801',
                                           '--pace-ms', '0', '--report-file', 'apply.json'], camunda)
    assert code == 0
    assert camunda.items['f1']['suspended'] is True
    assert list(tmp_path.glob('camunda_suspension_ledger_suspend_*.jsonl'))
    assert json.loads((tmp_path / 'apply.json').read_text(encoding='utf-8'))['run']['mode'] == 'apply'


def test_cli_exit_codes(monkeypatch, tmp_path, capsys):
    camunda = FakeCamunda(fee())
    assert run_cli(monkeypatch, tmp_path, ['suspend', '--apply', '--confirm-plan', '0' * 16, '--reason', 'x',
                                           '--report-file', 'a.json'], camunda) == cli.EXIT_PLAN_CHANGED
    assert 'Nothing was changed' in capsys.readouterr().err
    assert camunda.calls == []
    plan = json.loads((tmp_path / 'a.json').read_text(encoding='utf-8'))['run']['plan_hash']
    assert run_cli(monkeypatch, tmp_path, ['suspend', '--apply', '--confirm-plan', plan, '--reason', 'x',
                                           '--max-instances', '0', '--report-file', 'b.json'], camunda) == cli.EXIT_PLAN_TOO_LARGE
    review = FakeCamunda(fee(incident=True))
    assert run_cli(monkeypatch, tmp_path, ['preview', '--strict', '--report-file', 'c.json'], review) == cli.EXIT_MANUAL_REVIEW
    assert run_cli(monkeypatch, tmp_path, ['preview', '--report-file', 'd.json'], review) == 0
    failing = FakeCamunda(fee())
    failing.fail_suspend.add('f1')
    run_cli(monkeypatch, tmp_path, ['suspend', '--report-file', 'e.json'], failing)
    plan = json.loads((tmp_path / 'e.json').read_text(encoding='utf-8'))['run']['plan_hash']
    assert run_cli(monkeypatch, tmp_path, ['suspend', '--apply', '--confirm-plan', plan, '--reason', 'x', '--pace-ms', '0',
                                           '--report-file', 'f.json'], failing) == cli.EXIT_RECORD_ERRORS


def test_cli_reports_a_source_failure_without_a_traceback(monkeypatch, tmp_path, capsys):
    class Broken:
        def marker_holders(self):
            raise SuspensionSourceError('Camunda POST /variable-instance answered HTTP 401')
    assert run_cli(monkeypatch, tmp_path, ['status'], Broken()) == cli.EXIT_SOURCE_FAILURE
    assert 'HTTP 401' in capsys.readouterr().err


def test_cli_status_and_reactivate(monkeypatch, tmp_path):
    camunda = FakeCamunda(held())
    assert run_cli(monkeypatch, tmp_path, ['status', '--report-file', 's.json'], camunda) == 0
    run_cli(monkeypatch, tmp_path, ['reactivate', '--report-file', 'r.json'], camunda)
    plan = json.loads((tmp_path / 'r.json').read_text(encoding='utf-8'))['run']['plan_hash']
    assert camunda.items['f1']['suspended'] is True
    assert run_cli(monkeypatch, tmp_path, ['reactivate', '--apply', '--confirm-plan', plan, '--pace-ms', '0',
                                           '--report-file', 'r2.json'], camunda) == 0
    assert camunda.items['f1']['suspended'] is False
    assert camunda.items['f1']['marker'] is None


# --- the connection problems seen on a real run: a token on every call, no retry, no stop ------------------------

def test_the_token_is_fetched_once_and_reused_until_it_is_old():
    tokens, now = [], [0.0]

    def provider():
        tokens.append(len(tokens) + 1)
        return 'tok%d' % len(tokens)
    camunda, session = client(*[FakeResponse(204) for _ in range(4)], provider=provider, clock=lambda: now[0])
    camunda.set_suspended('a', True)
    camunda.set_suspended('b', True)
    now[0] = svc.TOKEN_TTL_SECONDS + 1
    camunda.set_suspended('c', True)
    camunda.set_suspended('d', True)
    assert tokens == [1, 2]  # not one per call
    assert [r.headers['Authorization'] for r in session.requests] == ['Bearer tok1', 'Bearer tok1', 'Bearer tok2', 'Bearer tok2']


def test_a_network_failure_is_retried_then_succeeds():
    calls = []

    class Flaky(FakeSession):
        def request(self, *args, **kwargs):
            calls.append(1)
            if len(calls) < 3:
                raise svc.requests.ConnectTimeout('timed out')
            return super().request(*args, **kwargs)
    session = Flaky(FakeResponse(204))
    camunda = CamundaClient('http://camunda.test/engine-rest', lambda: 'tok', session, sleep=lambda s: None)
    camunda.set_suspended('p1', True)
    assert len(calls) == 3
    assert len(session.requests) == 1


def test_a_network_failure_that_keeps_happening_is_a_clean_error_after_the_retries():
    class Down(FakeSession):
        def request(self, *args, **kwargs):
            raise svc.requests.ConnectTimeout('timed out')
    camunda = CamundaClient('http://camunda.test/engine-rest', lambda: 'tok', Down(), sleep=lambda s: None)
    with pytest.raises(SuspensionSourceError, match='after 3 attempts: ConnectTimeout'):
        camunda.delete_marker('p1')


def test_a_token_endpoint_that_times_out_is_retried_with_a_new_token_request():
    attempts = []

    def provider():
        attempts.append(1)
        if len(attempts) == 1:
            raise svc.requests.ConnectTimeout('dev.loginproxy timed out')
        return 'tok'
    camunda, session = client(FakeResponse(204), provider=provider)
    camunda.set_suspended('p1', True)
    assert len(attempts) == 2
    assert session.requests[0].headers['Authorization'] == 'Bearer tok'


def test_an_expired_token_is_replaced_once_and_the_call_repeated():
    tokens = iter(['old', 'new'])
    camunda, session = client(FakeResponse(401), FakeResponse(204), provider=lambda: next(tokens))
    camunda.set_suspended('p1', True)
    assert [r.headers['Authorization'] for r in session.requests] == ['Bearer old', 'Bearer new']
    camunda, _ = client(FakeResponse(401), FakeResponse(401), provider=lambda: 'tok')
    with pytest.raises(SuspensionSourceError, match='HTTP 401'):
        camunda.set_suspended('p1', True)


def test_a_503_is_retried():
    camunda, session = client(FakeResponse(503), FakeResponse(204))
    camunda.set_suspended('p1', True)
    assert len(session.requests) == 2


def test_the_run_stops_after_repeated_failures_and_the_rest_are_marked_not_attempted(tmp_path):
    camunda = FakeCamunda(*[fee('f%d' % n, 100 + n, sub=SUB if n == 0 else SUB2) for n in range(5)])
    rows = [sla(ministry=100 + n, sub=SUB if n == 0 else SUB2) for n in range(5)]
    camunda.fail_suspend.update({'f0', 'f1', 'f2'})
    plan = tool(camunda, rows=rows)[0].suspend()['run']['plan_hash']
    job, _ = tool(camunda, rows=rows, apply=True, confirm_plan=plan, reason='x', max_consecutive_failures=3,
                  ledger=Ledger(str(tmp_path), 'test-run', 'suspend'))
    report = job.suspend()
    job.ledger.close()
    assert report['run']['aborted'] is True
    assert [by_id(report, 'f%d' % n)['reason'] for n in range(5)] == [
        'suspend_failed', 'suspend_failed', 'suspend_failed', 'not_attempted_run_aborted', 'not_attempted_run_aborted']
    assert not camunda.items['f3']['suspended']
    assert ('suspend', 'f3') not in camunda.calls
    assert 'RUN STOPPED EARLY' in format_summary(report)
    assert 'aborted' in [json.loads(line)['event'] for line in open(job.ledger.path, encoding='utf-8')]


def test_a_success_between_failures_does_not_stop_the_run():
    camunda = FakeCamunda(*[fee('f%d' % n, 100 + n, sub=SUB if n == 0 else SUB2) for n in range(4)])
    rows = [sla(ministry=100 + n, sub=SUB if n == 0 else SUB2) for n in range(4)]
    camunda.fail_suspend.update({'f0', 'f2'})
    plan = tool(camunda, rows=rows)[0].suspend()['run']['plan_hash']
    report = tool(camunda, rows=rows, apply=True, confirm_plan=plan, reason='x', max_consecutive_failures=2)[0].suspend()
    assert report['run']['aborted'] is False
    assert [by_id(report, 'f%d' % n)['outcome'] for n in range(4)] == [ERROR, SUSPEND, ERROR, SUSPEND]


def test_activated_but_marker_not_removed_is_reported_as_such_and_a_rerun_clears_it():
    camunda = FakeCamunda(held())
    camunda.fail_delete_marker.add('f1')
    plan = tool(camunda)[0].reactivate()['run']['plan_hash']
    report = tool(camunda, apply=True, confirm_plan=plan)[0].reactivate()
    record = only(report)
    assert (record['outcome'], record['reason']) == (ERROR, 'marker_not_removed_after_activation')
    assert 'ACTIVE' in record['detail']
    assert camunda.items['f1']['suspended'] is False
    assert camunda.items['f1']['marker'] is not None
    camunda.fail_delete_marker.clear()
    again = tool(camunda)[0].reactivate()
    assert (only(again)['outcome'], only(again)['reason']) == (CLEAR_MARKER, 'stale_marker_on_active_instance')
    tool(camunda, apply=True, confirm_plan=again['run']['plan_hash'])[0].reactivate()
    assert camunda.items['f1']['marker'] is None
    assert camunda.calls.count(('activate', 'f1')) == 1


def test_cli_max_failures_option():
    assert cli.parse_args(['suspend']).max_failures == 3
    assert cli.parse_args(['reactivate', '--max-failures', '0']).max_failures == 0
