"""Payment SLA backfill: Camunda fee instances -> n8n ``foi-payment-sla`` rows.

Pure tests: Camunda, the FOI database and the n8n Data Table are replaced by in-memory fakes, so nothing here
needs a database or network.
"""

import csv
import json
import re
from datetime import datetime, timezone
from types import SimpleNamespace
from urllib.parse import parse_qsl, urlsplit

import pytest

import payment_sla_backfill_cli as cli
from request_api.services import paymentslabackfillapi as backfillapi
from request_api.services import paymentslabackfillservice as svc
from request_api.services.paymentslabackfillservice import (
    ALREADY_VALID, CREATE, ERROR, EXPIRED_NOTIFIED, EXPIRY_UNRESOLVED, INVALID_IDS, SKIPPED, SLA_CONFLICT,
    BackfillSourceError, CamundaFeeSource, FoiPaymentSource, N8NPaymentSlaStore, N8NStoreError, PaymentSlaBackfill,
    PlanChangedError, compute_expires_at, format_summary, parse_payment_url, report_csv_text)

FORM = '638a2faabfddffe844de095d'
SUB = '6ae11636bfaa24f7903a8c3d'
SUB2 = '65666dd639a8bd03526d6adf'
NOW = datetime(2026, 10, 30, 20, 0, tzinfo=timezone.utc)


def url(form=FORM, sub=SUB):
    return 'https://payments.example.test/public/form/%s/submission/%s/edit' % (form, sub)


def instance(pid='p1', ministry=100, foi=10, form=FORM, sub=SUB, expiry='2030-01-10', counter=0,
             status='NOT PAID', offline=False, waiting=True, suspended=False, **extra):
    variables = {'formId': form, 'submissionId': sub, 'formUrl': 'https://forms.example.test/form/%s/submission/%s' % (
        form, sub), 'paymentExpiryDate': expiry, 'paymentstatus': status, 'expirycounter': counter,
                 'foiRequestID': foi, 'ministryRequestID': ministry, 'fileNumber': 'EDU-2030-%s' % ministry,
                 'servicekey': 'na', 'templateName': 'FEEESTIMATE', 'prevStatus': 'Fee Estimate',
                 'isofflinepayment': offline, 'applicantCorrespondenceId': 7}
    variables.update(extra)
    variables = {k: v for k, v in variables.items() if v is not ...}
    return {'id': pid, 'suspended': suspended, 'waiting': waiting, 'variables': variables}


def payment(ministry=100, form=FORM, sub=SUB, expiry='2030-01-10', paymentid=1):
    return {'paymentid': paymentid, 'form_id': form, 'submission_id': sub, 'payment_url': url(form, sub),
            'expiry': expiry}


class FakeCamunda:
    def __init__(self, *instances):
        self.instances = list(instances)

    def fetch(self):
        return self.instances


class FakeFoi:
    def __init__(self, payments=None, unpaid_requests=None):
        self.payments = payments or {}
        self.unpaid_requests = unpaid_requests
        self.closed = False

    def close(self):
        self.closed = True

    def active_payments(self, ids):
        return {i: self.payments[i] for i in ids if i in self.payments}

    def active_payment_request_ids(self):
        return set(self.payments) if self.unpaid_requests is None else set(self.unpaid_requests)

    def requests(self, ids):
        return {i: {'foi_request_id': 10, 'file_number': 'EDU-2030-%d' % i} for i in ids}


class FakeStore:
    def __init__(self, rows=None):
        self.rows = [dict(r) for r in (rows or [])]
        self.next_id = max([r['id'] for r in self.rows], default=0) + 1
        self.insert_calls, self.deleted = 0, []
        self.fail_inserts = 0
        self.fail_for = set()
        self.rival_before_insert = None

    def list_rows(self, ministry_request_id=None):
        return [dict(r) for r in self.rows if ministry_request_id is None
                or r['ministry_request_id'] == str(ministry_request_id)]

    def insert(self, row):
        self.insert_calls += 1
        if self.fail_inserts:
            self.fail_inserts -= 1
            raise N8NStoreError('n8n POST rows answered HTTP 503')
        if row['ministry_request_id'] in self.fail_for:
            raise N8NStoreError('n8n POST rows answered HTTP 500')
        if self.rival_before_insert:  # another run inserted first
            self.rows.append(dict(self.rival_before_insert, id=self.next_id))
            self.next_id += 1
            self.rival_before_insert = None
        stored = dict(row, id=self.next_id)
        self.next_id += 1
        self.rows.append(stored)
        return dict(stored)

    def delete(self, row_id):
        self.deleted.append(row_id)
        self.rows = [r for r in self.rows if r['id'] != row_id]


def sla_row(status='ACTIVE', ministry=100, sub=SUB, form=FORM, expires='2030-01-11T07:59:59.999Z', row_id=1):
    return {'id': row_id, 'sla_type': 'payment-expiry', 'sla_status': status, 'ministry_request_id': str(ministry),
            'form_id': form, 'submission_id': sub, 'expires_at': expires, 'payment_expiry_date': '2030-01-10'}


def agreeing_foi(instances):
    """A database that agrees with Camunda: every instance's payment is unpaid, with the same ids and deadline."""
    return FakeFoi({
        i['variables']['ministryRequestID']: [payment(form=i['variables'].get('formId') or FORM,
                                                      sub=i['variables'].get('submissionId') or SUB,
                                                      expiry=str(i['variables'].get('paymentExpiryDate') or '')[:10])]
        for i in instances})


def backfill(instances, payments=None, rows=None, apply=False, include_expired=False, **kwargs):
    store = kwargs.pop('store', None) or FakeStore(rows)
    foi = kwargs.pop('foi', None) or (FakeFoi(payments) if payments is not None else agreeing_foi(instances))
    job = PaymentSlaBackfill(FakeCamunda(*instances), foi, store, apply=apply, include_expired=include_expired,
                             run_id='test-run', operator='tester', clock=lambda: NOW, **kwargs)
    return job.run(), store


def only(report):
    assert len(report['records']) == 1
    return report['records'][0]


# --- 1. 2. 3. eligible, already present, rerun -------------------------------------------------------------------

