import importlib
import os
import pkgutil
import threading
from datetime import datetime, timedelta

import pytest
from flask import Flask
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError

import request_api.models as _models
from request_api.models.db import db
from request_api.models.FOIWorkflowEventOutbox import FOIWorkflowEventOutbox, OutboxStatus
from request_api.services.external.commonworkflowservice import n8ndeliveryresult
from request_api.services.workflowoutboxservice import AckResult, workflowoutboxservice

"""
Behaviour tests on in-memory SQLite (state machine, backoff, leases, atomicity with the
caller's session). FOR UPDATE SKIP LOCKED does not exist on SQLite, so real two-connection
concurrency is covered by test_skip_locked_* at the bottom, which needs a scratch Postgres:
    OUTBOX_TEST_POSTGRES_URL=postgresql://user:pass@host:5432/scratchdb pytest tests/services/test_workflowoutboxservice.py
"""

# SQLAlchemy's mapper registry needs every model referenced by a relationship to be loaded
for _module in pkgutil.iter_modules(_models.__path__):
    try:
        importlib.import_module("request_api.models." + _module.name)
    except Exception:  # pragma: no cover - an unrelated model that cannot import here
        pass

NOW = datetime(2040, 1, 1, 12, 0, 0)  # after any real "now", so freshly enqueued rows are due
OK = n8ndeliveryresult(True)
RETRYABLE = n8ndeliveryresult(False, retryable=True, error="HTTP 503")
FATAL = n8ndeliveryresult(False, retryable=False, error="HTTP 400")


class RequestChange(db.Model):
    """Stands in for the request row the caller changes in the same transaction."""
    __tablename__ = "OutboxTestRequestChange"
    id = db.Column(db.Integer, primary_key=True)
    note = db.Column(db.String(50))


def _bind_sqlite_savepoints(engine):
    # documented pysqlite workaround so SAVEPOINT (begin_nested) behaves like Postgres
    @event.listens_for(engine, "connect")
    def _connect(dbapi_connection, _):
        dbapi_connection.isolation_level = None

    @event.listens_for(engine, "begin")
    def _begin(conn):
        conn.execute("BEGIN")


@pytest.fixture(autouse=True)
def _retry_env(monkeypatch):
    for name in ("N8N_WEBHOOK_RETRY_MAX_ATTEMPTS", "N8N_WEBHOOK_RETRY_BACKOFF_SECONDS",
                 "N8N_WEBHOOK_RETRY_MAX_BACKOFF_SECONDS", "N8N_WEBHOOK_TIMEOUT_SECONDS"):
        monkeypatch.delenv(name, raising=False)


@pytest.fixture(autouse=True)
def _no_jitter(monkeypatch):
    """Pins the jitter to its upper bound so the backoff assertions stay exact."""
    monkeypatch.setattr("request_api.services.workflowoutboxservice.random.uniform", lambda low, high: high)


@pytest.fixture
def app():
    flask_app = Flask(__name__)
    flask_app.config.update(SQLALCHEMY_DATABASE_URI="sqlite://", SQLALCHEMY_TRACK_MODIFICATIONS=False)
    db.init_app(flask_app)
    with flask_app.app_context():
        _bind_sqlite_savepoints(db.engine)
        FOIWorkflowEventOutbox.__table__.create(db.engine)
        RequestChange.__table__.create(db.engine)
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def service(app):
    return workflowoutboxservice()


def _payload(n=1, event="foi-iao-complete"):
    return {"event": event, "event_id": "00000000-0000-4000-8000-%012d" % n, "foiRequestMetaData": "{}"}


def _row(n=1):
    return FOIWorkflowEventOutbox.getbyeventid(_payload(n)["event_id"])


def _seed(service, n=1, status=OutboxStatus.pending.value, **fields):
    service.enqueue(_payload(n))
    row = _row(n)
    row.status = status
    for key, value in fields.items():
        setattr(row, key, value)
    db.session.commit()
    return row


def _dispatch(service, deliver, now=NOW, batch=10):
    return service.dispatch_due(deliver, batchsize=batch, now=now)


# --- enqueue: atomic with the caller's session ---------------------------------------------------

