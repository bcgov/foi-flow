"""Background scheduler for publication publishing jobs."""

import logging
import os
import threading
from datetime import datetime, time

from request_api.services.publication_events.scheduled_service import ScheduledPublicationService


class PublicationPrePublishingScheduler:
    """Runs the OpenInfo and PD publishing job on a fixed interval."""

    def __init__(self, job=None, interval_seconds=300, app=None, stop_event=None,
                 window_start=time(13, 0), window_end=time(13, 30)):
        self.job = job or ScheduledPublicationService().publish_all_due_records
        self.interval_seconds = interval_seconds
        self.app = app
        self._stop_event = stop_event or threading.Event()
        self.thread = None
        self.window_start = window_start
        self.window_end = window_end

    @classmethod
    def from_env(cls, app=None, job=None):
        raw_start = os.getenv("PUBLICATION_WINDOW_START", "13:00")
        raw_end = os.getenv("PUBLICATION_WINDOW_END", "15:00")
        window_start = time.fromisoformat(raw_start)
        window_end = time.fromisoformat(raw_end)
        return cls(
            job=job,
            app=app,
            interval_seconds=int(os.getenv("PUBLICATION_PREPUBLISHING_INTERVAL_SECONDS", 300)),
            window_start=window_start,
            window_end=window_end,
        )

    def _is_within_window(self):
        now = datetime.now().time()
        return self.window_start <= now <= self.window_end

    def start(self):
        self.thread = threading.Thread(
            target=self.run_forever,
            name="publication-prepublishing-scheduler",
            daemon=True,
        )
        self.thread.start()
        logging.info(
            "Publication publishing scheduler started interval_seconds=%s",
            self.interval_seconds,
        )
        return self.thread

    def stop(self):
        self._stop_event.set()
        if self.thread:
            self.thread.join(timeout=1)

    def run_once(self):
        if not self._is_within_window():
            logging.debug(
                "Outside publishing window (%s–%s), skipping",
                self.window_start.strftime("%H:%M"),
                self.window_end.strftime("%H:%M"),
            )
            return None
        if self.app is None:
            return self.job()
        with self.app.app_context():
            return self.job()

    def run_forever(self):
        while not self._stop_event.is_set():
            try:
                self.run_once()
            except Exception as err:
                logging.exception("Error running publication publishing scheduler: %s", err)
            self._stop_event.wait(self.interval_seconds)
