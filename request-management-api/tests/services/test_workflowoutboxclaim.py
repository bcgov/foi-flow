import importlib
import pkgutil
from datetime import datetime, timedelta

import pytest
from flask import Flask
from sqlalchemy import event

import request_api.models as _models
from request_api.models.db import db
from request_api.models.FOIWorkflowEventOutbox import FOIWorkflowEventOutbox, OutboxStatus
from request_api.services.workflowoutboxservice import AckResult, ClaimDecision, workflowoutboxservice

"""
Behaviour tests for the outbox claim (idempotency, in-flight protection and ordering that FOI Request
Routing used to keep in the n8n foi-process-audit table; the ordering watermark is the stateoccurredat of the outbox
rows themselves), the execution lookup used by the error handler,
and retention. In-memory SQLite, like test_workflowoutboxservice.py.
"""

for _module in pkgutil.iter_modules(_models.__path__):
    try:
        importlib.import_module("request_api.models." + _module.name)
    except Exception:  # pragma: no cover - an unrelated model that cannot import here
        pass

NOW = datetime(2040, 1, 1, 12, 0, 0)
STATE = "state"
RAW = "raw_request_id"
MINISTRY = "ministry_request_id"


def _bind_sqlite_savepoints(engine):
    @event.listens_for(engine, "connect")
    def _connect(dbapi_connection, _):
        dbapi_connection.isolation_level = None

    @event.listens_for(engine, "begin")
    def _begin(conn):
        conn.exec_driver_sql("BEGIN")


@pytest.fixture(autouse=True)
def _env(monkeypatch):
    for name in ("N8N_OUTBOX_CLAIM_LEASE_MINUTES", "N8N_OUTBOX_NO_OUTCOME_MINUTES"):
        monkeypatch.delenv(name, raising=False)


@pytest.fixture
def app():
    flask_app = Flask(__name__)
    flask_app.config.update(SQLALCHEMY_DATABASE_URI="sqlite://", SQLALCHEMY_TRACK_MODIFICATIONS=False)
    db.init_app(flask_app)
    with flask_app.app_context():
        _bind_sqlite_savepoints(db.engine)
        FOIWorkflowEventOutbox.__table__.create(db.engine)
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def service(app):
    return workflowoutboxservice()


def _occurred(second, micro=0):
    return "2040-01-01T12:00:%02d.%06d+00:00" % (second, micro)


def _eventid(n):
    return "00000000-0000-4000-8000-%012d" % n


def _enqueue(service, n, status=OutboxStatus.delivered.value, event="foi-ministry-complete", **fields):
    service.enqueue({"event": event, "event_id": _eventid(n), "occurred_at": _occurred(n), "foiRequestMetaData": "{}"})
    row = FOIWorkflowEventOutbox.getbyeventid(_eventid(n))
    row.status = status
    for key, value in fields.items():
        setattr(row, key, value)
    db.session.commit()
    return row


def _claim(service, n, execution="100", kind=STATE, scope=MINISTRY, key="5265", at=None, now=NOW, **ids):
    return service.claim(_eventid(n), execution, kind=kind, scope=scope, scopekey=key,
                         occurredat=at or _occurred(n), requestids=ids, now=now)


def _watermark(scope, key):
    """The ordering watermark: the newest state event allowed to run for the request."""
    return FOIWorkflowEventOutbox.neweststateoccurredat(scope, key, None)


# --- duplicate and in-flight protection -----------------------------------------------------------

def test_a_new_event_proceeds_and_records_the_claim_and_request_ids(service):
    _enqueue(service, 1)
    decision = _claim(service, 1, execution="2035", rawrequestid=4858, foirequestid=4255, ministryrequestid=5265,
                      status="Fee Estimate")
    row = FOIWorkflowEventOutbox.getbyeventid(_eventid(1))
    assert decision == ClaimDecision.proceed
    assert (row.n8nexecutionid, row.claimedat) == ("2035", NOW)
    assert (row.rawrequestid, row.foirequestid, row.ministryrequestid, row.requeststatus) == ("4858", "4255", "5265", "Fee Estimate")
    assert row.stateoccurredat == datetime(2040, 1, 1, 12, 0, 1)


def test_the_scope_key_is_recorded_on_the_row_even_when_the_request_ids_omit_it(service):
    _enqueue(service, 1)
    assert _claim(service, 1, scope=RAW, key="4858") == ClaimDecision.proceed
    assert FOIWorkflowEventOutbox.getbyeventid(_eventid(1)).rawrequestid == "4858"