def test_enqueue_stores_a_pending_row_with_the_event_id_and_payload(service):
    service.enqueue(_payload(1))
    row = _row(1)
    assert (row.status, row.attempts, row.eventname) == ("PENDING", 0, "foi-iao-complete")
    assert row.payload == _payload(1)


def test_a_rollback_leaves_no_outbox_row(service):
    service.enqueue(_payload(1), commit=False)
    db.session.rollback()
    assert FOIWorkflowEventOutbox.query.count() == 0


def test_outbox_row_commits_together_with_the_callers_pending_change(service):
    db.session.add(RequestChange(note="status changed"))
    service.enqueue(_payload(1))
    db.session.rollback()  # nothing left to roll back: both were committed together
    assert RequestChange.query.count() == 1 and FOIWorkflowEventOutbox.query.count() == 1


def test_rolling_back_the_callers_change_also_drops_the_outbox_row(service):
    db.session.add(RequestChange(note="status changed"))
    service.enqueue(_payload(1), commit=False)
    db.session.rollback()
    assert RequestChange.query.count() == 0 and FOIWorkflowEventOutbox.query.count() == 0


def test_failed_insert_does_not_roll_back_the_callers_pending_change(service):
    service.enqueue(_payload(1))
    db.session.add(RequestChange(note="kept"))
    with pytest.raises(IntegrityError):
        service.enqueue(_payload(1), commit=False)  # duplicate event_id
    db.session.commit()
    assert RequestChange.query.count() == 1


# --- dispatcher ------------------------------------------------------------------------------

def test_dispatch_delivers_pending_rows_and_marks_them_delivered(service):
    service.enqueue(_payload(1))
    sent = []
    assert _dispatch(service, lambda payload: sent.append(payload) or OK) == 1
    row = _row(1)
    assert sent == [_payload(1)]
    assert (row.status, row.attempts) == ("DELIVERED", 1)
    assert row.deliveredat is not None and row.lasterror is None


def test_rows_not_yet_due_and_non_pending_rows_are_not_delivered(service):
    _seed(service, 1, nextattemptat=NOW + timedelta(hours=1))
    _seed(service, 2, status=OutboxStatus.delivered.value)
    _seed(service, 3, status=OutboxStatus.dead.value)
    sent = []
    _dispatch(service, lambda payload: sent.append(payload) or OK)
    assert sent == []


def test_batch_size_limits_one_pass_and_rows_go_oldest_first(service):
    for n in (1, 2, 3):
        _seed(service, n, nextattemptat=NOW - timedelta(minutes=1))
    sent = []
    _dispatch(service, lambda payload: sent.append(payload["event_id"]) or OK, batch=2)
    assert sent == [_payload(1)["event_id"], _payload(2)["event_id"]]
    assert _row(3).status == "PENDING"


def test_retryable_failure_stays_pending_and_backs_off_exponentially(service):
    service.enqueue(_payload(1))
    _dispatch(service, lambda payload: RETRYABLE)
    row = _row(1)
    assert (row.status, row.attempts, row.lasterror) == ("PENDING", 1, "HTTP 503")
    assert row.nextattemptat == NOW + timedelta(seconds=30)
    _dispatch(service, lambda payload: RETRYABLE, now=NOW + timedelta(seconds=31))
    assert (_row(1).attempts, _row(1).nextattemptat) == (2, NOW + timedelta(seconds=31 + 60))


def test_backoff_is_jittered_between_half_and_full(service, monkeypatch):
    monkeypatch.setattr("request_api.services.workflowoutboxservice.random.uniform", lambda low, high: low)
    service.enqueue(_payload(1))
    _dispatch(service, lambda payload: RETRYABLE)
    assert _row(1).nextattemptat == NOW + timedelta(seconds=15)   # 30s backoff, lower bound; above the 15s timeout floor


def test_backoff_is_capped(service, monkeypatch):
    monkeypatch.setenv("N8N_WEBHOOK_RETRY_MAX_BACKOFF_SECONDS", "40")
    svc = workflowoutboxservice()
    _seed(svc, 1, attempts=2)
    _dispatch(svc, lambda payload: RETRYABLE)
    assert _row(1).nextattemptat == NOW + timedelta(seconds=40)


