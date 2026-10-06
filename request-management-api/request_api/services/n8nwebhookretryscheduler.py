"""Background scheduler that re-sends queued n8n webhook events."""

import logging
import os
import threading

from request_api.services.external.commonworkflowservice import commonworkflowservice
from request_api.services.external.n8nwebhookretryqueue import n8nwebhookretryqueue


class N8NWebhookRetryScheduler:
    """Drains the n8n webhook retry queue on a fixed interval."""

    def __init__(self, queue=None, engine_factory=None, interval_seconds=60, batch_size=10,
                 webhook_timeout_seconds=10, stop_event=None):
        self.queue = queue or n8nwebhookretryqueue()
        self.engine_factory = engine_factory or commonworkflowservice
        self.interval_seconds = interval_seconds
        self.batch_size = batch_size
        self.webhook_timeout_seconds = webhook_timeout_seconds
        self._stop_event = stop_event or threading.Event()
        self.thread = None

    @classmethod
    def from_env(cls, queue=None, engine_factory=None):
        return cls(
            queue=queue,
            engine_factory=engine_factory,
            interval_seconds=int(os.getenv("N8N_WEBHOOK_RETRY_INTERVAL_SECONDS", 60)),
            batch_size=int(os.getenv("N8N_WEBHOOK_RETRY_BATCH_SIZE", 10)),
            webhook_timeout_seconds=float(os.getenv("N8N_WEBHOOK_TIMEOUT_SECONDS") or 10),
        )

    def check_lease(self):
        """Warns when a lease could expire while a full batch is still being sent,
        which would let another worker send the same entry again."""
        worstcase = self.batch_size * self.webhook_timeout_seconds
        if self.queue.leaseseconds <= worstcase:
            logging.warning("n8n webhook retry lease is not longer than a worst-case batch; lease_seconds=%s batch_size=%s timeout_seconds=%s",
                            self.queue.leaseseconds, self.batch_size, self.webhook_timeout_seconds)

    def start(self):
        self.check_lease()
        self.thread = threading.Thread(
            target=self.run_forever,
            name="n8n-webhook-retry-scheduler",
            daemon=True,
        )
        self.thread.start()
        logging.info("n8n webhook retry scheduler started interval_seconds=%s", self.interval_seconds)
        return self.thread

    def stop(self):
        self._stop_event.set()
        if self.thread:
            self.thread.join(timeout=1)

    def run_once(self):
        """Re-sends every due entry once. Returns the number delivered."""
        delivered = 0
        engine = self.engine_factory()
        for member, entry in self.queue.claimdue(self.batch_size):
            attempts = entry.get("attempts", 0) + 1
            try:
                result = engine.deliver(entry["payload"])
            except Exception as err:
                logging.exception("n8n webhook retry failed unexpectedly; id=%s event=%s", entry.get("id"), entry.get("event"))
                self.queue.reschedule(member, entry, attempts, type(err).__name__)
                continue
            if result.delivered:
                self.queue.ack(member)
                delivered += 1
                logging.info("n8n webhook retry delivered; id=%s event=%s attempts=%s", entry.get("id"), entry.get("event"), attempts)
            elif result.retryable:
                self.queue.reschedule(member, entry, attempts, result.error)
            else:
                self.queue.deadletter(dict(entry, attempts=attempts, lasterror=result.error), member)
        self.__logbacklog()
        return delivered

    def __logbacklog(self):
        try:
            pending, failed = self.queue.backlog()
        except Exception:
            logging.exception("Unable to read n8n webhook retry backlog")
            return
        level = logging.INFO if (pending or failed) else logging.DEBUG
        logging.log(level, "n8n webhook retry backlog; pending=%s failed=%s", pending, failed)

    def run_forever(self):
        while not self._stop_event.is_set():
            try:
                self.run_once()
            except Exception as err:
                logging.exception("Error running n8n webhook retry scheduler: %s", err)
            self._stop_event.wait(self.interval_seconds)