def test_a_completed_event_is_a_duplicate_and_nothing_changes(service):
    _enqueue(service, 1, status=OutboxStatus.completed.value)
    assert _claim(service, 1) == ClaimDecision.duplicate
    row = FOIWorkflowEventOutbox.getbyeventid(_eventid(1))
    assert row.claimedat is None
    assert row.stateoccurredat is None
    assert _watermark(MINISTRY, "5265") is None


def test_a_second_execution_is_told_in_progress_while_the_first_holds_the_claim(service):
    _enqueue(service, 1)
    assert _claim(service, 1, execution="100") == ClaimDecision.proceed
    assert _claim(service, 1, execution="101", now=NOW + timedelta(minutes=5)) == ClaimDecision.inprogress
    assert FOIWorkflowEventOutbox.getbyeventid(_eventid(1)).n8nexecutionid == "100"


def test_the_same_execution_may_claim_again(service):
    _enqueue(service, 1)
    assert _claim(service, 1, execution="100") == ClaimDecision.proceed
    assert _claim(service, 1, execution="100", now=NOW + timedelta(minutes=1)) == ClaimDecision.proceed


def test_an_expired_claim_can_be_taken_over(service):
    _enqueue(service, 1)
    assert _claim(service, 1, execution="100") == ClaimDecision.proceed
    assert _claim(service, 1, execution="101", now=NOW + timedelta(minutes=31)) == ClaimDecision.proceed
    assert FOIWorkflowEventOutbox.getbyeventid(_eventid(1)).n8nexecutionid == "101"


def test_the_lease_comes_from_the_environment(service, monkeypatch):
    monkeypatch.setenv("N8N_OUTBOX_CLAIM_LEASE_MINUTES", "2")
    _enqueue(service, 1)
    short = workflowoutboxservice()
    assert _claim(short, 1, execution="100") == ClaimDecision.proceed
    assert _claim(short, 1, execution="101", now=NOW + timedelta(minutes=3)) == ClaimDecision.proceed


def test_acknowledging_releases_the_claim_so_a_failed_event_can_run_again(service):
    _enqueue(service, 1)
    _claim(service, 1, execution="100")
    result, _ = service.acknowledge(_eventid(1), "FAILED", error="boom", executionid="100", now=NOW)
    assert result == AckResult.updated
    assert FOIWorkflowEventOutbox.getbyeventid(_eventid(1)).claimedat is None
    service.replay(_eventid(1), now=NOW)
    assert _claim(service, 1, execution="102") == ClaimDecision.proceed


def test_replay_releases_a_claim(service):
    _enqueue(service, 1, status=OutboxStatus.failed.value, claimedat=NOW, n8nexecutionid="100")
    service.replay(_eventid(1), now=NOW)
    assert FOIWorkflowEventOutbox.getbyeventid(_eventid(1)).claimedat is None


def test_an_event_without_an_outbox_row_is_still_order_checked_but_not_claimed(service):
    assert _claim(service, 9, at=_occurred(5)) == ClaimDecision.proceed
    assert FOIWorkflowEventOutbox.query.count() == 0


# --- ordering -------------------------------------------------------------------------------------

def test_a_state_event_older_than_one_already_applied_is_stale(service):
    _enqueue(service, 1)
    _enqueue(service, 2)
    assert _claim(service, 2, execution="200", at=_occurred(20)) == ClaimDecision.proceed
    assert _claim(service, 1, execution="201", at=_occurred(10)) == ClaimDecision.stale
    assert _watermark(MINISTRY, "5265") == datetime(2040, 1, 1, 12, 0, 20)
    stale = FOIWorkflowEventOutbox.getbyeventid(_eventid(1))
    assert stale.claimedat is None
    assert stale.stateoccurredat is None  # a stale event is not claimed and moves nothing


def test_an_equal_timestamp_runs_so_a_replay_of_the_same_event_works(service):
    _enqueue(service, 1)
    assert _claim(service, 1, execution="100", at=_occurred(7)) == ClaimDecision.proceed
    service.acknowledge(_eventid(1), "FAILED", error="x", now=NOW)
    service.replay(_eventid(1), now=NOW)
    assert _claim(service, 1, execution="101", at=_occurred(7)) == ClaimDecision.proceed