def test_eligible_payment_without_row_is_planned_in_a_dry_run_and_inserted_when_applied():
    report, store = backfill([instance()])
    record = only(report)
    assert (record['outcome'], record['reason']) == (CREATE, 'insert_active_row')
    assert report['run']['mode'] == 'dry-run' and store.rows == []
    assert report['summary']['sla_rows_would_be_created'] == 1 and 'sla_rows_created' not in report['summary']

    report, store = backfill([instance()], apply=True)
    assert report['summary']['sla_rows_created'] == 1 and len(store.rows) == 1
    row = store.rows[0]
    assert (row['sla_type'], row['sla_status'], row['payment_status']) == ('payment-expiry', 'ACTIVE', 'NOT PAID')
    assert (row['form_id'], row['submission_id']) == (FORM, SUB)
    assert (row['ministry_request_id'], row['foi_request_id'], row['file_number']) == ('100', '10', 'EDU-2030-100')
    assert row['payment_expiry_date'] == '2030-01-10'
    assert row['expires_at'] == '2030-01-11T07:59:59.999Z'  # end of 10 Jan in Vancouver (PST) as UTC
    assert row['payment_url'] == url() and row['service_key'] == 'payonline' and row['applicant_correspondence_id'] == '7'
    assert json.loads(row['metadata'])['camunda_process_instance_id'] == 'p1'
    assert row['comments'].startswith('BACKFILL(camunda) run test-run')
    assert report['summary']['eligible_active_payments_still_missing_active_row'] == 0


def test_existing_valid_active_row_is_kept_and_its_deadline_is_not_reset():
    existing = sla_row(expires='2029-12-31T07:59:59.999Z')
    report, store = backfill([instance()], rows=[existing], apply=True)
    record = only(report)
    assert (record['outcome'], record['sla_row_id']) == (ALREADY_VALID, 1)
    assert store.insert_calls == 0 and store.rows == [existing]
    assert report['summary']['sla_rows_already_present_valid'] == 1


def test_second_run_creates_no_duplicates():
    store = FakeStore()
    instances = [instance('p1', 100), instance('p2', 101, sub=SUB2)]
    first, _ = backfill(instances, apply=True, store=store)
    snapshot = json.dumps(store.rows, sort_keys=True)
    second, _ = backfill(instances, apply=True, store=store)
    assert first['summary']['sla_rows_created'] == 2
    assert second['summary']['sla_rows_created'] == 0 and second['summary']['sla_rows_already_present_valid'] == 2
    assert json.dumps(store.rows, sort_keys=True) == snapshot and len(store.rows) == 2


# --- 4. 5. 6. 7. ineligible payments -------------------------------------------------------------------------------

@pytest.mark.parametrize('inst, payments, reason', [
    (instance(status='PAID'), None, 'camunda_payment_paid'),
    (instance(status='CANCELLED'), None, 'camunda_payment_cancelled'),
    (instance(), {}, 'database_shows_no_unpaid_payment'),  # paid or cancelled in the FOI database
    (instance(waiting=False), None, 'not_waiting_for_payment'),  # no longer at the payment gateway
    (instance(offline=True), None, 'offline_payment'),
])
def test_paid_cancelled_ended_and_offline_payments_are_skipped(inst, payments, reason):
    report, store = backfill([inst], payments=payments, apply=True)
    record = only(report)
    assert (record['outcome'], record['reason']) == (SKIPPED, reason)
    assert store.insert_calls == 0 and report['summary']['skipped_ineligible'] == 1
    assert report['summary']['eligible_unpaid_online_payments'] == 0


def test_expired_and_notified_payment_is_not_written_as_active():
    report, store = backfill([instance(counter=1, expiry='2023-01-10')], apply=True)
    record = only(report)
    assert (record['outcome'], record['reason']) == (EXPIRED_NOTIFIED, 'expired_and_notified_in_camunda')
    assert store.rows == []  # an ACTIVE row would make n8n notify the applicant a second time
    assert report['summary']['eligible_expired_and_notified_in_camunda'] == 1
    assert report['summary']['eligible_active_payments_still_missing_active_row'] == 0


def test_include_expired_writes_an_expired_row_never_an_active_one():
    report, store = backfill([instance(counter=1, expiry='2023-01-10')], apply=True, include_expired=True)
    assert only(report)['reason'] == 'insert_expired_row' and report['summary']['expired_rows_created'] == 1
    row = store.rows[0]
    assert (row['sla_status'], row['payment_status']) == ('EXPIRED', 'EXPIRED')
    assert row['completed_at']


# --- 8. 9. 10. identifiers and expiry --------------------------------------------------------------------------------

@pytest.mark.parametrize('overrides, reason', [
    ({'form': ''}, 'missing_form_id'),
    ({'form': ...}, 'missing_form_id'),
    ({'sub': ''}, 'missing_submission_id'),
    ({'sub': ...}, 'missing_submission_id'),
    ({'form': 'undefined'}, 'missing_form_id'),
    ({'sub': 'not-an-object-id'}, 'invalid_submission_id'),
    ({'form': 'xyz'}, 'invalid_form_id'),
    ({'ministry': ...}, 'missing_or_invalid_ministry_request_id'),
])
def test_missing_or_invalid_form_and_submission_ids_are_reported_not_guessed(overrides, reason):
    inst = instance(**overrides)
    if overrides.get('ministry') is ...:
        inst['variables'].pop('ministryRequestID', None)
    report, store = backfill([inst], payments={100: [payment()]}, apply=True)
    record = only(report)
    assert (record['outcome'], record['reason']) == (INVALID_IDS, reason)
    assert store.insert_calls == 0 and report['summary']['missing_or_invalid_form_or_submission_id'] == 1
    assert report['manual_review_required'] == 1


def test_form_url_that_disagrees_with_the_variables_is_reported():
    inst = instance(formUrl='https://forms.example.test/form/%s/submission/%s' % (FORM, SUB2))
    assert only(backfill([inst])[0])['reason'] == 'form_url_disagrees_with_variables'


@pytest.mark.parametrize('overrides, reason', [
    ({'expiry': ''}, 'missing_payment_expiry_date'),
    ({'expiry': ...}, 'missing_payment_expiry_date'),
    ({'expiry': 'next tuesday'}, 'invalid_payment_expiry_date'),
    ({'counter': ...}, 'missing_expirycounter'),
])
def test_missing_or_ambiguous_expiry_is_reported_and_no_deadline_is_invented(overrides, reason):
    inst = instance(**overrides)
    if overrides.get('counter') is ...:
        inst['variables'].pop('expirycounter', None)
    report, store = backfill([inst], apply=True)
    record = only(report)
    assert (record['outcome'], record['reason']) == (EXPIRY_UNRESOLVED, reason)
    assert store.insert_calls == 0 and report['summary']['missing_or_ambiguous_expiry'] == 1


