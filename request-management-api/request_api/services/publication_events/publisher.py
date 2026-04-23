"""Publication event publisher."""

import json
import logging
import os

from request_api.models.default_method_result import DefaultMethodResult
from request_api.services.external.eventqueueservice import eventqueueservice
from request_api.services.publication_events.types import PublicationEventType


class PublicationEventPublisher:
    """Publishes publication events to the OpenInfo Redis stream."""

    def __init__(self, queue_service=None, stream_name=None, stream_names=None):
        self.queue_service = queue_service or eventqueueservice()
        default_stream_name = stream_name or os.getenv("OPENINFO_REDIS_STREAM_NAME")
        self.stream_names = stream_names or {
            PublicationEventType.OPENINFO_PUBLISH_REQUESTED: os.getenv(
                "OPENINFO_PUBLISH_STREAM_NAME",
                default_stream_name,
            ),
            PublicationEventType.PROACTIVE_DISCLOSURE_PUBLISH_REQUESTED: os.getenv(
                "PROACTIVEDISCLOSURE_PUBLISH_STREAM_NAME",
                default_stream_name,
            ),
        }

    def _resolve_stream_name(self, event_type):
        stream_name = self.stream_names.get(event_type) or os.getenv("OPENINFO_REDIS_STREAM_NAME")
        if not stream_name:
            raise ValueError(f"No Redis stream configured for event type: {event_type}")
        return stream_name

    def publish(self, envelope):
        serialized_envelope = json.dumps(envelope.to_dict(), default=str)
        stream_name = self._resolve_stream_name(envelope.event_type)
        logging.info(
            "Publishing publication event to OpenInfo stream",
            extra={
                "stream_name": stream_name,
                "event_id": envelope.event_id,
                "event_type": envelope.event_type,
                "correlation_id": envelope.correlation_id,
            },
        )
        result = self.queue_service.add_publication_stream_message(stream_name, serialized_envelope)
        if not result.success:
            logging.error("Failed to publish publication event to stream %s", stream_name)
            return DefaultMethodResult(False, result.message, result.identifier)
        logging.info(
            "Publication event pushed to OpenInfo stream",
            extra={
                "stream_name": stream_name,
                "event_id": envelope.event_id,
                "event_type": envelope.event_type,
                "stream_identifier": result.identifier,
            },
        )
        return DefaultMethodResult(True, "Request queued for publishing successfully", result.identifier)
