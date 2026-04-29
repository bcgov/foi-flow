"""Background scheduler for publication pre-publishing jobs."""

import logging
import os
import threading

from request_api.services.publication_events.scheduled_service import ScheduledPublicationService


class PublicationPrePublishingScheduler:
    """Runs the OpenInfo pre-publishing job on a fixed interval."""

    def __init__(self, job=None, interval_seconds=300, app=None, stop_event=None):
        self.job = job or ScheduledPublicationService().publish_due_openinfo_records
        self.interval_seconds = interval_seconds
        self.app = app
        self._stop_event = stop_event or threading.Event()
        self.thread = None

    @classmethod
    def from_env(cls, app=None, job=None):
        return cls(
            job=job,
            app=app,
            interval_seconds=int(os.getenv("PUBLICATION_PREPUBLISHING_INTERVAL_SECONDS", 300)),
        )

    def start(self):
        self.thread = threading.Thread(
            target=self.run_forever,
            name="publication-prepublishing-scheduler",
            daemon=True,
        )
        self.thread.start()
        logging.info(
            "Publication pre-publishing scheduler started interval_seconds=%s",
            self.interval_seconds,
        )
        return self.thread

    def stop(self):
        self._stop_event.set()
        if self.thread:
            self.thread.join(timeout=1)

    def run_once(self):
        if self.app is None:
            return self.job()
        with self.app.app_context():
            return self.job()

    def run_forever(self):
        while not self._stop_event.is_set():
            try:
                self.run_once()
            except Exception as err:
                logging.exception("Error running publication pre-publishing scheduler: %s", err)
            self._stop_event.wait(self.interval_seconds)
