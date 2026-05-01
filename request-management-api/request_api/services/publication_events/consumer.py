"""Publication event consumers."""

import logging
import re

from request_api.models.FOIOpenInformationRequests import FOIOpenInformationRequests
from request_api.models.FOIProactiveDisclosureRequests import FOIProactiveDisclosureRequests
from request_api.models.default_method_result import DefaultMethodResult
from request_api.services.publication_events.types import PublicationEventType
from request_api.resources.foirequest import FOIRequestUpdateBySection


class OpenInfoPublishCompletedConsumer:
    """Handles completed publication events for OpenInfo records."""

    _CORRELATION_ID_PATTERN = re.compile(r"^openinfo-publish-(?P<openinfo_id>\d+)$")

    def __init__(self, openinfo_model=None):
        self.openinfo_model = openinfo_model or FOIOpenInformationRequests

    def handle_foiministryrequest_update(self, envelope):
        payload = envelope.get("payload") or {} 
        foirequestid = payload.get('request_id')
        foiministryrequestid = payload.get('ministry_request_id')
        oistatus_id = 4 if envelope.get("event_type") == PublicationEventType.PUBLISH_COMPLETED else 6 if envelope.get("event_type") == PublicationEventType.UNPUBLISH_COMPLETED else None
        result = FOIRequestUpdateBySection().handle_oistatusid_update(foirequestid, foiministryrequestid, oistatus_id)
        if result is not None and result["success"]:
            return DefaultMethodResult(True, "FOIMinistryRequest data updated")
        return DefaultMethodResult(False, "Unable to update FOIMinistryRequest data") 
        
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
        self.handle_foiministryrequest_update(envelope)

        return self.openinfo_model.create_published_version_from_openinfo_id(openinfo_id, message)


class ProactiveDisclosurePublishCompletedConsumer:
    """Handles completed publication events for Proactive Disclosure records."""

    _CORRELATION_ID_PATTERN = re.compile(
        r"^proactivedisclosure-publish-(?P<proactive_id>\d+)$"
    )

    def __init__(self, proactive_model=None):
        self.proactive_model = proactive_model or FOIProactiveDisclosureRequests
    
    def handle_foiministryrequest_update(self, envelope):
        payload = envelope.get("payload") or {} 
        foirequestid = payload.get('request_id')
        foiministryrequestid = payload.get('ministry_request_id')
        oistatus_id = 4 if envelope.get("event_type") == PublicationEventType.PUBLISH_COMPLETED else 6 if envelope.get("event_type") == PublicationEventType.UNPUBLISH_COMPLETED else None
        result = FOIRequestUpdateBySection().handle_oistatusid_update(foirequestid, foiministryrequestid, oistatus_id)
        if result is not None and result["success"]:
            return DefaultMethodResult(True, "FOIMinistryRequest data updated")
        return DefaultMethodResult(False, "Unable to update FOIMinistryRequest data") 

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
        self.handle_foiministryrequest_update(envelope)

        return self.proactive_model.create_published_version_from_proactive_id(
            proactive_id,
            message,
        )
