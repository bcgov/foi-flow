import threading

from request_api.services.external.n8nworkflowoutboxdispatcher import N8NWorkflowOutboxDispatcher

"""The dispatcher runs the outbox retention only when it is configured, in bounded batches, and never lets a failure stop delivery."""


class FakeService:
    def __init__(self, scrubbed=(0,), purged=(0,), fail=False):
        self.scrubbed, self.purged, self.fail = list(scrubbed), list(purged), fail
        self.calls = []

    def dispatch_due(self, deliver, batch_size):
        return 0

    def sweepnooutcome(self, minutes):
        self.calls.append(("sweep", minutes))

    def scrubpayloads(self, days, batchsize):
        self.calls.append(("scrub", days, batchsize))
        if self.fail:
            raise RuntimeError("db down")
        return self.scrubbed.pop(0) if self.scrubbed else 0

    def purgecompleted(self, days, batchsize):
        self.calls.append(("purge", days, batchsize))
        return self.purged.pop(0) if self.purged else 0


class Clock:
    now = 0.0

    def __call__(self):
        return self.now


def _dispatcher(service, clock=None, **kwargs):
    return N8NWorkflowOutboxDispatcher(app=None, service_factory=lambda: service, engine_factory=lambda: type("E", (), {"deliver": None})(),
                                       stop_event=threading.Event(), clock=clock or Clock(), **kwargs)


def _retention_calls(service):
    return [call for call in service.calls if call[0] in ("scrub", "purge")]


def test_retention_is_off_by_default():
    service = FakeService()
    _dispatcher(service).run_once()
    assert _retention_calls(service) == []


def test_retention_runs_scrub_then_purge_with_the_configured_days():
    service = FakeService()
    _dispatcher(service, scrub_after_days=90, purge_after_days=365, retention_batch_size=50).run_once()
    assert _retention_calls(service) == [("scrub", 90, 50), ("purge", 365, 50)]


def test_only_the_configured_stage_runs():
    service = FakeService()
    _dispatcher(service, purge_after_days=365).run_once()
    assert _retention_calls(service) == [("purge", 365, 1000)]


def test_a_full_batch_is_followed_by_another_until_one_is_short():
    service = FakeService(scrubbed=[10, 10, 3], purged=[10, 4])
    _dispatcher(service, scrub_after_days=90, purge_after_days=365, retention_batch_size=10).run_once()
    assert [call[0] for call in _retention_calls(service)] == ["scrub"] * 3 + ["purge"] * 2


def test_retention_waits_for_its_interval():
    service, clock = FakeService(), Clock()
    dispatcher = _dispatcher(service, clock, scrub_after_days=90, retention_interval_seconds=3600)
    dispatcher.run_once()
    clock.now = 100
    dispatcher.run_once()
    assert len(_retention_calls(service)) == 1
    clock.now = 3700
    dispatcher.run_once()
    assert len(_retention_calls(service)) == 2


def test_a_retention_failure_does_not_stop_the_dispatcher():
    service = FakeService(fail=True)
    assert _dispatcher(service, scrub_after_days=90).run_once() == 0
    assert ("sweep", 30) in service.calls