def test_expiry_that_differs_from_the_database_is_ambiguous():
    report, _ = backfill([instance()], payments={100: [payment(expiry='2031-05-05')]})
    assert only(report)['reason'] == 'expiry_date_differs_from_database'


def test_payment_ids_not_found_in_the_database_payment_url_are_reported():
    report, _ = backfill([instance()], payments={100: [payment(sub=SUB2)]})
    assert (only(report)['outcome'], only(report)['reason']) == (INVALID_IDS, 'ids_not_found_in_database_payment_url')


# --- 11. existing SLA rows that conflict ---------------------------------------------------------------------------

@pytest.mark.parametrize('status', ['PAID', 'CANCELLED', 'EXPIRED'])
def test_terminal_row_for_the_same_payment_is_reported_and_never_revived(status):
    existing = sla_row(status)
    report, store = backfill([instance()], rows=[existing], apply=True)
    record = only(report)
    assert (record['outcome'], record['reason']) == (SLA_CONFLICT, 'existing_%s_row_for_same_payment' % status.lower())
    assert store.rows == [existing] and store.insert_calls == 0
    assert report['summary']['conflicting_or_terminal_sla_state'] == 1


def test_pending_row_or_open_row_for_another_payment_is_a_conflict():
    pending = backfill([instance()], rows=[sla_row('PENDING')])[0]
    assert only(pending)['reason'] == 'pending_row_for_same_payment'
    other = backfill([instance()], rows=[sla_row('ACTIVE', sub=SUB2)])[0]
    assert only(other)['reason'] == 'open_sla_row_for_a_different_payment'
    blank = backfill([instance()], rows=[sla_row('PENDING', sub='', form='')])[0]
    assert only(blank)['reason'] == 'open_sla_row_without_form_ids'


def test_closed_history_for_an_older_payment_does_not_block_a_new_row():
    old = sla_row('PAID', sub=SUB2)
    report, store = backfill([instance()], rows=[old], apply=True)
    assert only(report)['outcome'] == CREATE and len(store.rows) == 2


def test_active_row_without_a_deadline_is_reported_not_repaired():
    report, store = backfill([instance()], rows=[sla_row(expires=None)], apply=True)
    assert only(report)['reason'] == 'existing_active_row_has_no_expires_at' and store.insert_calls == 0


# --- 12. 14. failures and partial runs -----------------------------------------------------------------------------

def test_failed_insert_is_reported_and_a_retry_succeeds_without_duplicates():
    store = FakeStore()
    store.fail_inserts = 1
    first, _ = backfill([instance()], apply=True, store=store)
    assert (only(first)['outcome'], only(first)['reason']) == (ERROR, 'write_failed')
    assert first['summary']['errors'] == 1 and store.rows == []
    assert first['summary']['eligible_active_payments_still_missing_active_row'] == 1
    second, _ = backfill([instance()], apply=True, store=store)
    assert only(second)['outcome'] == CREATE and len(store.rows) == 1
    third, _ = backfill([instance()], apply=True, store=store)
    assert only(third)['outcome'] == ALREADY_VALID and len(store.rows) == 1


def test_partial_failure_keeps_the_successes_and_lists_the_failures():
    store = FakeStore()
    store.fail_for = {'101'}
    instances = [instance('p1', 100), instance('p2', 101, sub=SUB2), instance('p3', 102, sub='5' * 24),
                 instance('p4', 103, form='')]
    report, _ = backfill(instances, apply=True, store=store)
    outcomes = {r['process_instance_id']: r['outcome'] for r in report['records']}
    assert outcomes == {'p1': CREATE, 'p2': ERROR, 'p3': CREATE, 'p4': INVALID_IDS}
    assert sorted(r['ministry_request_id'] for r in store.rows) == ['100', '102']
    assert report['summary']['errors'] == 1 and report['summary']['sla_rows_created'] == 2
    assert report['summary']['eligible_active_payments_still_missing_active_row'] == 1
    assert cli.run(SimpleNamespace(apply=True, include_expired=False, ministry_request_id=[], strict=False),
                   FakeCamunda(*instances), FakeFoi({i['variables']['ministryRequestID']: [payment(
                       form=i['variables']['formId'] or FORM, sub=i['variables']['submissionId'])] for i in instances}),
                   FakeStore())[1] == 0
    assert cli.run(SimpleNamespace(apply=True, include_expired=False, ministry_request_id=[], strict=True),
                   FakeCamunda(*instances), FakeFoi({100: [payment()]}), FakeStore())[1] == cli.EXIT_MANUAL_REVIEW


def test_rival_run_that_inserted_first_wins_and_our_duplicate_is_removed():
    store = FakeStore()
    store.rival_before_insert = sla_row(row_id=0)
    report, _ = backfill([instance()], apply=True, store=store)
    record = only(report)
    assert (record['outcome'], record['reason']) == (SLA_CONFLICT, 'concurrent_run_created_a_row_first')
    assert len(store.rows) == 1 and store.deleted


# --- 13. dry run ---------------------------------------------------------------------------------------------------

def test_dry_run_makes_no_writes_and_has_the_same_summary_shape():
    instances = [instance('p1', 100), instance('p2', 101, sub=SUB2), instance('p3', 102, sub='5' * 24, status='PAID')]
    rows = [sla_row('PAID', ministry=999, sub=SUB2)]
    store = FakeStore(rows)
    dry, _ = backfill(instances, store=store)
    assert store.insert_calls == 0 and not store.deleted and store.rows == rows
    store2 = FakeStore(rows)
    applied, _ = backfill(instances, store=store2, apply=True)
    assert list(dry['summary'])[:4] == list(applied['summary'])[:4]
    assert dry['summary']['sla_rows_would_be_created'] == applied['summary']['sla_rows_created'] == 2
    assert dry['summary']['eligible_active_payments_still_missing_active_row'] == 2
    assert dry['summary']['eligible_active_payments_missing_active_row_after_apply'] == 0
    assert applied['summary']['eligible_active_payments_still_missing_active_row'] == 0


