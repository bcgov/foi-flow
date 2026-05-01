"""Publication event consumers."""

import logging
import re

from request_api.models.FOIOpenInformationRequests import FOIOpenInformationRequests
from request_api.models.FOIProactiveDisclosureRequests import FOIProactiveDisclosureRequests
from request_api.models.default_method_result import DefaultMethodResult
from request_api.services.publication_events.types import PublicationEventType


class OpenInfoPublishCompletedConsumer:
    """Handles completed publication events for OpenInfo records."""

    _CORRELATION_ID_PATTERN = re.compile(r"^openinfo-publish-(?P<openinfo_id>\d+)$")

    def __init__(self, openinfo_model=None):
        self.openinfo_model = openinfo_model or FOIOpenInformationRequests

    def handle(self, envelope):
        """Validate and apply a publication.publish.completed event for OpenInfo."""
        if envelope.get("event_type") != PublicationEventType.PUBLISH_COMPLETED:
            return DefaultMethodResult(False, "Unsupported event type")

        payload = envelope.get("payload") or {}
        missing = [field for field in ("tenant_id", "request_event_id") if not payload.get(field)]
        if missing:
            return DefaultMethodResult(False, f"Missing required payload fields: {', '.join(missing)}")

        correlation_id = envelope.get("correlation_id")
        match = self._CORRELATION_ID_PATTERN.match(correlation_id or "")
        if not match:
            return DefaultMethodResult(False, "Invalid OpenInfo publish correlation_id")

        openinfo_id = int(match.group("openinfo_id"))
        message = payload.get("message") or "Publication completed"

        logging.info(
            "Handling OpenInfo publish completed event | "
            f"event_id={envelope.get('event_id')} "
            f"correlation_id={correlation_id} "
            f"openinfo_id={openinfo_id} "
            f"request_event_id={payload.get('request_event_id')}"
        )
        return self.openinfo_model.create_published_version_from_openinfo_id(openinfo_id, message)


class OpenInfoUnpublishCompletedConsumer:
    """Logs completed unpublish events for OpenInfo records."""

    def handle(self, envelope):
        """Validate and log a publication.unpublish.completed event for OpenInfo."""
        if envelope.get("event_type") != PublicationEventType.UNPUBLISH_COMPLETED:
            return DefaultMethodResult(False, "Unsupported event type")

        payload = envelope.get("payload") or {}
        # FIXME: status needs to be updated
        logging.info(
            "Handling OpenInfo unpublish completed event | "
            f"event_id={envelope.get('event_id')} "
            f"correlation_id={envelope.get('correlation_id')} "
            f"kind={payload.get('kind')} "
            f"publication_id={payload.get('publication_id')} "
            f"status={payload.get('status')} "
            f"objects_deleted={payload.get('objects_deleted')} "
            f"sitemap_result={payload.get('sitemap_result')}"
        )
        return DefaultMethodResult(True, "Unpublish completion logged")


class ProactiveDisclosurePublishCompletedConsumer:
    """Handles completed publication events for Proactive Disclosure records."""

    _CORRELATION_ID_PATTERN = re.compile(
        r"^proactivedisclosure-publish-(?P<proactive_id>\d+)$"
    )

    def __init__(self, proactive_model=None):
        self.proactive_model = proactive_model or FOIProactiveDisclosureRequests

    def handle(self, envelope):
        """Validate and apply a publication.publish.completed event for Proactive Disclosure."""
        if envelope.get("event_type") != PublicationEventType.PUBLISH_COMPLETED:
            return DefaultMethodResult(False, "Unsupported event type")

        payload = envelope.get("payload") or {}
        missing = [field for field in ("tenant_id", "request_event_id") if not payload.get(field)]
        if missing:
            return DefaultMethodResult(False, f"Missing required payload fields: {', '.join(missing)}")

        correlation_id = envelope.get("correlation_id")
        match = self._CORRELATION_ID_PATTERN.match(correlation_id or "")
        if not match:
            return DefaultMethodResult(False, "Invalid Proactive Disclosure publish correlation_id")

        proactive_id = int(match.group("proactive_id"))
        message = payload.get("message") or "Publication completed"

        logging.info(
            "Handling Proactive Disclosure publish completed event | "
            f"event_id={envelope.get('event_id')} "
            f"correlation_id={correlation_id} "
            f"proactive_id={proactive_id} "
            f"request_event_id={payload.get('request_event_id')}"
        )

        return self.proactive_model.create_published_version_from_proactive_id(
            proactive_id,
            message,
        )


class ProactiveDisclosureUnpublishCompletedConsumer:
    """Logs completed unpublish events for Proactive Disclosure records."""

    def handle(self, envelope):
        """Validate and log a publication.unpublish.completed event for Proactive Disclosure."""
        if envelope.get("event_type") != PublicationEventType.UNPUBLISH_COMPLETED:
            return DefaultMethodResult(False, "Unsupported event type")
        payload = envelope.get("payload") or {}

        # FIXME: status needs to be updated
        logging.info(
            "Handling Proactive Disclosure unpublish completed event | "
            f"event_id={envelope.get('event_id')} "
            f"correlation_id={envelope.get('correlation_id')} "
            f"kind={payload.get('kind')} "
            f"publication_id={payload.get('publication_id')} "
            f"status={payload.get('status')} "
            f"objects_deleted={payload.get('objects_deleted')} "
            f"sitemap_result={payload.get('sitemap_result')}"
        )
        return DefaultMethodResult(True, "Unpublish completion logged")