def test_microsecond_ordering_is_kept(service):
    _enqueue(service, 1)
    _enqueue(service, 2)
    assert _claim(service, 2, execution="200", at=_occurred(5, 500)) == ClaimDecision.proceed
    assert _claim(service, 1, execution="201", at=_occurred(5, 499)) == ClaimDecision.stale


def test_action_events_are_never_order_checked_and_do_not_move_a_watermark(service):
    _enqueue(service, 1, event="foi-manage-payment")
    _enqueue(service, 2)
    assert _claim(service, 2, execution="200", at=_occurred(30)) == ClaimDecision.proceed
    assert _claim(service, 1, execution="201", kind="action", at=_occurred(1)) == ClaimDecision.proceed
    assert _watermark(MINISTRY, "5265") == datetime(2040, 1, 1, 12, 0, 30)
    assert FOIWorkflowEventOutbox.getbyeventid(_eventid(1)).stateoccurredat is None


def test_a_state_event_without_occurred_at_or_key_is_processed_without_an_order_check(service):
    _enqueue(service, 1)
    _enqueue(service, 2)
    assert service.claim(_eventid(1), "100", kind=STATE, scope=MINISTRY, scopekey="5265", occurredat=None, now=NOW) == ClaimDecision.proceed
    assert service.claim(_eventid(2), "101", kind=STATE, scope=MINISTRY, scopekey=None, occurredat=_occurred(2), now=NOW) == ClaimDecision.proceed
    assert _watermark(MINISTRY, "5265") is None


def test_different_ministry_requests_do_not_make_each_other_stale(service):
    _enqueue(service, 1)
    _enqueue(service, 2)
    assert _claim(service, 2, execution="200", key="6000", at=_occurred(20)) == ClaimDecision.proceed
    assert _claim(service, 1, execution="201", key="5265", at=_occurred(10)) == ClaimDecision.proceed


def test_a_ministry_event_also_counts_for_its_raw_request_so_a_late_intake_event_is_stale(service):
    _enqueue(service, 1, event="foi-iao-open-complete")
    _enqueue(service, 2, event="foi-intake-complete")
    assert _claim(service, 1, execution="100", at=_occurred(20), rawrequestid=4858) == ClaimDecision.proceed
    late_intake = _claim(service, 2, execution="101", scope=RAW, key="4858", at=_occurred(10))
    assert late_intake == ClaimDecision.stale


def test_an_intake_event_does_not_make_a_ministry_event_stale(service):
    _enqueue(service, 1)
    _enqueue(service, 2)
    assert _claim(service, 2, execution="200", scope=RAW, key="4858", at=_occurred(30)) == ClaimDecision.proceed
    assert _claim(service, 1, execution="201", at=_occurred(10), rawrequestid=4858) == ClaimDecision.proceed


def test_the_watermark_is_the_newest_value_and_an_older_event_does_not_lower_it(service):
    _enqueue(service, 1)
    _enqueue(service, 2)
    _claim(service, 2, execution="200", scope=RAW, key="4858", at=_occurred(30))
    assert _claim(service, 1, execution="201", at=_occurred(10), rawrequestid=4858) == ClaimDecision.proceed
    assert _watermark(RAW, "4858") == datetime(2040, 1, 1, 12, 0, 30)


def test_a_duplicate_does_not_move_a_watermark(service):
    _enqueue(service, 1, status=OutboxStatus.completed.value)
    _claim(service, 1, at=_occurred(50))
    assert _watermark(MINISTRY, "5265") is None


def test_a_failed_newer_event_still_holds_the_watermark_until_it_is_replayed(service):
    _enqueue(service, 1)
    _enqueue(service, 2)
    assert _claim(service, 2, execution="200", at=_occurred(20)) == ClaimDecision.proceed
    service.acknowledge(_eventid(2), "FAILED", error="boom", now=NOW)
    assert _claim(service, 1, execution="201", at=_occurred(10)) == ClaimDecision.stale


def test_an_event_does_not_order_against_itself_on_replay(service):
    _enqueue(service, 1)
    assert _claim(service, 1, execution="100", at=_occurred(20)) == ClaimDecision.proceed
    service.acknowledge(_eventid(1), "FAILED", error="boom", now=NOW)
    service.replay(_eventid(1), now=NOW)
    assert _claim(service, 1, execution="101", at=_occurred(20)) == ClaimDecision.proceed