def test_dry_run_is_the_cli_default():
    args = cli.parse_args([])
    assert args.apply is False and args.include_expired is False
    assert cli.parse_args(['--apply', '--confirm-plan', '0123456789abcdef']).apply is True
    with pytest.raises(SystemExit):
        cli.parse_args(['--apply', '--confirm-plan', '0123456789abcdef', '--dry-run'])


# --- 15. several instances for the same payment ------------------------------------------------------------------

def test_duplicate_instances_for_one_payment_produce_one_row():
    report, store = backfill([instance('b'), instance('a', suspended=True), instance('c')], apply=True)
    by_id = {r['process_instance_id']: r for r in report['records']}
    assert by_id['b']['outcome'] == CREATE  # not suspended, lowest id
    assert by_id['a']['reason'] == by_id['c']['reason'] == 'duplicate_instance_for_same_payment'
    assert len(store.rows) == 1 and store.rows[0]['metadata'].count('"b"') == 1


def test_duplicates_that_disagree_on_expiry_are_not_guessed():
    report, store = backfill([instance('a', expiry='2030-01-10'), instance('b', expiry='2030-01-10', counter=1)],
                             apply=True)
    assert {r['reason'] for r in report['records']} == {'duplicate_instances_disagree_on_expiry'}
    assert store.insert_calls == 0


def test_stale_instance_of_a_reissued_payment_is_superseded_by_the_matching_one():
    stale, current = instance('old', sub=SUB2), instance('new', sub=SUB)
    report, store = backfill([stale, current], payments={100: [payment(sub=SUB, paymentid=2)]}, apply=True)
    by_id = {r['process_instance_id']: r for r in report['records']}
    assert by_id['old']['reason'] == 'superseded_instance' and by_id['new']['outcome'] == CREATE
    assert [r['submission_id'] for r in store.rows] == [SUB]


def test_two_active_payments_for_one_request_are_not_given_two_rows():
    payments = {100: [payment(sub=SUB, paymentid=1), payment(sub=SUB2, paymentid=2)]}
    report, store = backfill([instance('a', sub=SUB), instance('b', sub=SUB2)], payments=payments, apply=True)
    assert {r['reason'] for r in report['records']} == {'multiple_active_payments_for_request'}
    assert store.insert_calls == 0


def test_suspended_instances_are_still_backfilled_and_flagged():
    report, store = backfill([instance(suspended=True)], apply=True)
    assert only(report)['suspended'] is True and only(report)['outcome'] == CREATE and len(store.rows) == 1


def test_camunda_ministry_request_id_is_accepted_as_integer_or_string():
    report, _ = backfill([instance('a', ministry=100), instance('b', ministry='101', sub=SUB2)],
                         payments={100: [payment()], 101: [payment(sub=SUB2)]})
    assert [r['outcome'] for r in report['records']] == [CREATE, CREATE]
    assert [r['ministry_request_id'] for r in report['records']] == [100, 101]


def test_request_scope_limits_the_run_and_unpaid_payments_without_an_instance_are_counted():
    foi = FakeFoi({100: [payment()], 101: [payment(sub=SUB2)], 555: [payment(sub='6' * 24)]})
    report, store = backfill([instance('a', 100), instance('b', 101, sub=SUB2)], foi=foi, apply=True,
                             ministry_request_ids=[100])
    assert [r['outcome'] for r in report['records']] == [CREATE, SKIPPED] and len(store.rows) == 1
    assert report['summary']['database_unpaid_payments_without_camunda_instance'] == 1
    assert report['summary']['camunda_instances_examined'] == 2


# --- reporting and secrets -----------------------------------------------------------------------------------------

def test_report_has_references_for_every_exception_and_no_payment_secrets():
    secret = 'hunter2-formio-password'
    bad = instance('p-bad', 101, form='', formioRootPassword=secret, accessToken='tok-123')
    good = instance('p-good', 100, formioRootPassword=secret)
    report, _ = backfill([good, bad], payments={100: [payment()], 101: [payment()]}, apply=True)
    text = json.dumps(report) + format_summary(report)
    assert secret not in text and 'tok-123' not in text and url() not in text and 'payments.example.test' not in text
    exception = [r for r in report['records'] if r['outcome'] == INVALID_IDS][0]
    assert exception['process_instance_id'] == 'p-bad' and exception['ministry_request_id'] == 101
    assert exception['foi_request_id'] == 10 and exception['reason'] == 'missing_form_id'
    assert 'form_id' not in exception  # ids only appear where a row exists or is planned
    assert 'instance=p-bad ministry_request=101' in format_summary(report)
    assert set(report['summary']) >= {
        'camunda_instances_examined', 'candidate_payments_waiting_in_camunda', 'eligible_unpaid_online_payments',
        'sla_rows_already_present_valid', 'sla_rows_created', 'skipped_ineligible',
        'missing_or_invalid_form_or_submission_id', 'missing_or_ambiguous_expiry',
        'conflicting_or_terminal_sla_state', 'errors', 'eligible_active_payments_still_missing_active_row'}


def test_reports_are_written_as_json_and_csv(tmp_path):
    report, _ = backfill([instance()])
    cli.write_reports(report, str(tmp_path / 'r.json'), str(tmp_path / 'r.csv'))
    assert json.loads((tmp_path / 'r.json').read_text())['run']['id'] == 'test-run'
    assert (tmp_path / 'r.csv').read_bytes().startswith(b'\xef\xbb\xbf')  # BOM: Excel reads the file as UTF-8
    header, line = (tmp_path / 'r.csv').read_text(encoding='utf-8-sig').splitlines()[:2]
    assert header.startswith('process_instance_id,ministry_request_id') and line.startswith('p1,100,10')


# --- expiry timestamp --------------------------------------------------------------------------------------------

@pytest.mark.parametrize('raw, expected', [
    ('2030-01-10', '2030-01-11T07:59:59.999Z'),     # PST, UTC-8
    ('2026-07-15', '2026-07-16T06:59:59.999Z'),     # PDT, UTC-7
    ('2026-03-08', '2026-03-09T06:59:59.999Z'),     # the day DST starts: end of day is already PDT
    ('2026-11-01', '2026-11-02T07:59:59.999Z'),     # the day DST ends: end of day is PST
    ('2030-01-10T12:00:00Z', '2030-01-10T12:00:00.000Z'),
    ('2030-01-10T12:00:00-08:00', '2030-01-10T20:00:00.000Z'),
    ('2030-01-10T12:00:00', '2030-01-10T20:00:00.000Z'),  # naive date-time is Vancouver time
])
def test_expires_at_follows_the_n8n_build_payment_sla_rule(raw, expected):
    assert compute_expires_at(raw) == expected


