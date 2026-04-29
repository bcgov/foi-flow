"""Publication event type constants."""


class PublicationEventType:
    """Known publication event types."""

    OPENINFO_PUBLISH_REQUESTED = "openinfo.publish.requested"
    OPENINFO_PUBLISH_COMPLETED = "openinfo.publish.completed"
    PROACTIVE_DISCLOSURE_PUBLISH_REQUESTED = "proactivedisclosure.publish.requested"
    PROACTIVE_DISCLOSURE_PUBLISH_COMPLETED = "proactivedisclosure.publish.completed"


DEFAULT_SCHEMA_VERSION = "1.0.0"
DEFAULT_EVENT_SOURCE = "request-management-api"