def test_row_is_dead_lettered_after_the_maximum_attempts(service, monkeypatch):
    monkeypatch.setenv("N8N_WEBHOOK_RETRY_MAX_ATTEMPTS", "3")
    svc = workflowoutboxservice()
    svc.enqueue(_payload(1))
    now = NOW
    for _ in range(3):
        _dispatch(svc, lambda payload: RETRYABLE, now=now)
        now += timedelta(hours=2)
    row = _row(1)
    assert (row.status, row.attempts, row.lasterror) == ("DEAD", 3, "HTTP 503")
    sent = []
    _dispatch(svc, lambda payload: sent.append(payload) or OK, now=now)
    assert sent == []


def test_non_retryable_failure_is_dead_immediately(service):
    service.enqueue(_payload(1))
    _dispatch(service, lambda payload: FATAL)
    assert (_row(1).status, _row(1).attempts, _row(1).lasterror) == ("DEAD", 1, "HTTP 400")


def test_one_bad_delivery_does_not_stop_the_rest_of_the_batch(service):
    service.enqueue(_payload(1))
    service.enqueue(_payload(2))

    def deliver(payload):
        if payload["event_id"] == _payload(1)["event_id"]:
            raise RuntimeError("boom")
        return OK

    assert _dispatch(service, deliver) == 1
    assert (_row(1).status, _row(2).status) == ("PENDING", "DELIVERED")


# --- crash between commit and delivery -----------------------------------------------------------

def test_committed_event_survives_a_crash_before_any_delivery_and_is_sent_by_a_new_dispatcher(app):
    workflowoutboxservice().enqueue(_payload(1))          # request thread commits, then the process dies
    db.session.remove()
    sent = []
    _dispatch(workflowoutboxservice(), lambda payload: sent.append(payload) or OK)   # fresh dispatcher after restart
    assert sent == [_payload(1)] and _row(1).status == "DELIVERED"


def test_crash_after_claim_leaves_a_lease_then_the_row_is_retried(service):
    service.enqueue(_payload(1))

    def crash(payload):
        raise SystemExit("process killed mid-delivery")

    with pytest.raises(SystemExit):
        _dispatch(service, crash)
    db.session.rollback()
    row = _row(1)
    assert (row.status, row.attempts) == ("PENDING", 1)
    sent = []
    _dispatch(service, lambda payload: sent.append(payload) or OK, now=NOW + timedelta(seconds=5))
    assert sent == []                                   # still leased: no double send
    _dispatch(service, lambda payload: sent.append(payload) or OK, now=NOW + timedelta(seconds=31))
    assert sent == [_payload(1)] and _row(1).status == "DELIVERED"


def test_row_claimed_the_maximum_times_without_a_result_goes_dead_without_sending(service, monkeypatch):
    monkeypatch.setenv("N8N_WEBHOOK_RETRY_MAX_ATTEMPTS", "2")
    svc = workflowoutboxservice()
    _seed(svc, 1, attempts=2, nextattemptat=NOW - timedelta(seconds=1))
    sent = []
    _dispatch(svc, lambda payload: sent.append(payload) or OK)
    assert sent == [] and _row(1).status == "DEAD"


# --- two dispatchers --------------------------------------------------------------------------------

def test_a_second_dispatcher_does_not_send_a_row_the_first_is_delivering(service):
    service.enqueue(_payload(1))
    sent_by_b = []

    def deliver_a(payload):
        db.session.remove()   # dispatcher B runs in its own session while A's request is in flight
        _dispatch(workflowoutboxservice(), lambda p: sent_by_b.append(p) or OK)
        return OK

    assert _dispatch(service, deliver_a) == 1
    assert sent_by_b == []


def test_an_acknowledgement_that_arrives_while_sending_is_not_overwritten(service):
    service.enqueue(_payload(1))

    def deliver(payload):
        service.acknowledge(payload["event_id"], "COMPLETED")
        return OK

    _dispatch(service, deliver)
    assert _row(1).status == "COMPLETED"


# --- acknowledgement -------------------------------------------------------------------------------

def test_delivered_moves_to_completed(service):
    _seed(service, 1, status="DELIVERED")
    result, row = service.acknowledge(_payload(1)["event_id"], "COMPLETED", executionid="77", now=NOW)
    assert (result, row.status, row.completedat, row.n8nexecutionid) == (AckResult.updated, "COMPLETED", NOW, "77")


