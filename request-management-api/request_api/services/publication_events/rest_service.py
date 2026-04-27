"""Synchronous REST orchestration for publish-now endpoints."""

import logging
from pathlib import PurePosixPath

from request_api.models.FOIOpenInformationRequests import FOIOpenInformationRequests
from request_api.models.FOIProactiveDisclosureRequests import FOIProactiveDisclosureRequests
from request_api.models.default_method_result import DefaultMethodResult
from request_api.services.openinfoservice import openinfoservice
from request_api.services.publication_events.mappers import (
    OpenInfoPublishRequestedMapper,
    ProactiveDisclosurePublishRequestedMapper,
)
from request_api.services.publication_events.rest_client import PublicationRestClient


REST_PAYLOAD_FIELDS = {
    "tenant_id",
    "axis_request_id",
    "description",
    "published_date",
    "contributor",
    "fees",
    "applicant_type",
    "proactivedisclosure_category",
    "report_period",
    "source",
    "destination",
}


class PublicationStatusUpdater:
    """Persists successful publication REST metadata."""

    def mark_openinfo_ready_for_crawling(self, foiministryrequestid, sitemap_page):
        return FOIOpenInformationRequests.mark_ready_for_crawling(foiministryrequestid, sitemap_page)

    def mark_proactive_disclosure_ready_for_crawling(self, foiministryrequestid, sitemap_page):
        return FOIProactiveDisclosureRequests.mark_ready_for_crawling(foiministryrequestid, sitemap_page)


class PublishNowRestService:
    """Publishes current OpenInfo and Proactive Disclosure rows through REST."""

    def __init__(
        self,
        openinfo_service=None,
        publication_client=None,
        publication_status_updater=None,
        openinfo_mapper=None,
        proactive_disclosure_mapper=None,
    ):
        self.openinfo_service = openinfo_service or openinfoservice()
        self.publication_client = publication_client or PublicationRestClient()
        self.publication_status_updater = publication_status_updater or PublicationStatusUpdater()
        self.openinfo_mapper = openinfo_mapper or OpenInfoPublishRequestedMapper()
        self.proactive_disclosure_mapper = proactive_disclosure_mapper or ProactiveDisclosurePublishRequestedMapper()

    @staticmethod
    def _sitemap_page_name(response):
        sitemap_page_key = response.get("sitemap_page_key")
        if not sitemap_page_key:
            raise ValueError("Publication API response did not include sitemap_page_key")
        return PurePosixPath(sitemap_page_key).name

    @staticmethod
    def _validate_completed(response):
        if response.get("status") != "completed":
            message = response.get("message") or response.get("status") or "unknown"
            raise ValueError(f"Publication API did not complete: {message}")

    @staticmethod
    def _rest_payload(payload):
        return {key: value for key, value in payload.items() if key in REST_PAYLOAD_FIELDS}

    def _publish_and_update(self, publication_type, row, payload, update_status):
        try:
            response = self.publication_client.publish(publication_type, payload)
            self._validate_completed(response)
            sitemap_page = self._sitemap_page_name(response)
            update_result = update_status(sitemap_page)
            if not update_result.success:
                return update_result
            return DefaultMethodResult(
                True,
                "Request published successfully",
                response.get("publication_id"),
            )
        except Exception as exception:
            logging.exception(
                "Publication REST integration failed",
                extra={
                    "publication_type": publication_type,
                    "foiministryrequestid": row.get("foiministryrequestid"),
                    "axisrequestid": row.get("axisrequestid"),
                },
            )
            return DefaultMethodResult(False, str(exception))

    def publish_openinfo_now(self, foiministryrequestid):
        rows = self.openinfo_service.getopeninforequestforpublishing(foiministryrequestid)
        if not rows:
            return DefaultMethodResult(True, "No data found to publish for this request")

        row = rows[0]
        payload = self.openinfo_mapper.map(row).to_dict()
        return self._publish_and_update(
            "openinfo",
            row,
            payload,
            lambda sitemap_page: self.publication_status_updater.mark_openinfo_ready_for_crawling(
                foiministryrequestid,
                sitemap_page,
            ),
        )

    def publish_proactive_disclosure_now(self, foiministryrequestid):
        row = self.openinfo_service.getpdopeninforequestforpublishing(foiministryrequestid)
        if not row:
            return DefaultMethodResult(True, "No data found to publish for this request")

        payload = self._rest_payload(self.proactive_disclosure_mapper.map(row).to_dict())
        return self._publish_and_update(
            "proactivedisclosure",
            row,
            payload,
            lambda sitemap_page: self.publication_status_updater.mark_proactive_disclosure_ready_for_crawling(
                foiministryrequestid,
                sitemap_page,
            ),
        )
