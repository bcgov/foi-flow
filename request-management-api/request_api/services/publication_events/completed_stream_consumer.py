"""Redis Stream consumer for publication completed events."""

import json
import logging
import os
import socket
import threading
import time

import redis

from request_api.services.publication_events.consumer import (
    OpenInfoPublishCompletedConsumer,
    ProactiveDisclosurePublishCompletedConsumer,
)
from request_api.services.publication_events.types import PublicationEventType


class PublicationCompletedStreamConsumer:
    """Consumes publication completed Redis Stream messages and routes them."""

    def __init__(
        self,
        redis_client,
        stream_names,
        group_name,
        consumer_name,
        handlers=None,
        app=None,
        count=10,
        block_ms=5000,
        sleep_seconds=1,
    ):
        self.redis_client = redis_client
        self.stream_names = {event_type: stream for event_type, stream in stream_names.items() if stream}
        self.group_name = group_name
        self.consumer_name = consumer_name
        self.handlers = handlers or {
            PublicationEventType.OPENINFO_PUBLISH_COMPLETED: OpenInfoPublishCompletedConsumer(),
            PublicationEventType.PROACTIVE_DISCLOSURE_PUBLISH_COMPLETED: ProactiveDisclosurePublishCompletedConsumer(),
        }
        self.app = app
        self.count = count
        self.block_ms = block_ms
        self.sleep_seconds = sleep_seconds
        self._stop_event = threading.Event()
        self.thread = None

    @classmethod
    def from_env(cls, redis_client=None, app=None):
        redis_client = redis_client or redis.Redis(
            host=os.getenv("PUBLICATION_REDIS_HOST", "localhost"),
            port=int(os.getenv("PUBLICATION_REDIS_PORT", 6379)),
            db=0,
            password=os.getenv("PUBLICATION_REDIS_PASSWORD"),
            decode_responses=True,
            socket_connect_timeout=int(os.getenv("PUBLICATION_REDIS_CONNECT_TIMEOUT", 5)),
            health_check_interval=int(os.getenv("PUBLICATION_REDIS_HEALTHCHECK_INTERVAL", 30)),
            retry_on_timeout=True,
            socket_keepalive=True,
        )
        return cls(
            redis_client=redis_client,
            stream_names={
                PublicationEventType.OPENINFO_PUBLISH_COMPLETED: os.getenv(
                    "OPENINFO_PUBLISH_COMPLETED_STREAM_NAME",
                    "openinfo.publish.completed",
                ),
                PublicationEventType.PROACTIVE_DISCLOSURE_PUBLISH_COMPLETED: os.getenv(
                    "PROACTIVEDISCLOSURE_PUBLISH_COMPLETED_STREAM_NAME",
                    "proactivedisclosure.publish.completed",
                ),
            },
            group_name=os.getenv(
                "PUBLICATION_COMPLETED_CONSUMER_GROUP",
                "request-management-api",
            ),
            consumer_name=os.getenv(
                "PUBLICATION_COMPLETED_CONSUMER_NAME",
                f"{socket.gethostname()}-{os.getpid()}",
            ),
            app=app,
            count=int(os.getenv("PUBLICATION_COMPLETED_CONSUMER_COUNT", 10)),
            block_ms=int(os.getenv("PUBLICATION_COMPLETED_CONSUMER_BLOCK_MS", 5000)),
            sleep_seconds=float(os.getenv("PUBLICATION_COMPLETED_CONSUMER_SLEEP_SECONDS", 1)),
        )

    def ensure_groups(self):
        for stream_name in self.stream_names.values():
            try:
                self.redis_client.xgroup_create(
                    name=stream_name,
                    groupname=self.group_name,
                    id="0",
                    mkstream=True,
                )
            except redis.exceptions.ResponseError as err:
                if "BUSYGROUP" not in str(err):
                    raise

    def start(self):
        self.ensure_groups()
        self.thread = threading.Thread(
            target=self.run_forever,
            name="publication-completed-stream-consumer",
            daemon=True,
        )
        self.thread.start()
        logging.info(
            "Publication completed stream consumer started",
            extra={
                "streams": list(self.stream_names.values()),
                "group_name": self.group_name,
                "consumer_name": self.consumer_name,
            },
        )
        return self.thread

    def stop(self):
        self._stop_event.set()
        if self.thread:
            self.thread.join(timeout=self.sleep_seconds + 1)

    def run_forever(self):
        while not self._stop_event.is_set():
            try:
                self.read_once()
            except Exception as err:
                logging.exception("Error consuming publication completed event: %s", err)
                time.sleep(self.sleep_seconds)

    def read_once(self):
        if not self.stream_names:
            return 0

        messages = self.redis_client.xreadgroup(
            groupname=self.group_name,
            consumername=self.consumer_name,
            streams={stream_name: ">" for stream_name in self.stream_names.values()},
            count=self.count,
            block=self.block_ms,
        )
        processed = 0
        for stream_name, stream_messages in messages:
            for message_id, fields in stream_messages:
                processed += 1
                self._handle_message(stream_name, message_id, fields)
        return processed

    def _handle_message(self, stream_name, message_id, fields):
        envelope = self._parse_envelope(fields)
        event_type = envelope.get("event_type")
        handler = self.handlers.get(event_type)
        if handler is None:
            logging.error(
                "No publication completed handler configured for event type: %s",
                event_type,
            )
            return

        result = self._call_handler(handler, envelope)
        if result.success:
            self.redis_client.xack(stream_name, self.group_name, message_id)
        else:
            logging.error(
                "Publication completed handler failed for message %s: %s",
                message_id,
                result.message,
            )

    def _call_handler(self, handler, envelope):
        if self.app is None:
            return handler.handle(envelope)
        with self.app.app_context():
            return handler.handle(envelope)

    @staticmethod
    def _parse_envelope(fields):
        payload = fields.get("payload") if isinstance(fields, dict) else fields
        if isinstance(payload, bytes):
            payload = payload.decode("utf-8")
        if isinstance(payload, str):
            return json.loads(payload)
        return payload
