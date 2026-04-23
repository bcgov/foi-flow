"""Orchestrates /publishnow publication events."""

import logging

from request_api.models.default_method_result import DefaultMethodResult
from request_api.services.openinfoservice import openinfoservice
from request_api.services.publication_events.envelope import EventEnvelopeFactory
from request_api.services.publication_events.mappers import (
    OpenInfoPublishRequestedMapper,
    ProactiveDisclosurePublishRequestedMapper,
)
from request_api.services.publication_events.publisher import PublicationEventPublisher
from request_api.services.publication_events.types import PublicationEventType


class PublishNowEventService:
    """Builds and publishes production event envelopes for publish-now endpoints."""

    def __init__(
        self,
        openinfo_service=None,
        envelope_factory=None,
        publisher=None,
        openinfo_mapper=None,
        proactive_disclosure_mapper=None,
    ):
        self.openinfo_service = openinfo_service or openinfoservice()
        self.envelope_factory = envelope_factory or EventEnvelopeFactory()
        self.publisher = publisher or PublicationEventPublisher()
        self.openinfo_mapper = openinfo_mapper or OpenInfoPublishRequestedMapper()
        self.proactive_disclosure_mapper = proactive_disclosure_mapper or ProactiveDisclosurePublishRequestedMapper()

    def queue_openinfo_publishnow(self, foiministryrequestid):
        rows = self.openinfo_service.getopeninforequestforpublishing(foiministryrequestid)
        if not rows:
            return DefaultMethodResult(True, "No data found to publish for this request")

        row = rows[0]
        payload = self.openinfo_mapper.map(row)
        envelope = self.envelope_factory.create(
            PublicationEventType.OPENINFO_PUBLISH_REQUESTED,
            self.openinfo_mapper.correlation_id(row),
            payload.to_dict(),
        )
        return self.publisher.publish(envelope)

    def queue_proactive_disclosure_publishnow(self, foiministryrequestid):
        logging.info(
            "Fetching proactive disclosure publish-now source row",
            extra={"foiministryrequestid": foiministryrequestid},
        )
        row = self.openinfo_service.getpdopeninforequestforpublishing(foiministryrequestid)
        if not row:
            logging.info(
                "No proactive disclosure publish-now source row found",
                extra={"foiministryrequestid": foiministryrequestid},
            )
            return DefaultMethodResult(True, "No data found to publish for this request")

        logging.info(
            "Proactive disclosure publish-now source row fetched",
            extra={
                "foiministryrequestid": foiministryrequestid,
                "proactivedisclosureid": row.get("proactivedisclosureid"),
                "axisrequestid": row.get("axisrequestid"),
                "bcgovcode": row.get("bcgovcode"),
            },
        )
        payload = self.proactive_disclosure_mapper.map(row)
        correlation_id = self.proactive_disclosure_mapper.correlation_id(row)
        payload_dict = payload.to_dict()
        logging.info(
            "Proactive disclosure publish-now payload mapped",
            extra={
                "foiministryrequestid": foiministryrequestid,
                "proactivedisclosureid": row.get("proactivedisclosureid"),
                "correlation_id": correlation_id,
                "tenant_id": payload_dict.get("tenant_id"),
                "source_bucket": payload_dict.get("source", {}).get("bucket"),
                "destination_bucket": payload_dict.get("destination", {}).get("bucket"),
            },
        )
        envelope = self.envelope_factory.create(
            PublicationEventType.PROACTIVE_DISCLOSURE_PUBLISH_REQUESTED,
            correlation_id,
            payload_dict,
        )
        logging.info(
            "Proactive disclosure publish-now envelope created",
            extra={
                "foiministryrequestid": foiministryrequestid,
                "proactivedisclosureid": row.get("proactivedisclosureid"),
                "event_id": envelope.event_id,
                "event_type": envelope.event_type,
                "correlation_id": envelope.correlation_id,
            },
        )
        result = self.publisher.publish(envelope)
        logging.info(
            "Proactive disclosure publish-now publish step completed",
            extra={
                "foiministryrequestid": foiministryrequestid,
                "proactivedisclosureid": row.get("proactivedisclosureid"),
                "event_id": envelope.event_id,
                "queue_identifier": result.identifier,
                "publish_success": result.success,
                "publish_message": result.message,
            },
        )
        return result
