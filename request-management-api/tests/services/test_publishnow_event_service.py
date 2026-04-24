import json
import uuid

from request_api.models.default_method_result import DefaultMethodResult
from request_api.services.publication_events.service import PublishNowEventService
from request_api.services.publication_events.types import PublicationEventType


class FakePublisher:
    def __init__(self):
        self.published_envelopes = []

    def publish(self, envelope):
        self.published_envelopes.append(envelope)
        return DefaultMethodResult(True, "Request queued for publishing successfully", "1-0")


class FakeOpenInfoService:
    def __init__(self, openinfo_rows=None, proactive_row=None):
        self.openinfo_rows = openinfo_rows or []
        self.proactive_row = proactive_row

    def getopeninforequestforpublishing(self, foiministryrequestid):
        return self.openinfo_rows

    def getpdopeninforequestforpublishing(self, foiministryrequestid):
        return self.proactive_row


def test_queue_openinfo_publishnow_builds_openinfo_envelope():
    publisher = FakePublisher()
    service = PublishNowEventService(
        openinfo_service=FakeOpenInfoService(
            openinfo_rows=[
                {
                    "openinfoid": 345,
                    "axisrequestid": "FIN-2026-047533",
                    "description": "Budget briefing records",
                    "published_date": "2026-04-20",
                    "contributor": "Ministry of Finance",
                    "fees": 0,
                    "applicant_type": "Media",
                    "bcgovcode": "fin",
                }
            ]
        ),
        publisher=publisher,
    )

    result = service.queue_openinfo_publishnow(22318)

    assert result.success is True
    assert result.identifier == "1-0"
    envelope = publisher.published_envelopes[0].to_dict()
    assert envelope["event_type"] == PublicationEventType.OPENINFO_PUBLISH_REQUESTED
    assert envelope["correlation_id"] == "openinfo-publish-345"
    assert envelope["payload"]["tenant_id"] == str(uuid.uuid5(uuid.NAMESPACE_DNS, "bcgov:fin"))
    assert envelope["payload"]["axis_request_id"] == "FIN-2026-047533"
    assert envelope["payload"]["source"]["bucket"] == "fin-dev-e"
    assert envelope["payload"]["destination"]["prefix"] == "openinfo/published/"


def test_queue_proactive_disclosure_publishnow_builds_pd_envelope():
    publisher = FakePublisher()
    service = PublishNowEventService(
        openinfo_service=FakeOpenInfoService(
            proactive_row={
                "proactivedisclosureid": 71,
                "axisrequestid": "PD-FIN-2026-047533",
                "description": "Ministerial Directive",
                "published_date": "2026-04-20",
                "contributor": "Ministry of Finance",
                "fees": 0,
                "applicant_type": None,
                "bcgovcode": "fin",
                "proactivedisclosurecategory": "Calendars",
                "reportperiod": "Quarter 1 2026-27",
            }
        ),
        publisher=publisher,
    )

    result = service.queue_proactive_disclosure_publishnow(22318)

    assert result.success is True
    assert result.identifier == "1-0"
    envelope = publisher.published_envelopes[0].to_dict()
    assert envelope["event_type"] == PublicationEventType.PROACTIVE_DISCLOSURE_PUBLISH_REQUESTED
    assert envelope["correlation_id"] == "proactivedisclosure-publish-71"
    assert envelope["payload"]["tenant_id"] == str(uuid.uuid5(uuid.NAMESPACE_DNS, "bcgov:fin"))
    assert envelope["payload"]["proactivedisclosure_category"] == "Calendars"
    assert envelope["payload"]["report_period"] == "Quarter 1 2026-27"


