"""Scheduled publication orchestration for OpenInfo and Proactive Disclosure pre-publishing."""

import logging

from request_api.models.FOIOpenInformationRequests import FOIOpenInformationRequests
from request_api.models.FOIProactiveDisclosureRequests import FOIProactiveDisclosureRequests
from request_api.services.publication_events.envelope import EventEnvelopeFactory
from request_api.services.publication_events.mappers import (
    OpenInfoPublishRequestedMapper,
    ProactiveDisclosurePublishRequestedMapper,
)
from request_api.services.publication_events.publisher import PublicationEventPublisher
from request_api.services.publication_events.types import PublicationEventType


class ScheduledPublicationService:
    """Publishes all OpenInfo and PD rows that are due for pre-publishing."""

    def __init__(
        self,
        openinfo_model=None,
        envelope_factory=None,
        publisher=None,
        openinfo_mapper=None,
        pd_model=None,
        pd_mapper=None,
    ):
        self.openinfo_model = openinfo_model or FOIOpenInformationRequests
        self.envelope_factory = envelope_factory or EventEnvelopeFactory()
        self.publisher = publisher or PublicationEventPublisher()
        self.openinfo_mapper = openinfo_mapper or OpenInfoPublishRequestedMapper()
        self.pd_model = pd_model or FOIProactiveDisclosureRequests
        self.pd_mapper = pd_mapper or ProactiveDisclosurePublishRequestedMapper()

    def publish_due_openinfo_records(self):
        rows = self.openinfo_model.getopeninforecordsforprepublishing()
        if not rows:
            logging.info("OpenInfo publishing scheduler found no publishable rows")
            return []

        results = []
        for row in rows:
            payload = self.openinfo_mapper.map(row)
            envelope = self.envelope_factory.create(
                PublicationEventType.PUBLISH_REQUESTED,
                self.openinfo_mapper.correlation_id(row),
                payload.to_dict(),
            )
            results.append(self.publisher.publish(envelope))
        return results

    def publish_due_pd_records(self):
        rows = self.pd_model.getpdrecordsforprepublishing()
        if not rows:
            logging.info("PD publishing scheduler found no publishable rows")
            return []

        results = []
        for row in rows:
            payload = self.pd_mapper.map(row)
            envelope = self.envelope_factory.create(
                PublicationEventType.PUBLISH_REQUESTED,
                self.pd_mapper.correlation_id(row),
                payload.to_dict(),
            )
            results.append(self.publisher.publish(envelope))
        return results

    def publish_all_due_records(self):
        oi_results = self.publish_due_openinfo_records()
        pd_results = self.publish_due_pd_records()
        return oi_results + pd_results
