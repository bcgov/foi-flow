import os
import logging

import redis
from walrus import Database

from request_api.models.default_method_result import DefaultMethodResult

class eventqueueservice:
    """Supports legacy streams plus OpenInfo list and stream publishing."""

    @staticmethod
    def _format_exception(err):
        return f"{type(err).__name__}: {err}"

    def __init__(self):
        self.stream_host = os.getenv("EVENT_QUEUE_HOST")
        self.stream_port = os.getenv("EVENT_QUEUE_PORT")
        self.stream_password = os.getenv("EVENT_QUEUE_PASSWORD")
        self.stream_db = Database(
            host=self.stream_host,
            port=self.stream_port,
            db=0,
            password=self.stream_password,
        )

        self.publication_host = os.getenv("PUBLICATION_REDIS_HOST", "localhost")
        self.publication_port = int(os.getenv("PUBLICATION_REDIS_PORT", 6379))
        self.publication_password = os.getenv("PUBLICATION_REDIS_PASSWORD")
        self.publication_client = redis.Redis(
            host=self.publication_host,
            port=self.publication_port,
            db=0,
            password=self.publication_password,
            decode_responses=True,
        )

    def add(self, streamkey, payload):
        try:
            stream = self.stream_db.Stream(streamkey)
            msgid = stream.add(payload, id="*")
            return DefaultMethodResult(True, 'Added to stream', msgid.decode('utf-8'))
        except Exception as err:
            logging.exception("Error in contacting Redis Stream")
            return DefaultMethodResult(False, self._format_exception(err), -1)

    def add_openinfo_queue_message(self, queue_name, payload):
        try:
            queue_position = self.publication_client.rpush(queue_name, payload)
            return DefaultMethodResult(True, 'Added to queue', queue_position)
        except Exception as err:
            logging.exception(
                "Error in contacting Publication Redis queue: %s",
                queue_name,
            )
            return DefaultMethodResult(False, self._format_exception(err), -1)

    def add_publication_stream_message(self, stream_name, payload):
        try:
            message_id = self.publication_client.xadd(stream_name, {"payload": payload})
            return DefaultMethodResult(True, 'Added to stream', message_id)
        except Exception as err:
            logging.exception(
                "Error in contacting Publication Redis stream: %s",
                stream_name,
            )
            return DefaultMethodResult(False, self._format_exception(err), -1)