@pytest.mark.parametrize('raw', ['', None, 'undefined', 'garbage', '2030-13-45'])
def test_expires_at_is_none_for_a_missing_or_invalid_date(raw):
    assert compute_expires_at(raw) is None


def test_payment_url_ids_are_parsed_from_both_url_shapes():
    assert parse_payment_url(url()) == (FORM, SUB)
    assert parse_payment_url('https://x.test/public/form/%s/submission/%s' % (FORM.upper(), SUB)) == (FORM, SUB)
    assert parse_payment_url('https://x.test/other') == (None, None) and parse_payment_url(None) == (None, None)


# --- adapters ------------------------------------------------------------------------------------------------------

class FakeResponse:
    def __init__(self, payload, status=200):
        self.payload, self.status_code, self.ok = payload, status, status < 400
        self.content = b'x' if payload is not None else b''

    def json(self):
        return self.payload


class FakeSession:
    def __init__(self, handler):
        self.handler, self.calls = handler, []

    def post(self, url_, data=None, params=None, headers=None, timeout=None):
        self.calls.append(('POST', url_, json.loads(data), params, headers))
        return self.handler('POST', url_, json.loads(data), params)

    def request(self, method, url_, json=None, headers=None, timeout=None):
        parts = urlsplit(url_)
        assert not re.search(r'[{}:,"]', parts.query), 'n8n needs a fully percent-encoded query string'
        params = dict(parse_qsl(parts.query)) or None
        url_ = url_.split('?')[0]
        self.calls.append((method, url_, json, params, headers))
        return self.handler(method, url_, json, params)


def test_camunda_source_requests_only_whitelisted_variables_and_pages():
    def handler(method, url_, body, params):
        if url_.endswith('/process-instance'):
            first = params['firstResult']
            return FakeResponse([{'id': 'i%d' % n, 'suspended': n == 2} for n in range(first, min(first + 2, 3))])
        if url_.endswith('/execution'):
            assert body['activityId'] == 'Gateway_1771ld6' and body['processDefinitionKey'] == 'foi-fee-processing'
            waiting = [{'processInstanceId': 'i0'}, {'processInstanceId': 'i2'}]
            return FakeResponse(waiting[params['firstResult']:params['firstResult'] + 2])
        assert url_.endswith('/variable-instance') and params == {'deserializeValues': 'false'}
        assert 'formioRootPassword' not in body['variableNameIn'] and 'accessToken' not in body['variableNameIn']
        return FakeResponse([
            {'name': 'ministryRequestID', 'value': '41', 'processInstanceId': 'i0', 'executionId': 'i0'},
            {'name': 'formId', 'value': FORM, 'processInstanceId': 'i0', 'executionId': 'child'},
            {'name': 'formId', 'value': 'x' * 24, 'processInstanceId': 'i0', 'executionId': 'i0'},
            {'name': 'expirycounter', 'value': 1, 'processInstanceId': 'i2', 'executionId': 'i2'}])
    session = FakeSession(handler)
    source = CamundaFeeSource('http://camunda/engine-rest/', lambda: 'token', session, page_size=2)
    result = {i['id']: i for i in source.fetch()}
    assert set(result) == {'i0', 'i1', 'i2'} and result['i2']['suspended'] and not result['i0']['suspended']
    assert [i['waiting'] for i in result.values()] == [True, False, True]
    assert result['i0']['variables'] == {'ministryRequestID': '41', 'formId': 'x' * 24}  # process scope wins
    assert all(call[4]['Authorization'] == 'Bearer token' for call in session.calls)


def test_camunda_failure_aborts_the_run_instead_of_reporting_partial_data():
    source = CamundaFeeSource('http://camunda', lambda: 't', FakeSession(lambda *a: FakeResponse(None, 500)))
    with pytest.raises(svc.BackfillSourceError, match='HTTP 500'):
        source.fetch()


def test_n8n_store_finds_the_table_by_name_pages_rows_and_unwraps_inserts():
    def handler(method, url_, body, params):
        if url_.endswith('/data-tables'):
            return FakeResponse({'data': [{'id': 'other', 'name': 'x'}, {'id': 'T1', 'name': 'foi-payment-sla'}]})
        if method == 'GET':
            f = json.loads(params['filter'])
            assert f == {'type': 'and', 'filters': [
                {'columnName': 'sla_type', 'condition': 'eq', 'value': 'payment-expiry'},
                {'columnName': 'ministry_request_id', 'condition': 'eq', 'value': '100'}]}
            if params.get('cursor'):
                return FakeResponse({'data': [{'id': 2}], 'nextCursor': None})
            return FakeResponse({'data': [{'id': 1}], 'nextCursor': 'c1'})
        if method == 'POST':
            assert body == {'data': [{'a': 1}], 'returnType': 'all'}
            return FakeResponse([{'id': 9, 'a': 1}])
        return FakeResponse(True)
    session = FakeSession(handler)
    store = N8NPaymentSlaStore('http://n8n/', 'key', session=session)
    assert [r['id'] for r in store.list_rows(100)] == [1, 2]
    assert store.insert({'a': 1}) == {'id': 9, 'a': 1}
    store.delete(9)
    assert session.calls[-1][0] == 'DELETE' and json.loads(session.calls[-1][3]['filter'])['filters'][0]['value'] == 9
    assert all(call[4]['X-N8N-API-KEY'] == 'key' for call in session.calls)
    assert any(c[1] == 'http://n8n/api/v1/data-tables/T1/rows' for c in session.calls)


def test_n8n_store_needs_credentials_and_exactly_one_table(monkeypatch):
    monkeypatch.delenv('N8N_API_KEY', raising=False)  # a developer's .env may define them
    monkeypatch.delenv('N8N_PAYMENT_SLA_TABLE_ID', raising=False)
    with pytest.raises(N8NStoreError, match='N8N_API_KEY'):
        N8NPaymentSlaStore('http://n8n', None, session=FakeSession(lambda *a: FakeResponse({}))).list_rows()
    ambiguous = FakeSession(lambda *a: FakeResponse({'data': []}))
    with pytest.raises(N8NStoreError, match='exactly one'):
        N8NPaymentSlaStore('http://n8n', 'k', session=ambiguous).list_rows()
    with pytest.raises(N8NStoreError, match='HTTP 401'):
        N8NPaymentSlaStore('http://n8n', 'k', session=FakeSession(lambda *a: FakeResponse(None, 401))).list_rows()


