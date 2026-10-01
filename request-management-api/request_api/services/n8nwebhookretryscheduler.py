"""Background scheduler that re-sends queued n8n webhook events."""

import logging
import os
import threading

from request_api.services.external.commonworkflowservice import commonworkflowservice
from request_api.services.external.n8nwebhookretryqueue import n8nwebhookretryqueue


class N8NWebhookRetryScheduler:
    """Drains the n8n webhook retry queue on a fixed interval."""

    def __init__(self, queue=None, engine_factory=None, interval_seconds=60, batch_size=10, stop_event=None):
        self.queue = queue or n8nwebhookretryqueue()
        self.engine_factory = engine_factory or commonworkflowservice
        self.interval_seconds = interval_seconds
        self.batch_size = batch_size
        self._stop_event = stop_event or threading.Event()
        self.thread = None

    @classmethod
    def from_env(cls, queue=None, engine_factory=None):
        return cls(
            queue=queue,
            engine_factory=engine_factory,
            interval_seconds=int(os.getenv("N8N_WEBHOOK_RETRY_INTERVAL_SECONDS", 60)),
            batch_size=int(os.getenv("N8N_WEBHOOK_RETRY_BATCH_SIZE", 10)),
        )

    def start(self):
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
        for entry in self.queue.claimdue(self.batch_size):
            attempts = entry.get("attempts", 0) + 1
            result = engine.deliver(entry["payload"])
            if result.delivered:
                delivered += 1
                logging.info("n8n webhook retry delivered; id=%s event=%s attempts=%s", entry.get("id"), entry.get("event"), attempts)
            elif result.retryable:
                self.queue.enqueue(entry["payload"], attempts=attempts, error=result.error, entryid=entry.get("id"))
            else:
                entry.update({"attempts": attempts, "lasterror": result.error})
                self.queue.deadletter(entry)
        return delivered

    def run_forever(self):
        while not self._stop_event.is_set():
            try:
                self.run_once()
            except Exception as err:
                logging.exception("Error running n8n webhook retry scheduler: %s", err)
            self._stop_event.wait(self.interval_seconds)