def test_delivered_moves_to_failed_and_stores_the_error(service):
    _seed(service, 1, status="DELIVERED")
    result, row = service.acknowledge(_payload(1)["event_id"], "FAILED", error="Form.io PATCH failed", executionid="78")
    assert (result, row.status, row.lasterror, row.n8nexecutionid) == (AckResult.updated, "FAILED", "Form.io PATCH failed", "78")


def test_a_very_long_error_is_truncated(service):
    _seed(service, 1, status="DELIVERED")
    _, row = service.acknowledge(_payload(1)["event_id"], "FAILED", error="x" * 5000)
    assert len(row.lasterror) == 2000


def test_pending_can_be_acknowledged_because_n8n_receiving_it_proves_delivery(service):
    _seed(service, 1)
    assert service.acknowledge(_payload(1)["event_id"], "COMPLETED")[0] == AckResult.updated


def test_acknowledging_twice_is_safe(service):
    _seed(service, 1, status="DELIVERED")
    service.acknowledge(_payload(1)["event_id"], "COMPLETED", now=NOW)
    result, row = service.acknowledge(_payload(1)["event_id"], "COMPLETED", now=NOW + timedelta(hours=1))
    assert (result, row.completedat) == (AckResult.unchanged, NOW)


@pytest.mark.parametrize("start,target", [("COMPLETED", "FAILED"), ("FAILED", "COMPLETED"), ("DEAD", "COMPLETED"), ("DEAD", "FAILED")])
def test_transitions_outside_the_allowed_ones_are_rejected(service, start, target):
    _seed(service, 1, status=start, lasterror="real error")
    result, row = service.acknowledge(_payload(1)["event_id"], target)
    assert (result, row.status) == (AckResult.conflict, start)


@pytest.mark.parametrize("target", ["DELIVERED", "PENDING", "DEAD", "bogus", None])
def test_only_completed_and_failed_can_be_reported(service, target):
    _seed(service, 1, status="DELIVERED")
    assert service.acknowledge(_payload(1)["event_id"], target)[0] == AckResult.conflict
    assert _row(1).status == "DELIVERED"


def test_unknown_event_is_not_found(service):
    assert service.acknowledge("00000000-0000-4000-8000-999999999999", "COMPLETED") == (AckResult.notfound, None)


# --- sweeper ----------------------------------------------------------------------------------------

def test_sweeper_flags_delivered_rows_with_no_outcome_after_the_threshold(service):
    _seed(service, 1, status="DELIVERED", deliveredat=NOW - timedelta(minutes=31))
    _seed(service, 2, status="DELIVERED", deliveredat=NOW - timedelta(minutes=5))
    _seed(service, 3, status="COMPLETED", deliveredat=NOW - timedelta(hours=5))
    flagged = service.sweepnooutcome(30, now=NOW)
    assert flagged == [_payload(1)["event_id"]]
    assert _row(1).status == "FAILED" and _row(1).lasterror.startswith("NO_OUTCOME")
    assert (_row(2).status, _row(3).status) == ("DELIVERED", "COMPLETED")


def test_swept_rows_can_be_replayed(service):
    _seed(service, 1, status="DELIVERED", deliveredat=NOW - timedelta(hours=1))
    service.sweepnooutcome(30, now=NOW)
    assert service.replay(_payload(1)["event_id"], now=NOW)[0] == AckResult.updated


def test_a_late_success_supersedes_the_sweepers_failure(service):
    _seed(service, 1, status="DELIVERED", deliveredat=NOW - timedelta(hours=1))
    service.sweepnooutcome(30, now=NOW)
    result, row = service.acknowledge(_payload(1)["event_id"], "COMPLETED")
    assert (result, row.status, row.lasterror) == (AckResult.updated, "COMPLETED", None)


def test_the_real_failure_replaces_the_sweepers_no_outcome_note(service):
    _seed(service, 1, status="DELIVERED", deliveredat=NOW - timedelta(hours=1))
    service.sweepnooutcome(30, now=NOW)
    result, row = service.acknowledge(_payload(1)["event_id"], "FAILED", error="Send Email failed")
    assert (result, row.lasterror) == (AckResult.updated, "Send Email failed")


# --- replay ------------------------------------------------------------------------------------------