def test_publication_event_publisher_serializes_envelope(monkeypatch):
    from request_api.services.publication_events.envelope import EventEnvelopeFactory
    from request_api.services.publication_events.publisher import PublicationEventPublisher
    from request_api.services.publication_events.types import PublicationEventType

    class FakeQueueService:
        def __init__(self):
            self.calls = []

        def add_publication_stream_message(self, stream_name, payload):
            self.calls.append((stream_name, payload))
            return DefaultMethodResult(True, "Added to stream", "2-0")

    monkeypatch.setenv("OPENINFO_REDIS_STREAM_NAME", "fallback.publish.requested")
    monkeypatch.setenv("OPENINFO_PUBLISH_STREAM_NAME", "openinfo.publish.requested")
    monkeypatch.setenv("PROACTIVEDISCLOSURE_PUBLISH_STREAM_NAME", "proactivedisclosure.publish.requested")

    queue_service = FakeQueueService()
    publisher = PublicationEventPublisher(queue_service=queue_service)
    envelope = EventEnvelopeFactory().create(
        PublicationEventType.PROACTIVE_DISCLOSURE_PUBLISH_REQUESTED,
        "corr-1",
        {"hello": "world"},
    )

    result = publisher.publish(envelope)

    assert result.success is True
    assert queue_service.calls[0][0] == "proactivedisclosure.publish.requested"
    serialized_payload = queue_service.calls[0][1]
    message = json.loads(serialized_payload)
    assert message["event_type"] == PublicationEventType.PROACTIVE_DISCLOSURE_PUBLISH_REQUESTED
    assert message["payload"]["hello"] == "world"


def test_publication_event_publisher_routes_openinfo_to_openinfo_stream(monkeypatch):
    from request_api.services.publication_events.envelope import EventEnvelopeFactory
    from request_api.services.publication_events.publisher import PublicationEventPublisher
    from request_api.services.publication_events.types import PublicationEventType

    class FakeQueueService:
        def __init__(self):
            self.calls = []

        def add_publication_stream_message(self, stream_name, payload):
            self.calls.append((stream_name, payload))
            return DefaultMethodResult(True, "Added to stream", "3-0")

    monkeypatch.setenv("OPENINFO_PUBLISH_STREAM_NAME", "openinfo.publish.requested")
    monkeypatch.setenv("PROACTIVEDISCLOSURE_PUBLISH_STREAM_NAME", "proactivedisclosure.publish.requested")

    queue_service = FakeQueueService()
    publisher = PublicationEventPublisher(queue_service=queue_service)
    envelope = EventEnvelopeFactory().create(
        PublicationEventType.OPENINFO_PUBLISH_REQUESTED,
        "corr-2",
        {"hello": "openinfo"},
    )

    result = publisher.publish(envelope)

    assert result.success is True
    assert queue_service.calls[0][0] == "openinfo.publish.requested"


def test_publication_event_publisher_requires_configured_stream(monkeypatch):
    from request_api.services.publication_events.envelope import EventEnvelopeFactory
    from request_api.services.publication_events.publisher import PublicationEventPublisher
    from request_api.services.publication_events.types import PublicationEventType

    monkeypatch.delenv("OPENINFO_PUBLISH_STREAM_NAME", raising=False)
    monkeypatch.delenv("PROACTIVEDISCLOSURE_PUBLISH_STREAM_NAME", raising=False)
    monkeypatch.delenv("OPENINFO_REDIS_STREAM_NAME", raising=False)

    publisher = PublicationEventPublisher(queue_service=object())
    envelope = EventEnvelopeFactory().create(
        PublicationEventType.PROACTIVE_DISCLOSURE_PUBLISH_REQUESTED,
        "corr-3",
        {"hello": "missing-config"},
    )

    try:
        publisher.publish(envelope)
        assert False, "Expected ValueError when no stream is configured"
    except ValueError as exc:
        assert "No Redis stream configured" in str(exc)


def test_publication_event_publisher_normalizes_exception_messages(monkeypatch):
    from request_api.services.publication_events.envelope import EventEnvelopeFactory
    from request_api.services.publication_events.publisher import PublicationEventPublisher
    from request_api.services.publication_events.types import PublicationEventType

    class FakeQueueService:
        def add_publication_stream_message(self, stream_name, payload):
            return DefaultMethodResult(False, TimeoutError("timed out waiting for Redis stream"), -1)

    monkeypatch.setenv("PROACTIVEDISCLOSURE_PUBLISH_STREAM_NAME", "proactivedisclosure.publish.requested")

    publisher = PublicationEventPublisher(queue_service=FakeQueueService())
    envelope = EventEnvelopeFactory().create(
        PublicationEventType.PROACTIVE_DISCLOSURE_PUBLISH_REQUESTED,
        "corr-timeout",
        {"hello": "timeout"},
    )

    result = publisher.publish(envelope)

    assert result.success is False
    assert result.identifier == -1
    assert result.message == "TimeoutError: timed out waiting for Redis stream"