def test_foi_source_groups_active_payments_by_request_and_parses_their_ids():
    rows = [{'ministryrequestid': 100, 'paymentid': 1, 'version': 3, 'paymenturl': url(), 'paymentexpirydate':
             datetime(2030, 1, 10)},
            {'ministryrequestid': 100, 'paymentid': 2, 'version': 1, 'paymenturl': 'https://x.test/legacy',
             'paymentexpirydate': None}]
    grouped = FoiPaymentSource._group(rows)
    assert grouped[100][0] == {'paymentid': 1, 'form_id': FORM, 'submission_id': SUB, 'payment_url': url(),
                               'expiry': '2030-01-10'}
    assert grouped[100][1]['form_id'] is None and grouped[100][1]['expiry'] == ''
    assert 'createdby <> \'System_Cancel\'' in FoiPaymentSource.ACTIVE_SQL  # same rule as getactivepayment
    assert 'paidamount IS NULL' in FoiPaymentSource.ACTIVE_SQL


# --- plan hash: an apply is tied to the dry run that was reviewed -----------------------------------------------

def trio():
    """Three independent unpaid payments (ministry requests 101 to 103)."""
    return [instance('p%d' % n, ministry=100 + n, foi=10 + n, sub='%024x' % n) for n in (1, 2, 3)]


def plan_hash(instances, **kwargs):
    return backfill(instances, **kwargs)[0]['run']['plan_hash']


def test_plan_hash_is_16_hex_characters_and_is_in_the_summary_text():
    report, _ = backfill(trio())
    plan = report['run']['plan_hash']
    assert re.fullmatch(r'[0-9a-f]{16}', plan)
    assert 'Plan hash: %s' % plan in format_summary(report)
    assert '--apply --confirm-plan %s' % plan in format_summary(report)


def test_plan_hash_is_the_same_for_every_run_of_the_same_plan():
    items = trio()
    other_run = PaymentSlaBackfill(FakeCamunda(*items), agreeing_foi(items), FakeStore(), run_id='another-run',
                                   operator='someone', clock=lambda: datetime(2027, 1, 1, tzinfo=timezone.utc)).run()
    assert plan_hash(items) == other_run['run']['plan_hash'] == plan_hash(list(reversed(items)))


def test_plan_hash_is_the_same_in_a_dry_run_and_an_apply():
    assert backfill(trio())[0]['run']['plan_hash'] == backfill(trio(), apply=True)[0]['run']['plan_hash']


def test_plan_hash_changes_when_the_planned_rows_change():
    base = plan_hash(trio())
    assert plan_hash(trio()[:2]) != base                                       # a row fewer
    assert plan_hash(trio() + [instance('p4', 104, sub='%024x' % 4)]) != base  # a row more
    moved = trio()
    moved[1] = instance('p2', 102, foi=12, sub='%024x' % 2, expiry='2030-01-09')
    assert plan_hash(moved) != base                                            # another deadline


def test_plan_hash_ignores_records_that_write_nothing():
    paid = instance('p9', 109, sub='%024x' % 9, status='PAID')
    assert plan_hash(trio() + [paid]) == plan_hash(trio())


def test_include_expired_adds_the_expired_row_to_the_plan():
    items = trio() + [instance('p4', 104, sub='%024x' % 4, expiry='2023-01-10', counter=1)]
    assert plan_hash(items) != plan_hash(items, include_expired=True)


def test_an_empty_plan_still_has_a_hash():
    assert re.fullmatch(r'[0-9a-f]{16}', plan_hash([]))


def test_apply_with_the_reviewed_plan_hash_writes_the_rows():
    items = trio()
    report, store = backfill(items, apply=True, confirm_plan=plan_hash(items))
    assert store.insert_calls == 3 and report['summary']['sla_rows_created'] == 3
    assert report['run']['mode'] == 'apply'


def test_apply_accepts_the_hash_in_upper_case_with_spaces():
    items = trio()
    _, store = backfill(items, apply=True, confirm_plan='  %s ' % plan_hash(items).upper())
    assert store.insert_calls == 3


def test_apply_refuses_and_writes_nothing_when_the_plan_changed_since_the_review():
    reviewed = plan_hash(trio()[:2])
    store = FakeStore()
    with pytest.raises(PlanChangedError) as raised:  # a third payment appeared after the review
        backfill(trio(), apply=True, confirm_plan=reviewed, store=store)
    assert store.insert_calls == 0 and store.rows == []
    assert raised.value.expected == reviewed
    new_plan = raised.value.report
    assert new_plan['run']['mode'] == 'dry-run' and new_plan['run']['plan_hash'] != reviewed
    assert new_plan['summary']['sla_rows_would_be_created'] == 3 and new_plan['summary']['errors'] == 0


def test_the_report_of_a_refused_apply_can_be_confirmed_in_turn():
    with pytest.raises(PlanChangedError) as raised:
        backfill(trio(), apply=True, confirm_plan=plan_hash(trio()[:1]))
    _, store = backfill(trio(), apply=True, confirm_plan=raised.value.report['run']['plan_hash'])
    assert store.insert_calls == 3


def test_a_wrong_hash_never_writes_even_when_the_plan_is_empty():
    with pytest.raises(PlanChangedError):
        backfill([], apply=True, confirm_plan='0' * 16)


def test_a_dry_run_ignores_a_confirm_plan():
    report, store = backfill(trio(), confirm_plan='0' * 16)
    assert store.insert_calls == 0 and report['run']['mode'] == 'dry-run'


def test_apply_without_a_plan_hash_still_works_for_library_callers():
    assert backfill(trio(), apply=True)[1].insert_calls == 3


def test_a_second_apply_after_the_rows_exist_is_a_changed_plan_and_writes_nothing():
    items = trio()
    reviewed = plan_hash(items)
    _, store = backfill(items, apply=True, confirm_plan=reviewed)
    with pytest.raises(PlanChangedError):
        backfill(items, apply=True, confirm_plan=reviewed, store=store)
    assert store.insert_calls == 3


# --- CSV for review in Excel -------------------------------------------------------------------------------------

