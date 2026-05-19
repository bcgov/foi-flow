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
from datetime import datetime


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


class OpenInfoPublicationCompletedConsumer:
    """Handles completed publication events for OpenInfo records."""

    _CORRELATION_ID_PATTERN = re.compile(r"^openinfo-publish-(?P<openinfo_id>\d+)$")

    def __init__(self, openinfo_model=None, section_updater=None):
        self.openinfo_model = openinfo_model or FOIOpenInformationRequests
        self.section_updater = section_updater or FOIRequestUpdateBySection()

    def _handle_foiministryrequest_update(self, payload, oistatusid):
        return handle_foiministryrequest_update(
            payload,
            oistatusid,
            self.section_updater,
        )
    
    def _get_sitemap(self, payload):
        sitemap_page_key = payload.get("sitemap_page_key")
        if not sitemap_page_key:
            raise ValueError("Publication API payload did not include sitemap_page_key")
        return PurePosixPath(sitemap_page_key).name

    def handle(self, envelope):
        """Validate publication event for OpenInfo."""
        event_type = envelope.get("event_type")
        if event_type != PublicationEventType.PUBLISH_COMPLETED and event_type != PublicationEventType.UNPUBLISH_COMPLETED:
            return DefaultMethodResult(False, "Unsupported event type")
        print("LOG:payload", envelope.get("payload"))
        print("LOG:eventtype", event_type)

        payload = envelope.get("payload") or {}
        missing = [field for field in ("tenant_id", "request_event_id") if not payload.get(field)]
        if missing:
            return DefaultMethodResult(False, f"Missing required payload fields: {', '.join(missing)}")

        correlation_id = envelope.get("correlation_id")
        match = self._CORRELATION_ID_PATTERN.match(correlation_id or "")
        if not match:
            return DefaultMethodResult(False, "Invalid OpenInfo publish correlation_id")

        openinfo_id = int(match.group("openinfo_id"))
        if event_type == PublicationEventType.PUBLISH_COMPLETED:
            message = "Published"
            sitemap = self._get_sitemap(payload)
            oistatusid = OIStatusEnum.PUBLISHED.value
            publicationdate = datetime.now()
        else:
            message = "Unpublished"
            sitemap = None
            oistatusid = OIStatusEnum.UNPUBLISHED.value
            publicationdate = None

        logging.info(
            "Handling OpenInfo publication completed event | "
            f"event_id={envelope.get('event_id')} "
            f"correlation_id={envelope.get('correlation_id')} "
            f"kind={payload.get('kind')} "
            f"publication_id={payload.get('publication_id')} "
            f"status={payload.get('status')}"
        )

        update_result = self._handle_foiministryrequest_update(payload, oistatusid)
        if update_result.success is False:
            return update_result
        
        return self.openinfo_model.create_published_version_from_openinfo_id(openinfo_id, message, sitemap, publicationdate)


class ProactiveDisclosurePublicationCompletedConsumer:
    """Handles completed publication events for Proactive Disclosure records."""

    _CORRELATION_ID_PATTERN = re.compile(
        r"^proactivedisclosure-publish-(?P<proactive_id>\d+)$"
    )

    def __init__(self, proactive_model=None, section_updater=None):
        self.proactive_model = proactive_model or FOIProactiveDisclosureRequests
        self.section_updater = section_updater or FOIRequestUpdateBySection()
    
    def _handle_foiministryrequest_update(self, payload, oistatusid):
        return handle_foiministryrequest_update(
            payload,
            oistatusid,
            self.section_updater,
        )
    
    def _get_sitemap(self, payload):
        sitemap_page_key = payload.get("sitemap_page_key")
        if not sitemap_page_key:
            raise ValueError("Publication API payload did not include sitemap_page_key")
        return PurePosixPath(sitemap_page_key).name

    def handle(self, envelope):
        """Validate publication event for Proactive Disclosure."""
        event_type = envelope.get("event_type")
        if event_type != PublicationEventType.PUBLISH_COMPLETED and event_type != PublicationEventType.UNPUBLISH_COMPLETED:
            return DefaultMethodResult(False, "Unsupported event type")
        print("LOG:payload", envelope.get("payload"))
        print("LOG:eventtype", event_type)

        payload = envelope.get("payload") or {}
        missing = [field for field in ("tenant_id", "request_event_id") if not payload.get(field)]
        if missing:
            return DefaultMethodResult(False, f"Missing required payload fields: {', '.join(missing)}")

        correlation_id = envelope.get("correlation_id")
        match = self._CORRELATION_ID_PATTERN.match(correlation_id or "")
        if not match:
            return DefaultMethodResult(False, "Invalid Proactive Disclosure publish correlation_id")

        proactive_id = int(match.group("proactive_id"))
        if event_type == PublicationEventType.PUBLISH_COMPLETED:
            message = "Published"
            sitemap = self._get_sitemap(payload)
            oistatusid = OIStatusEnum.PUBLISHED.value
            publicationdate = datetime.now()
        else:
            message = "Unpublished"
            sitemap = None
            oistatusid = OIStatusEnum.UNPUBLISHED.value
            publicationdate = None
        
        logging.info(
            "Handling Proactive Disclosure publication completed event | "
            f"event_id={envelope.get('event_id')} "
            f"correlation_id={envelope.get('correlation_id')} "
            f"kind={payload.get('kind')} "
            f"publication_id={payload.get('publication_id')} "
            f"status={payload.get('status')}"
        )

        update_result = self._handle_foiministryrequest_update(payload, oistatusid)
        if update_result.success is False:
            return update_result
        
        return self.proactive_model.create_published_version_from_proactive_id(
            proactive_id,
            message,
            sitemap,
            publicationdate
        )
