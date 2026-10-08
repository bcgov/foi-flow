from contextlib import contextmanager
from unittest.mock import MagicMock

import pytest

from request_api.services.external.n8nworkflowoutboxdispatcher import N8NWorkflowOutboxDispatcher, dispatcherenabled


class FakeService:
    def __init__(self):
        self.dispatched = []
        self.swept = []

    def dispatch_due(self, deliver, batchsize):
        self.dispatched.append((deliver, batchsize))
        return 2

    def sweepnooutcome(self, minutes):
        self.swept.append(minutes)


class FakeEngine:
    def deliver(self, payload):
        raise AssertionError("not called by the dispatcher itself")


class Clock:
    def __init__(self):
        self.now = 0

    def __call__(self):
        return self.now


@pytest.fixture
def service():
    return FakeService()


def _dispatcher(service, clock=None, **kwargs):
    engine = FakeEngine()
    dispatcher = N8NWorkflowOutboxDispatcher(service_factory=lambda: service, engine_factory=lambda: engine,
                                             batch_size=7, no_outcome_minutes=45, clock=clock or Clock(), **kwargs)
    return dispatcher, engine


def test_run_once_hands_the_engines_deliver_to_the_service_with_the_batch_size(service):
    dispatcher, engine = _dispatcher(service)
    assert dispatcher.run_once() == 2
    deliver, batchsize = service.dispatched[0]
    assert deliver == engine.deliver and batchsize == 7


def test_sweep_runs_on_the_first_pass_then_only_when_its_interval_has_elapsed(service):
    clock = Clock()
    dispatcher, _ = _dispatcher(service, clock=clock, sweep_interval_seconds=300)
    dispatcher.run_once()
    clock.now = 100
    dispatcher.run_once()
    assert service.swept == [45]
    clock.now = 301
    dispatcher.run_once()
    assert service.swept == [45, 45]
    assert len(service.dispatched) == 3


def test_run_once_works_inside_the_app_context(service):
    entered = []

    @contextmanager
    def context():
        entered.append("in")
        yield
        entered.append("out")

    app = MagicMock()
    app.app_context = context
    dispatcher, _ = _dispatcher(service, app=app)
    dispatcher.run_once()
    assert entered == ["in", "out"] and len(service.dispatched) == 1


def test_run_forever_survives_an_error_and_keeps_polling(service, caplog):
    calls = []
    dispatcher, _ = _dispatcher(service, interval_seconds=0)

    def flaky():
        calls.append(1)
        if len(calls) == 1:
            raise RuntimeError("db down")
        if len(calls) == 3:
            dispatcher.stop()

    dispatcher.run_once = flaky
    dispatcher.run_forever()
    assert len(calls) == 3
    assert "Error running n8n workflow outbox dispatcher" in caplog.text


def test_from_env_reads_the_settings(monkeypatch):
    monkeypatch.setenv("N8N_OUTBOX_DISPATCH_INTERVAL_SECONDS", "2")
    monkeypatch.setenv("N8N_OUTBOX_BATCH_SIZE", "25")
    monkeypatch.setenv("N8N_OUTBOX_SWEEP_INTERVAL_SECONDS", "60")
    monkeypatch.setenv("N8N_OUTBOX_NO_OUTCOME_MINUTES", "15")
    dispatcher = N8NWorkflowOutboxDispatcher.from_env()
    assert (dispatcher.interval_seconds, dispatcher.batch_size, dispatcher.sweep_interval_seconds, dispatcher.no_outcome_minutes) == (2, 25, 60, 15)


def test_from_env_defaults(monkeypatch):
    for name in ("N8N_OUTBOX_DISPATCH_INTERVAL_SECONDS", "N8N_OUTBOX_BATCH_SIZE",
                 "N8N_OUTBOX_SWEEP_INTERVAL_SECONDS", "N8N_OUTBOX_NO_OUTCOME_MINUTES"):
        monkeypatch.delenv(name, raising=False)
    dispatcher = N8NWorkflowOutboxDispatcher.from_env()
    assert (dispatcher.interval_seconds, dispatcher.batch_size, dispatcher.sweep_interval_seconds, dispatcher.no_outcome_minutes) == (5, 10, 300, 30)



@pytest.mark.parametrize("raw,expected", [
    (None, True), ("", True), ("true", True), ("TRUE", True), (" true\n", True),
    ("false", False), ("False", False), ("0", False), ("no", False),
])
def test_dispatcherenabled(monkeypatch, raw, expected):
    if raw is None:
        monkeypatch.delenv("N8N_OUTBOX_DISPATCHER_ENABLED", raising=False)
    else:
        monkeypatch.setenv("N8N_OUTBOX_DISPATCHER_ENABLED", raw)
    assert dispatcherenabled() is expected