def test_scrubbed_rows_still_order_events_and_the_purge_removes_the_watermark_with_the_row(service):
    _enqueue(service, 1, status=OutboxStatus.completed.value, completedat=NOW - timedelta(days=100),
             ministryrequestid="5265", stateoccurredat=datetime(2040, 1, 1, 12, 0, 20))
    _enqueue(service, 2)
    assert service.scrubpayloads(90, now=NOW) == 1
    assert _claim(service, 2, execution="100", at=_occurred(10)) == ClaimDecision.stale
    assert service.purgecompleted(90, now=NOW) == 1
    assert _watermark(MINISTRY, "5265") is None


@pytest.mark.parametrize("kwargs", [
    {"kind": "bogus"},
    {"scope": "bogus_scope"},
    {"at": "2040-01-01T12:00:00+00:00"},      # no microseconds
    {"at": "2040-01-01T12:00:00.000001Z"},    # not +00:00
])
def test_bad_input_is_a_value_error_and_changes_nothing(service, kwargs):
    _enqueue(service, 1)
    with pytest.raises(ValueError):
        _claim(service, 1, **kwargs)
    assert FOIWorkflowEventOutbox.getbyeventid(_eventid(1)).claimedat is None
    assert FOIWorkflowEventOutbox.getbyeventid(_eventid(1)).stateoccurredat is None


# --- execution lookup (error handler) -------------------------------------------------------------

def test_a_failed_execution_is_mapped_back_to_its_event_without_the_payload(service):
    _enqueue(service, 1)
    _claim(service, 1, execution="2035", rawrequestid=4858, foirequestid=4255, ministryrequestid=5265, status="Fee Estimate")
    found = service.findbyexecution("2035")
    assert found == {"event_id": _eventid(1), "event": "foi-ministry-complete", "raw_request_id": "4858",
                     "foi_request_id": "4255", "ministry_request_id": "5265", "status": "Fee Estimate",
                     "outbox_status": "DELIVERED"}
    assert service.findbyexecution("9999") is None


def test_the_listing_shows_the_request_ids_and_never_the_payload(service):
    _enqueue(service, 1, status=OutboxStatus.failed.value)
    FOIWorkflowEventOutbox.getbyeventid(_eventid(1)).ministryrequestid = "5265"
    db.session.commit()
    listed = service.listevents()[0]
    assert listed["ministryrequestid"] == "5265"
    assert "payload" not in listed


# --- retention ------------------------------------------------------------------------------------

def _completed(service, n, days_ago):
    return _enqueue(service, n, status=OutboxStatus.completed.value, completedat=NOW - timedelta(days=days_ago))


def test_scrub_removes_the_event_from_old_completed_payloads_only(service):
    _completed(service, 1, 100)
    _completed(service, 2, 10)
    _enqueue(service, 3, status=OutboxStatus.failed.value, completedat=None)
    assert service.scrubpayloads(90, now=NOW) == 1
    old, recent, failed = (FOIWorkflowEventOutbox.getbyeventid(_eventid(n)) for n in (1, 2, 3))
    assert old.payload == {"event_id": _eventid(1), "event": "foi-ministry-complete", "scrubbed": True}
    assert old.payloadscrubbedat == NOW
    assert old.status == "COMPLETED"
    assert recent.payload["foiRequestMetaData"] == "{}"
    assert failed.payload["foiRequestMetaData"] == "{}"
    assert service.scrubpayloads(90, now=NOW) == 0  # already scrubbed rows are not picked up again


def test_scrub_works_in_batches(service):
    for n in (1, 2, 3):
        _completed(service, n, 200)
    assert service.scrubpayloads(90, batchsize=2, now=NOW) == 2
    assert service.scrubpayloads(90, batchsize=2, now=NOW) == 1


def test_purge_deletes_old_completed_rows_but_never_dead_or_failed(service):
    _completed(service, 1, 400)
    _completed(service, 2, 30)
    _enqueue(service, 3, status=OutboxStatus.dead.value, completedat=None)
    _enqueue(service, 4, status=OutboxStatus.failed.value, completedat=None)
    assert service.purgecompleted(365, now=NOW) == 1
    remaining = {row.eventid for row in FOIWorkflowEventOutbox.query.all()}
    assert remaining == {_eventid(2), _eventid(3), _eventid(4)}
