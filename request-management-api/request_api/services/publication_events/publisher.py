"""Publication event publisher."""

import json
import logging
import os

from request_api.models.default_method_result import DefaultMethodResult
from request_api.services.external.eventqueueservice import eventqueueservice
from request_api.services.publication_events.types import PublicationEventType


class PublicationEventPublisher:
    """Publishes publication events to unified Redis streams."""

    def __init__(self, queue_service=None, stream_names=None):
        self.queue_service = queue_service or eventqueueservice()
        self.stream_names = stream_names or {
            PublicationEventType.PUBLISH_REQUESTED: os.getenv(
                "PUBLICATION_PUBLISH_STREAM_NAME",
            ),
            PublicationEventType.UNPUBLISH_REQUESTED: os.getenv(
                "PUBLICATION_UNPUBLISH_STREAM_NAME",
            ),
        }

    def _resolve_stream_name(self, event_type):
        stream_name = self.stream_names.get(event_type)
        if not stream_name:
            raise ValueError(f"No Redis stream configured for event type: {event_type}")
        return stream_name

    @staticmethod
    def _stringify_message(message):
        if isinstance(message, BaseException):
            return f"{type(message).__name__}: {message}"
        return str(message)

    def publish(self, envelope):
        serialized_envelope = json.dumps(envelope.to_dict(), default=str)
        stream_name = self._resolve_stream_name(envelope.event_type)
        logging.info(
            "Publishing publication event to stream | "
            "stream=%s event_id=%s event_type=%s correlation_id=%s",
            stream_name,
            envelope.event_id,
            envelope.event_type,
            envelope.correlation_id,
        )
        result = self.queue_service.add_publication_stream_message(stream_name, serialized_envelope)
        if not result.success:
            error_message = self._stringify_message(result.message)
            logging.error(
                "Failed to publish publication event to stream %s: %s",
                stream_name,
                error_message,
            )
            return DefaultMethodResult(False, error_message, result.identifier)
        logging.info(
            "Publication event pushed to stream | "
            "stream=%s event_id=%s event_type=%s stream_identifier=%s",
            stream_name,
            envelope.event_id,
            envelope.event_type,
            result.identifier,
        )
        return DefaultMethodResult(True, "Request queued for publishing successfully", result.identifier)
