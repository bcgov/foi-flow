"""Orchestrates unpublish event emission."""

import logging

from request_api.models.default_method_result import DefaultMethodResult
from request_api.services.openinfoservice import openinfoservice
from request_api.services.publication_events.envelope import EventEnvelopeFactory
from request_api.services.publication_events.mappers import UnpublishRequestedMapper
from request_api.services.publication_events.publisher import PublicationEventPublisher
from request_api.services.publication_events.types import PublicationEventType


class UnpublishEventService:
    """Builds and publishes unpublish event envelopes."""

    def __init__(
        self,
        openinfo_service=None,
        envelope_factory=None,
        publisher=None,
        mapper=None,
    ):
        self.openinfo_service = openinfo_service or openinfoservice()
        self.envelope_factory = envelope_factory or EventEnvelopeFactory()
        self.publisher = publisher or PublicationEventPublisher()
        self.mapper = mapper or UnpublishRequestedMapper()

    def _queue_unpublish(self, rows, publication_type, foiministryrequestid):
        if not rows:
            logging.info(
                "No data found to unpublish",
                extra={
                    "publication_type": publication_type,
                    "foiministryrequestid": foiministryrequestid,
                },
            )
            return DefaultMethodResult(True, "No data found to unpublish for this request")

        row = rows[0]
        payload = self.mapper.map(row, publication_type=publication_type)
        correlation_id = self.mapper.correlation_id(row, publication_type=publication_type)
        envelope = self.envelope_factory.create(
            PublicationEventType.UNPUBLISH_REQUESTED,
            correlation_id,
            payload.to_dict(),
        )
        logging.info(
            "Unpublish event envelope created",
            extra={
                "publication_type": publication_type,
                "foiministryrequestid": foiministryrequestid,
                "event_id": envelope.event_id,
                "event_type": envelope.event_type,
                "correlation_id": envelope.correlation_id,
            },
        )
        return self.publisher.publish(envelope)

    def queue_openinfo_unpublish(self, foiministryrequestid):
        rows = self.openinfo_service.getopeninforequestforunpublishing(foiministryrequestid)
        return self._queue_unpublish(
            rows,
            publication_type="openinfo",
            foiministryrequestid=foiministryrequestid,
        )

    def queue_pd_unpublish(self, foiministryrequestid):
        rows = self.openinfo_service.getpdopeninforequestforunpublishing(foiministryrequestid)
        return self._queue_unpublish(
            rows,
            publication_type="proactivedisclosure",
            foiministryrequestid=foiministryrequestid,
        )
