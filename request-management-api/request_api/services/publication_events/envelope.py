"""Event envelope models and factory."""

from dataclasses import dataclass
from datetime import datetime, timezone
import uuid

from request_api.services.publication_events.types import (
    DEFAULT_EVENT_SOURCE,
    DEFAULT_SCHEMA_VERSION,
)


def _utc_timestamp():
    return datetime.now(timezone.utc).isoformat()


@dataclass
class EventMeta:
    """System metadata for emitted events."""

    retry_count: int
    first_seen_at: str

    def to_dict(self):
        return {
            "retry_count": self.retry_count,
            "first_seen_at": self.first_seen_at,
        }


@dataclass
class EventEnvelope:
    """Standard event envelope."""

    event_id: str
    event_type: str
    timestamp: str
    schema_version: str
    correlation_id: str
    source: str
    payload: dict
    meta: EventMeta

    def to_dict(self):
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "timestamp": self.timestamp,
            "schema_version": self.schema_version,
            "correlation_id": self.correlation_id,
            "source": self.source,
            "payload": self.payload,
            "meta": self.meta.to_dict(),
        }


class EventEnvelopeFactory:
    """Builds standard publication event envelopes."""

    def __init__(self, source=DEFAULT_EVENT_SOURCE, schema_version=DEFAULT_SCHEMA_VERSION):
        self.source = source
        self.schema_version = schema_version

    def create(self, event_type, correlation_id, payload):
        timestamp = _utc_timestamp()
        return EventEnvelope(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            timestamp=timestamp,
            schema_version=self.schema_version,
            correlation_id=correlation_id,
            source=self.source,
            payload=payload,
            meta=EventMeta(retry_count=0, first_seen_at=timestamp),
        )