def test_report_csv_text_has_a_bom_a_header_and_one_line_per_record():
    report, _ = backfill([instance('p1', 100), instance('p2', 101, sub=SUB2, status='PAID')])
    text = report_csv_text(report)
    assert text.startswith('﻿') and not report_csv_text(report, bom=False).startswith('﻿')
    rows = list(csv.DictReader(text.lstrip('﻿').splitlines()))
    assert [r['process_instance_id'] for r in rows] == ['p1', 'p2']
    assert rows[0]['outcome'] == CREATE and rows[1]['reason'] == 'camunda_payment_paid'


def test_report_csv_holds_no_form_ids_or_payment_urls():
    text = report_csv_text(backfill([instance()])[0])
    assert 'example.test' not in text and FORM not in text and SUB not in text


# --- CLI: --confirm-plan, exit code 4, files ----------------------------------------------------------------------

def test_cli_apply_needs_a_confirm_plan():
    with pytest.raises(SystemExit):
        cli.parse_args(['--apply'])


def test_cli_confirm_plan_needs_apply():
    with pytest.raises(SystemExit):
        cli.parse_args(['--confirm-plan', '0123456789abcdef'])


@pytest.mark.parametrize('value', ['', 'abc', 'zzzzzzzzzzzzzzzz', '0123456789abcdef0'])
def test_cli_rejects_a_malformed_plan_hash(value):
    with pytest.raises(SystemExit):
        cli.parse_args(['--apply', '--confirm-plan', value])


def test_cli_accepts_apply_with_a_plan_hash_in_either_case():
    assert cli.parse_args(['--apply', '--confirm-plan', '0123456789ABCDEF']).confirm_plan == '0123456789ABCDEF'


def patch_cli_sources(monkeypatch, instances, store):
    foi = agreeing_foi(instances)
    monkeypatch.setattr(cli, 'CamundaFeeSource', lambda: FakeCamunda(*instances))
    monkeypatch.setattr(cli, 'FoiPaymentSource', lambda: foi)
    monkeypatch.setattr(cli, 'N8NPaymentSlaStore', lambda: store)
    return foi


def test_cli_dry_run_writes_the_json_and_an_excel_readable_csv(monkeypatch, tmp_path, capsys):
    store = FakeStore()
    patch_cli_sources(monkeypatch, trio(), store)
    json_path, csv_path = tmp_path / 'out.json', tmp_path / 'out.csv'
    assert cli.main(['--report-file', str(json_path), '--report-csv', str(csv_path), '--strict']) == 0
    report = json.loads(json_path.read_text(encoding='utf-8'))
    assert store.insert_calls == 0 and csv_path.read_bytes().startswith(b'\xef\xbb\xbf')
    assert len(list(csv.DictReader(csv_path.read_text(encoding='utf-8-sig').splitlines()))) == 3
    assert 'Plan hash: %s' % report['run']['plan_hash'] in capsys.readouterr().out


def test_cli_apply_with_the_reviewed_hash_writes(monkeypatch, tmp_path):
    store = FakeStore()
    foi = patch_cli_sources(monkeypatch, trio(), store)
    cli.main(['--report-file', str(tmp_path / 'dry.json')])
    reviewed = json.loads((tmp_path / 'dry.json').read_text(encoding='utf-8'))['run']['plan_hash']
    assert cli.main(['--apply', '--confirm-plan', reviewed, '--report-file', str(tmp_path / 'apply.json')]) == 0
    assert store.insert_calls == 3 and foi.closed


def test_cli_apply_with_a_stale_hash_exits_4_writes_nothing_and_reports_the_new_plan(monkeypatch, tmp_path, capsys):
    store = FakeStore()
    patch_cli_sources(monkeypatch, trio(), store)
    stale = '0' * 16
    code = cli.main(['--apply', '--confirm-plan', stale, '--report-file', str(tmp_path / 'new.json'),
                     '--report-csv', str(tmp_path / 'new.csv')])
    new_plan = json.loads((tmp_path / 'new.json').read_text(encoding='utf-8'))
    assert code == cli.EXIT_PLAN_CHANGED == 4 and store.insert_calls == 0
    assert new_plan['run']['mode'] == 'dry-run' and new_plan['run']['plan_hash'] != stale
    assert (tmp_path / 'new.csv').exists() and 'Nothing was written' in capsys.readouterr().err


# --- endpoints: request handling ---------------------------------------------------------------------------------

def test_enabled_only_when_the_variable_is_true(monkeypatch):
    monkeypatch.delenv(backfillapi.ENABLED_VARIABLE, raising=False)
    assert backfillapi.enabled() is False
    for value, expected in (('true', True), (' TRUE ', True), ('false', False), ('1', False), ('', False)):
        monkeypatch.setenv(backfillapi.ENABLED_VARIABLE, value)
        assert backfillapi.enabled() is expected


def test_parse_options_defaults_for_an_empty_dry_run_body():
    for body in (None, {}):
        assert backfillapi.parse_options(body, apply=False) == (
            {'include_expired': False, 'ministry_request_ids': []}, None)


def test_parse_options_normalises_the_request_ids():
    options, error = backfillapi.parse_options({'include_expired': True, 'ministry_request_ids': [5, 3, 5]}, apply=False)
    assert error is None and options == {'include_expired': True, 'ministry_request_ids': [3, 5]}


@pytest.mark.parametrize('body', [
    [], 'x', {'include_expired': 'true'}, {'include_expired': 1}, {'ministry_request_ids': 5},
    {'ministry_request_ids': ['5']}, {'ministry_request_ids': [True]}, {'ministry_request_ids': [0]},
    {'ministry_request_ids': [-1]}, {'ministry_request_ids': list(range(1, 502))}, {'report_file': 'x.json'},
    {'plan_hash': '0123456789abcdef'},  # a dry run takes no plan hash
])
def test_parse_options_rejects_bad_dry_run_bodies(body):
    options, error = backfillapi.parse_options(body, apply=False)
    assert options is None and error


@pytest.mark.parametrize('plan', [None, '', 123, 'abc', 'g' * 16, '0' * 17, ['0' * 16]])
def test_parse_options_requires_a_valid_plan_hash_to_apply(plan):
    options, error = backfillapi.parse_options({} if plan is None else {'plan_hash': plan}, apply=True)
    assert options is None and 'plan_hash' in error


def test_parse_options_normalises_the_plan_hash_to_apply():
    options, error = backfillapi.parse_options({'plan_hash': ' 0123456789ABCDEF '}, apply=True)
    assert error is None and options['plan_hash'] == '0123456789abcdef'


