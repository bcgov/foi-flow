"""Publication event consumers."""

import logging
import re
from pathlib import PurePosixPath

from request_api.models.FOIOpenInformationRequests import FOIOpenInformationRequests
from request_api.models.FOIProactiveDisclosureRequests import FOIProactiveDisclosureRequests
from request_api.models.default_method_result import DefaultMethodResult
from request_api.services.publication_events.types import PublicationEventType
from request_api.resources.foirequest import FOIRequestUpdateBySection
from request_api.utils.enums import OIStatusEnum


PUBLISHING_SERVICE_USER_ID = "publishingservice"
PUBLISHING_SERVICE_USERNAME = "Publishing Service"
OISTATUS_SECTION = "oistatusid"


def handle_foiministryrequest_update(payload, oistatus_id, section_updater):
    missing = [
        field
        for field in ("foirequest_id", "foiministryrequest_id")
        if not payload.get(field)
    ]
    if missing:
        return DefaultMethodResult(
            False,
            f"Missing required payload fields: {', '.join(missing)}",
        )

    result = section_updater.update_section(
        payload.get("foirequest_id"),
        payload.get("foiministryrequest_id"),
        OISTATUS_SECTION,
        {OISTATUS_SECTION: oistatus_id},
        PUBLISHING_SERVICE_USER_ID,
        PUBLISHING_SERVICE_USERNAME,
        False,
    )
    response, status_code = result if isinstance(result, tuple) else (result, 200)
    if status_code < 400 and response is not None and response.get("success"):
        return DefaultMethodResult(True, "FOIMinistryRequest data updated")
    message = (
        response.get("message")
        if isinstance(response, dict) and response.get("message")
        else "Unable to update FOIMinistryRequest data"
    )
    return DefaultMethodResult(False, message)


class OpenInfoPublishCompletedConsumer:
    """Handles completed publication events for OpenInfo records."""

    _CORRELATION_ID_PATTERN = re.compile(r"^openinfo-publish-(?P<openinfo_id>\d+)$")

    def __init__(self, openinfo_model=None, section_updater=None):
        self.openinfo_model = openinfo_model or FOIOpenInformationRequests
        self.section_updater = section_updater or FOIRequestUpdateBySection()

    def _handle_foiministryrequest_update(self, payload):
        return handle_foiministryrequest_update(
            payload,
            OIStatusEnum.PUBLISHED.value,
            self.section_updater,
        )
        
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
        message = payload.get("message") or "Published"
        sitemap_page_key = payload.get("sitemap_page_key")

        logging.info(
            "Handling OpenInfo publish completed event | "
            f"event_id={envelope.get('event_id')} "
            f"correlation_id={correlation_id} "
            f"openinfo_id={openinfo_id} "
            f"request_event_id={payload.get('request_event_id')}"
        )
        update_result = self._handle_foiministryrequest_update(payload)

        if update_result.success is False:
            return update_result
        
        return self.openinfo_model.create_published_version_from_openinfo_id(openinfo_id, message, PurePosixPath(sitemap_page_key).name)


class OpenInfoUnpublishCompletedConsumer:
    """Logs completed unpublish events for OpenInfo records."""

    _CORRELATION_ID_PATTERN = re.compile(r"^openinfo-publish-(?P<openinfo_id>\d+)$")

    def __init__(self, openinfo_model=None, section_updater=None):
        self.section_updater = section_updater or FOIRequestUpdateBySection()
        self.openinfo_model = openinfo_model or FOIOpenInformationRequests

    def _handle_foiministryrequest_update(self, payload):
        return handle_foiministryrequest_update(
            payload,
            OIStatusEnum.UNPUBLISHED.value,
            self.section_updater,
        )
    
    def handle(self, envelope):
        """Validate and log a publication.unpublish.completed event for OpenInfo."""
        if envelope.get("event_type") != PublicationEventType.UNPUBLISH_COMPLETED:
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
        message = payload.get("message") or "Unpublished"
        
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
        update_result = self._handle_foiministryrequest_update(payload)

        if update_result.success is False:
            return update_result
    
        return self.openinfo_model.create_published_version_from_openinfo_id(openinfo_id, message, None)


class ProactiveDisclosurePublishCompletedConsumer:
    """Handles completed publication events for Proactive Disclosure records."""

    _CORRELATION_ID_PATTERN = re.compile(
        r"^proactivedisclosure-publish-(?P<proactive_id>\d+)$"
    )

    def __init__(self, proactive_model=None, section_updater=None):
        self.proactive_model = proactive_model or FOIProactiveDisclosureRequests
        self.section_updater = section_updater or FOIRequestUpdateBySection()
    
    def _handle_foiministryrequest_update(self, payload):
        return handle_foiministryrequest_update(
            payload,
            OIStatusEnum.PUBLISHED.value,
            self.section_updater,
        )

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
        message = payload.get("message") or "Published"
        sitemap_page_key = payload.get("sitemap_page_key")

        logging.info(
            "Handling Proactive Disclosure publish completed event | "
            f"event_id={envelope.get('event_id')} "
            f"correlation_id={correlation_id} "
            f"proactive_id={proactive_id} "
            f"request_event_id={payload.get('request_event_id')}"
        )
        update_result = self._handle_foiministryrequest_update(payload)

        if update_result.success is False:
            return update_result
        
        return self.proactive_model.create_published_version_from_proactive_id(
            proactive_id,
            message,
            PurePosixPath(sitemap_page_key).name
        )


class ProactiveDisclosureUnpublishCompletedConsumer:
    """Logs completed unpublish events for Proactive Disclosure records."""

    _CORRELATION_ID_PATTERN = re.compile(
        r"^proactivedisclosure-publish-(?P<proactive_id>\d+)$"
    )

    def __init__(self, proactive_model=None, section_updater=None):
        self.section_updater = section_updater or FOIRequestUpdateBySection()
        self.proactive_model = proactive_model or FOIProactiveDisclosureRequests

    def _handle_foiministryrequest_update(self, payload):
        return handle_foiministryrequest_update(
            payload,
            OIStatusEnum.UNPUBLISHED.value,
            self.section_updater,
        )
    
    def handle(self, envelope):
        """Validate and log a publication.unpublish.completed event for Proactive Disclosure."""
        if envelope.get("event_type") != PublicationEventType.UNPUBLISH_COMPLETED:
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
        message = payload.get("message") or "Unpublished"

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
        update_result = self._handle_foiministryrequest_update(payload)

        if update_result.success is False:
            return update_result

        return self.proactive_model.create_published_version_from_proactive_id(
            proactive_id,
            message,
            None
        )
