"""Background dispatcher that delivers FOIWorkflowEventOutbox rows to n8n and sweeps stale ones."""

import logging
import os
import threading
import time

from request_api.services.external.n8nworkflowservice import n8nworkflowservice
from request_api.services.workflowoutboxservice import workflowoutboxservice


MAX_RETENTION_BATCHES = 20  # bounds one retention run


def dispatcherenabled():
    """Single source of truth for N8N_OUTBOX_DISPATCHER_ENABLED (unset means enabled)."""
    return (os.getenv("N8N_OUTBOX_DISPATCHER_ENABLED") or "true").strip().lower() == "true"


class N8NWorkflowOutboxDispatcher:
    """Every interval: delivers due PENDING rows; every sweep interval: flags DELIVERED rows
    that never reported an outcome. Safe to run in several pods/workers at once (the claim
    uses FOR UPDATE SKIP LOCKED)."""

    def __init__(self, app=None, service_factory=None, engine_factory=None, interval_seconds=5, batch_size=10,
                 sweep_interval_seconds=300, no_outcome_minutes=30, stop_event=None, clock=time.monotonic,
                 scrub_after_days=0, purge_after_days=0, retention_interval_seconds=3600, retention_batch_size=1000):
        self.app = app
        self.service_factory = service_factory or workflowoutboxservice
        self.engine_factory = engine_factory or n8nworkflowservice
        self.interval_seconds = interval_seconds
        self.batch_size = batch_size
        self.sweep_interval_seconds = sweep_interval_seconds
        self.no_outcome_minutes = no_outcome_minutes
        # retention is off unless a number of days is set (0 = never)
        self.scrub_after_days = scrub_after_days
        self.purge_after_days = purge_after_days
        self.retention_interval_seconds = retention_interval_seconds
        self.retention_batch_size = retention_batch_size
        self._stop_event = stop_event or threading.Event()
        self._clock = clock
        self._lastsweep = None
        self._lastretention = None
        self.thread = None

    @classmethod
    def from_env(cls, app=None):
        return cls(
            app=app,
            interval_seconds=int(os.getenv("N8N_OUTBOX_DISPATCH_INTERVAL_SECONDS") or 5),
            batch_size=int(os.getenv("N8N_OUTBOX_BATCH_SIZE") or 10),
            sweep_interval_seconds=int(os.getenv("N8N_OUTBOX_SWEEP_INTERVAL_SECONDS") or 300),
            no_outcome_minutes=int(os.getenv("N8N_OUTBOX_NO_OUTCOME_MINUTES") or 30),
            scrub_after_days=int(os.getenv("N8N_OUTBOX_SCRUB_AFTER_DAYS") or 0),
            purge_after_days=int(os.getenv("N8N_OUTBOX_PURGE_AFTER_DAYS") or 0),
            retention_interval_seconds=int(os.getenv("N8N_OUTBOX_RETENTION_INTERVAL_SECONDS") or 3600),
            retention_batch_size=int(os.getenv("N8N_OUTBOX_RETENTION_BATCH_SIZE") or 1000),
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
        if (self.scrub_after_days or self.purge_after_days) and (
                self._lastretention is None or now - self._lastretention >= self.retention_interval_seconds):
            self._lastretention = now
            self.__retention(service)
        return delivered

    def __retention(self, service):
        """Scrubs, then deletes, old COMPLETED rows in batches (bounded per run). A failure is logged
        and never stops delivery. Safe in several pods at once: batches skip locked rows."""
        try:
            for _ in range(MAX_RETENTION_BATCHES):
                if not self.scrub_after_days or service.scrubpayloads(self.scrub_after_days, self.retention_batch_size) < self.retention_batch_size:
                    break
            for _ in range(MAX_RETENTION_BATCHES):
                if not self.purge_after_days:
                    break
                deleted = service.purgecompleted(self.purge_after_days, self.retention_batch_size)
                logging.info("n8n workflow outbox retention: deleted %s outbox rows", deleted)
                if deleted < self.retention_batch_size:
                    break
        except Exception as err:
            logging.exception("n8n workflow outbox retention failed: %s", type(err).__name__)

    def run_forever(self):
        while not self._stop_event.is_set():
            try:
                self.run_once()
            except Exception as err:
                logging.exception("Error running n8n workflow outbox dispatcher: %s", err)
            self._stop_event.wait(self.interval_seconds)