def run_endpoint(instances, apply, store=None, camunda=None, **body):
    options, error = backfillapi.parse_options(body, apply)
    assert error is None, error
    store = store if store is not None else FakeStore()
    foi = agreeing_foi(instances)
    status, payload, report = backfillapi.execute(options, apply, 'tester', camunda=camunda or FakeCamunda(*instances),
                                                  foi=foi, store=store)
    return status, payload, report, store, foi


def test_endpoint_dry_run_returns_the_report_and_the_plan_hash_and_writes_nothing():
    status, payload, report, store, foi = run_endpoint(trio(), apply=False)
    assert status == 200 and payload['status'] is True and payload['applied'] is False
    assert payload['plan_hash'] == report['run']['plan_hash'] and store.insert_calls == 0
    assert report['run']['operator'] == 'tester'
    assert foi.closed is False  # an injected source is the caller's to close
    json.dumps(payload)  # must be serialisable as is


def test_endpoint_apply_with_the_reviewed_hash_writes_and_returns_the_report():
    reviewed = run_endpoint(trio(), apply=False)[1]['plan_hash']
    status, payload, report, store, _ = run_endpoint(trio(), apply=True, plan_hash=reviewed)
    assert status == 200 and payload['applied'] is True and store.insert_calls == 3
    assert report['summary']['sla_rows_created'] == 3


def test_endpoint_apply_with_a_stale_hash_is_a_409_with_the_new_plan_and_no_writes():
    reviewed = run_endpoint(trio()[:1], apply=False)[1]['plan_hash']
    status, payload, report, store, _ = run_endpoint(trio(), apply=True, plan_hash=reviewed)
    assert status == 409 and payload['status'] is False and store.insert_calls == 0
    assert payload['expected_plan_hash'] == reviewed and payload['plan_hash'] != reviewed
    assert payload['summary']['sla_rows_would_be_created'] == 3 and report['run']['mode'] == 'dry-run'
    json.dumps(payload)


def test_endpoint_scopes_to_the_requested_ministry_requests():
    status, _, report, _, _ = run_endpoint(trio(), apply=False, ministry_request_ids=[101])
    assert status == 200 and report['summary']['sla_rows_would_be_created'] == 1


def test_endpoint_reports_a_failed_source_as_502_without_writing():
    class Broken(FakeCamunda):
        def fetch(self):
            raise BackfillSourceError('Camunda /process-instance answered HTTP 503')

    status, payload, report, store, _ = run_endpoint(trio(), apply=False, camunda=Broken())
    assert status == 502 and report is None and 'HTTP 503' in payload['message'] and store.insert_calls == 0


def test_endpoint_flags_write_errors_in_the_status_field():
    reviewed = run_endpoint(trio()[:1], apply=False)[1]['plan_hash']
    store = FakeStore()
    store.fail_inserts = 1
    status, payload, report, _, _ = run_endpoint(trio()[:1], apply=True, store=store, plan_hash=reviewed)
    assert status == 200 and payload['status'] is False and report['summary']['errors'] == 1


def test_endpoint_payload_never_carries_credentials_or_payment_urls():
    items = [instance(accessToken='SECRET-TOKEN', formioRootPassword='SECRET-PASSWORD')]
    text = json.dumps(run_endpoint(items, apply=False)[1])
    assert 'SECRET' not in text and 'example.test' not in text


# --- endpoints: the foiworkflow resource -------------------------------------------------------------------------

@pytest.fixture
def workflow_resource(monkeypatch):
    try:
        from request_api.resources import foiworkflow  # pylint: disable=import-outside-toplevel
    except Exception as exc:  # pylint: disable=broad-except  # the full app stack (e.g. WeasyPrint) may not load here
        pytest.skip('resource module cannot be imported in this environment: %s' % type(exc).__name__)
    from flask import Flask  # pylint: disable=import-outside-toplevel
    monkeypatch.setattr(foiworkflow.AuthHelper, 'getuserid', staticmethod(lambda: 'admin-user'))
    monkeypatch.setenv(backfillapi.ENABLED_VARIABLE, 'true')
    app = Flask(__name__)

    def call(apply, body, query=''):
        with app.test_request_context('/x' + query, method='POST', json=body):
            return foiworkflow._runpaymentslabackfill(apply)  # pylint: disable=protected-access
    return call


def test_resource_is_a_404_while_the_tool_is_switched_off(workflow_resource, monkeypatch):
    monkeypatch.setenv(backfillapi.ENABLED_VARIABLE, 'false')
    monkeypatch.setattr(backfillapi, 'execute', lambda *a, **k: pytest.fail('must not run while switched off'))
    response = workflow_resource(False, {})
    assert response.status_code == 404 and response.headers['Cache-Control'] == 'no-store'


def test_resource_rejects_a_bad_body_with_400(workflow_resource, monkeypatch):
    monkeypatch.setattr(backfillapi, 'execute', lambda *a, **k: pytest.fail('must not run on a bad body'))
    response = workflow_resource(True, {})
    assert response.status_code == 400 and 'plan_hash' in json.loads(response.get_data())['message']


def test_resource_serves_the_csv_with_the_plan_hash_header(workflow_resource, monkeypatch):
    calls = []
    report = backfill(trio())[0]
    monkeypatch.setattr(backfillapi, 'execute', lambda options, apply, operator: calls.append((apply, operator)) or (
        200, {}, report))
    response = workflow_resource(False, {}, '?format=csv')
    assert calls == [(False, 'admin-user')]
    assert response.status_code == 200 and response.mimetype == 'text/csv'
    assert response.headers['Cache-Control'] == 'no-store' and response.headers['X-Plan-Hash'] == report['run']['plan_hash']
    assert response.headers['Content-Disposition'].startswith('attachment; filename=payment_sla_backfill_dry-run_')
    assert response.get_data().startswith(b'\xef\xbb\xbf')


def test_resource_returns_json_and_passes_the_409_through(workflow_resource, monkeypatch):
    monkeypatch.setattr(backfillapi, 'execute', lambda options, apply, operator: (409, {'status': False}, None))
    response = workflow_resource(True, {'plan_hash': '0' * 16})
    assert response.status_code == 409 and json.loads(response.get_data()) == {'status': False}
    assert response.headers['Cache-Control'] == 'no-store'