@pytest.mark.parametrize("status", ["DEAD", "FAILED"])
def test_replay_queues_dead_and_failed_events_again_with_the_same_event_id(service, status):
    _seed(service, 1, status=status, attempts=5, lasterror="boom")
    result, row = service.replay(_payload(1)["event_id"], now=NOW)
    assert (result, row.status, row.attempts, row.replaycount, row.nextattemptat) == (AckResult.updated, "PENDING", 0, 1, NOW)
    sent = []
    _dispatch(service, lambda payload: sent.append(payload) or OK)
    assert [p["event_id"] for p in sent] == [_payload(1)["event_id"]]
    assert _row(1).status == "DELIVERED"


@pytest.mark.parametrize("status", ["PENDING", "DELIVERED", "COMPLETED"])
def test_replay_is_refused_for_other_statuses(service, status):
    _seed(service, 1, status=status)
    result, row = service.replay(_payload(1)["event_id"])
    assert (result, row.status, row.replaycount) == (AckResult.conflict, status, 0)


def test_replay_of_an_unknown_event_is_not_found(service):
    assert service.replay("00000000-0000-4000-8000-999999999999") == (AckResult.notfound, None)


def test_listing_defaults_to_dead_and_failed_and_never_returns_the_payload(service):
    _seed(service, 1, status="DEAD", lasterror="HTTP 400")
    _seed(service, 2, status="FAILED", lasterror="NO_OUTCOME: x")
    _seed(service, 3, status="COMPLETED")
    events = service.listevents()
    assert {e["eventid"] for e in events} == {_payload(1)["event_id"], _payload(2)["event_id"]}
    assert all("payload" not in e and "foiRequestMetaData" not in str(e) for e in events)
    assert [e["status"] for e in service.listevents(["COMPLETED"])] == ["COMPLETED"]


# --- real concurrency on Postgres (skipped unless a scratch database is provided) --------------------

POSTGRES_URL = os.getenv("OUTBOX_TEST_POSTGRES_URL")


@pytest.mark.skipif(not POSTGRES_URL, reason="set OUTBOX_TEST_POSTGRES_URL to a scratch Postgres database")
def test_skip_locked_two_dispatchers_never_claim_the_same_row():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine(POSTGRES_URL)
    FOIWorkflowEventOutbox.__table__.create(engine, checkfirst=True)
    Session = sessionmaker(bind=engine)
    seed = Session()
    rows = 20
    try:
        for n in range(1000, 1000 + rows):
            seed.add(FOIWorkflowEventOutbox(eventid=_payload(n)["event_id"], eventname="e", payload=_payload(n), status="PENDING",
                                            attempts=0, nextattemptat=NOW - timedelta(minutes=1)))
        seed.commit()

        claimed = {"a": [], "b": []}
        holding = threading.Event()
        release = threading.Event()

        def claimer(name, wait_for=None, hold=False):
            session = Session()
            try:
                if wait_for:
                    wait_for.wait(5)
                batch = (session.query(FOIWorkflowEventOutbox)
                         .filter(FOIWorkflowEventOutbox.status == "PENDING", FOIWorkflowEventOutbox.nextattemptat <= NOW,
                                 FOIWorkflowEventOutbox.eventid.in_([_payload(n)["event_id"] for n in range(1000, 1000 + rows)]))
                         .order_by(FOIWorkflowEventOutbox.outboxid).limit(10).with_for_update(skip_locked=True).all())
                claimed[name] = [r.eventid for r in batch]
                if hold:
                    holding.set()
                    release.wait(5)           # keep A's row locks while B claims
                session.rollback()
            finally:
                session.close()

        a = threading.Thread(target=claimer, args=("a", None, True))
        b = threading.Thread(target=claimer, args=("b", holding))
        a.start(); b.start()
        b.join(10); release.set(); a.join(10)
        assert len(claimed["a"]) == 10 and len(claimed["b"]) == 10
        assert not set(claimed["a"]) & set(claimed["b"])
    finally:
        seed.rollback()
        seed.query(FOIWorkflowEventOutbox).filter(FOIWorkflowEventOutbox.eventid.in_([_payload(n)["event_id"] for n in range(1000, 1000 + rows)])).delete(synchronize_session=False)
        seed.commit()
        seed.close()
        engine.dispose()
