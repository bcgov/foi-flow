"""Scheduled publication orchestration for OpenInfo pre-publishing."""

import logging

from request_api.models.FOIOpenInformationRequests import FOIOpenInformationRequests
from request_api.services.publication_events.envelope import EventEnvelopeFactory
from request_api.services.publication_events.mappers import OpenInfoPublishRequestedMapper
from request_api.services.publication_events.publisher import PublicationEventPublisher
from request_api.services.publication_events.types import PublicationEventType


class ScheduledPublicationService:
    """Publishes all OpenInfo rows that are due for pre-publishing."""

    def __init__(
        self,
        openinfo_model=None,
        envelope_factory=None,
        publisher=None,
        openinfo_mapper=None,
    ):
        self.openinfo_model = openinfo_model or FOIOpenInformationRequests
        self.envelope_factory = envelope_factory or EventEnvelopeFactory()
        self.publisher = publisher or PublicationEventPublisher()
        self.openinfo_mapper = openinfo_mapper or OpenInfoPublishRequestedMapper()

    def publish_due_openinfo_records(self):
        rows = self.openinfo_model.getopeninforecordsforprepublishing()
        if not rows:
            logging.info("OpenInfo pre-publishing scheduler found no publishable rows")
            return []

        results = []
        for row in rows:
            payload = self.openinfo_mapper.map(row)
            envelope = self.envelope_factory.create(
                PublicationEventType.OPENINFO_PUBLISH_REQUESTED,
                self.openinfo_mapper.correlation_id(row),
                payload.to_dict(),
            )
            results.append(self.publisher.publish(envelope))
        return results
