"""Publication event type constants."""


class PublicationEventType:
    """Unified publication event types."""

    PUBLISH_REQUESTED = "publication.publish.requested"
    PUBLISH_COMPLETED = "publication.publish.completed"
    UNPUBLISH_REQUESTED = "publication.unpublish.requested"
    UNPUBLISH_COMPLETED = "publication.unpublish.completed"


class PublicationKind:
    """Discriminator for OpenInfo vs Proactive Disclosure."""

    OPENINFO = "openinfo"
    PROACTIVE_DISCLOSURE = "proactivedisclosure"


DEFAULT_SCHEMA_VERSION = "1.0.0"
DEFAULT_EVENT_SOURCE = "request-management-api"
