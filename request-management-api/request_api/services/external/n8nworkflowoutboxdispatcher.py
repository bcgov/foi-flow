"""Background dispatcher that delivers FOIWorkflowEventOutbox rows to n8n and sweeps stale ones."""

import logging
import os
import threading
import time

from request_api.services.external.commonworkflowservice import commonworkflowservice
from request_api.services.workflowoutboxservice import workflowoutboxservice


def dispatcherenabled():
    """Single source of truth for N8N_OUTBOX_DISPATCHER_ENABLED (unset means enabled)."""
    return (os.getenv("N8N_OUTBOX_DISPATCHER_ENABLED") or "true").strip().lower() == "true"


class N8NWorkflowOutboxDispatcher:
    """Every interval: delivers due PENDING rows; every sweep interval: flags DELIVERED rows
    that never reported an outcome. Safe to run in several pods/workers at once (the claim
    uses FOR UPDATE SKIP LOCKED)."""

    def __init__(self, app=None, service_factory=None, engine_factory=None, interval_seconds=5, batch_size=10,
                 sweep_interval_seconds=300, no_outcome_minutes=30, stop_event=None, clock=time.monotonic):
        self.app = app
        self.service_factory = service_factory or workflowoutboxservice
        self.engine_factory = engine_factory or commonworkflowservice
        self.interval_seconds = interval_seconds
        self.batch_size = batch_size
        self.sweep_interval_seconds = sweep_interval_seconds
        self.no_outcome_minutes = no_outcome_minutes
        self._stop_event = stop_event or threading.Event()
        self._clock = clock
        self._lastsweep = None
        self.thread = None

    @classmethod
    def from_env(cls, app=None):
        return cls(
            app=app,
            interval_seconds=int(os.getenv("N8N_OUTBOX_DISPATCH_INTERVAL_SECONDS") or 5),
            batch_size=int(os.getenv("N8N_OUTBOX_BATCH_SIZE") or 10),
            sweep_interval_seconds=int(os.getenv("N8N_OUTBOX_SWEEP_INTERVAL_SECONDS") or 300),
            no_outcome_minutes=int(os.getenv("N8N_OUTBOX_NO_OUTCOME_MINUTES") or 30),
        )

    def start(self):
        self.thread = threading.Thread(target=self.run_forever, name="n8n-workflow-outbox-dispatcher", daemon=True)
        self.thread.start()
        logging.info("n8n workflow outbox dispatcher started interval_seconds=%s", self.interval_seconds)
        return self.thread

    def stop(self):
        self._stop_event.set()
        if self.thread:
            self.thread.join(timeout=1)

    def run_once(self):
        """Delivers due rows and, when its interval has elapsed, sweeps. Returns the number delivered."""
        if self.app is None:
            return self.__work()
        with self.app.app_context():
            return self.__work()

    def __work(self):
        service = self.service_factory()
        delivered = service.dispatch_due(self.engine_factory().deliver, self.batch_size)
        now = self._clock()
        if self._lastsweep is None or now - self._lastsweep >= self.sweep_interval_seconds:
            self._lastsweep = now
            service.sweepnooutcome(self.no_outcome_minutes)
        return delivered

    def run_forever(self):
        while not self._stop_event.is_set():
            try:
                self.run_once()
            except Exception as err:
                logging.exception("Error running n8n workflow outbox dispatcher: %s", err)
            self._stop_event.wait(self.interval_seconds)
