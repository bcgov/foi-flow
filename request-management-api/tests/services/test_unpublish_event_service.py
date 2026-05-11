"""Tests for the unpublish event emission pipeline."""

import json
import uuid

from request_api.models.default_method_result import DefaultMethodResult
from request_api.services.publication_events.envelope import EventEnvelopeFactory
from request_api.services.publication_events.mappers import UnpublishRequestedMapper
from request_api.services.publication_events.payloads import (
    S3Location,
    UnpublishRequestedPayload,
)
from request_api.services.publication_events.publisher import PublicationEventPublisher
from request_api.services.publication_events.types import PublicationEventType


# --- Task 1: Event type constants ---


def test_unified_event_type_constants_exist():
    from request_api.services.publication_events.types import PublicationEventType, PublicationKind

    assert PublicationEventType.PUBLISH_REQUESTED == "publication.publish.requested"
    assert PublicationEventType.PUBLISH_COMPLETED == "publication.publish.completed"
    assert PublicationEventType.UNPUBLISH_REQUESTED == "publication.unpublish.requested"
    assert PublicationEventType.UNPUBLISH_COMPLETED == "publication.unpublish.completed"
    assert PublicationKind.OPENINFO == "openinfo"
    assert PublicationKind.PROACTIVE_DISCLOSURE == "proactivedisclosure"

    # Old constants must not exist
    assert not hasattr(PublicationEventType, "OPENINFO_PUBLISH_REQUESTED")
    assert not hasattr(PublicationEventType, "PROACTIVE_DISCLOSURE_PUBLISH_REQUESTED")
    assert not hasattr(PublicationEventType, "OPENINFO_UNPUBLISH_REQUESTED")
    assert not hasattr(PublicationEventType, "PROACTIVE_DISCLOSURE_UNPUBLISH_REQUESTED")


# --- Task 2: Payload kind field ---


def test_unpublish_requested_payload_includes_kind():
    payload = UnpublishRequestedPayload(
        tenant_id="tenant-abc",
        publication_id="EDU-2024-12345",
        public_url="https://openinfo.gov.bc.ca/public/EDU-2024-12345.html",
        public_repository=S3Location(bucket="pub-bucket", prefix="openinfo/EDU-2024-12345"),
        last_modified="2026-04-27",
        kind="openinfo",
    )

    result = payload.to_dict()
    assert result["kind"] == "openinfo"


def test_openinfo_publish_payload_includes_kind():
    from request_api.services.publication_events.payloads import (
        OpenInfoPublishRequestedPayload,
    )

    payload = OpenInfoPublishRequestedPayload(
        tenant_id="tenant-abc",
        axis_request_id="EDU-2024-12345",
        source=S3Location(bucket="src", prefix="p/"),
        destination=S3Location(bucket="dst", prefix="q/"),
        kind="openinfo",
    )

    result = payload.to_dict()
    assert result["kind"] == "openinfo"


def test_proactive_disclosure_publish_payload_includes_kind():
    from request_api.services.publication_events.payloads import (
        ProactiveDisclosurePublishRequestedPayload,
    )

    payload = ProactiveDisclosurePublishRequestedPayload(
        tenant_id="tenant-abc",
        axis_request_id="PD-2024-001",
        source=S3Location(bucket="src", prefix="p/"),
        destination=S3Location(bucket="dst", prefix="q/"),
        kind="proactivedisclosure",
    )

    result = payload.to_dict()
    assert result["kind"] == "proactivedisclosure"


# --- Task 2b: UnpublishRequestedPayload ---


def test_unpublish_requested_payload_to_dict():
    payload = UnpublishRequestedPayload(
        tenant_id="tenant-abc",
        publication_id="EDU-2024-12345",
        public_url="https://openinfo.gov.bc.ca/public/EDU-2024-12345.html",
        public_repository=S3Location(bucket="pub-bucket", prefix="openinfo/EDU-2024-12345"),
        last_modified="2026-04-27",
        foirequest_id=200,
        foiministryrequest_id=100,
    )

    result = payload.to_dict()

    assert result == {
        "tenant_id": "tenant-abc",
        "publication_id": "EDU-2024-12345",
        "public_url": "https://openinfo.gov.bc.ca/public/EDU-2024-12345.html",
        "public_repository": {"bucket": "pub-bucket", "prefix": "openinfo/EDU-2024-12345"},
        "last_modified": "2026-04-27",
        "foirequest_id": 200,
        "foiministryrequest_id": 100,
        "kind": "openinfo",
    }


# --- Task 3: Mapper kind ---


def test_unpublish_mapper_sets_kind_for_openinfo(monkeypatch):
    monkeypatch.setenv("OPENINFO_PUBLICATION_BUCKET", "dev-openinfopub")
    monkeypatch.setenv("PUBLICATION_PUBLIC_BASE_URL", "https://openinfo.gov.bc.ca")

    mapper = UnpublishRequestedMapper()
    row = {
        "openinfoid": 42,
        "axisrequestid": "EDU-2024-12345",
        "bcgovcode": "edu",
        "publicationdate": "2026-04-27",
    }
    payload = mapper.map(row, publication_type="openinfo")
    assert payload.kind == "openinfo"


def test_unpublish_mapper_sets_kind_for_proactivedisclosure(monkeypatch):
    monkeypatch.setenv("OPENINFO_PUBLICATION_BUCKET", "dev-openinfopub")
    monkeypatch.setenv("PUBLICATION_PUBLIC_BASE_URL", "https://openinfo.gov.bc.ca")

    mapper = UnpublishRequestedMapper()
    row = {
        "proactivedisclosureid": 99,
        "axisrequestid": "PD-FIN-2026-001",
        "bcgovcode": "fin",
        "publicationdate": "2026-04-20",
    }
    payload = mapper.map(row, publication_type="proactivedisclosure")
    assert payload.kind == "proactivedisclosure"


# --- Task 3b: UnpublishRequestedMapper ---


def test_unpublish_mapper_maps_openinfo_row(monkeypatch):
    monkeypatch.setenv("OPENINFO_PUBLICATION_BUCKET", "dev-openinfopub")
    monkeypatch.setenv(
        "PUBLICATION_PUBLIC_BASE_URL",
        "https://citz-foi-prod.objectstore.gov.bc.ca/dev-openinfopub/packages",
    )

    mapper = UnpublishRequestedMapper()
    row = {
        "openinfoid": 42,
        "axisrequestid": "EDU-2024-12345",
        "bcgovcode": "edu",
        "publicationdate": "2026-04-27",
    }

    payload = mapper.map(row, publication_type="openinfo")

    assert payload.tenant_id == str(uuid.uuid5(uuid.NAMESPACE_DNS, "bcgov:edu"))
    assert payload.publication_id == "EDU-2024-12345"
    assert (
        payload.public_url
        == "https://citz-foi-prod.objectstore.gov.bc.ca/dev-openinfopub/packages/EDU-2024-12345/openinfo/EDU-2024-12345.html"
    )
    assert payload.public_repository.bucket == "dev-openinfopub"
    assert payload.public_repository.prefix == "openinfo/EDU-2024-12345"
    assert payload.last_modified == "2026-04-27"


def test_unpublish_mapper_maps_pd_row(monkeypatch):
    monkeypatch.setenv("OPENINFO_PUBLICATION_BUCKET", "dev-openinfopub")
    monkeypatch.setenv(
        "PUBLICATION_PUBLIC_BASE_URL",
        "https://citz-foi-prod.objectstore.gov.bc.ca/dev-openinfopub/packages",
    )

    mapper = UnpublishRequestedMapper()
    row = {
        "proactivedisclosureid": 99,
        "axisrequestid": "PD-FIN-2026-001",
        "bcgovcode": "fin",
        "publicationdate": "2026-04-20",
    }

    payload = mapper.map(row, publication_type="proactivedisclosure")

    assert payload.tenant_id == str(uuid.uuid5(uuid.NAMESPACE_DNS, "bcgov:fin"))
    assert payload.publication_id == "PD-FIN-2026-001"
    assert (
        payload.public_url
        == "https://citz-foi-prod.objectstore.gov.bc.ca/dev-openinfopub/packages/PD-FIN-2026-001/openinfo/PD-FIN-2026-001.html"
    )
    assert payload.public_repository.prefix == "proactivedisclosure/PD-FIN-2026-001"
    assert payload.last_modified == "2026-04-20"


def test_unpublish_mapper_correlation_id_openinfo():
    row = {"openinfoid": 42}
    assert UnpublishRequestedMapper.correlation_id(row, "openinfo") == "openinfo-unpublish-42"


def test_unpublish_mapper_correlation_id_pd():
    row = {"proactivedisclosureid": 99}
    assert UnpublishRequestedMapper.correlation_id(row, "proactivedisclosure") == "proactivedisclosure-unpublish-99"


def test_unpublish_mapper_handles_missing_publicationdate(monkeypatch):
    monkeypatch.setenv("OPENINFO_PUBLICATION_BUCKET", "dev-openinfopub")
    monkeypatch.setenv("PUBLICATION_PUBLIC_BASE_URL", "https://openinfo.gov.bc.ca")

    mapper = UnpublishRequestedMapper()
    row = {
        "openinfoid": 1,
        "axisrequestid": "EDU-2024-00001",
        "bcgovcode": "edu",
    }

    payload = mapper.map(row, publication_type="openinfo")
    assert payload.last_modified == ""


# --- Task 4: Publisher unpublish stream routing ---


class FakeQueueService:
    def __init__(self):
        self.calls = []

    def add_publication_stream_message(self, stream_name, payload):
        self.calls.append((stream_name, payload))
        return DefaultMethodResult(True, "Added to stream", "1-0")


def test_publisher_routes_unpublish_to_unified_stream(monkeypatch):
    monkeypatch.setenv("PUBLICATION_UNPUBLISH_STREAM_NAME", "publication.unpublish.requested")

    queue_service = FakeQueueService()
    publisher = PublicationEventPublisher(queue_service=queue_service)
    envelope = EventEnvelopeFactory().create(
        PublicationEventType.UNPUBLISH_REQUESTED,
        "corr-unpublish-1",
        {"kind": "openinfo", "publication_id": "EDU-2024-12345"},
    )

    result = publisher.publish(envelope)

    assert result.success is True
    assert queue_service.calls[0][0] == "publication.unpublish.requested"


def test_publisher_requires_configured_unpublish_stream(monkeypatch):
    monkeypatch.delenv("PUBLICATION_UNPUBLISH_STREAM_NAME", raising=False)
    monkeypatch.delenv("PUBLICATION_PUBLISH_STREAM_NAME", raising=False)

    publisher = PublicationEventPublisher(queue_service=object())
    envelope = EventEnvelopeFactory().create(
        PublicationEventType.UNPUBLISH_REQUESTED,
        "corr-fallback",
        {"kind": "openinfo", "publication_id": "EDU-2024-99999"},
    )

    try:
        publisher.publish(envelope)
        assert False, "Expected ValueError when no stream is configured"
    except ValueError as exc:
        assert "No Redis stream configured" in str(exc)


# --- Task 5: UnpublishEventService ---


class FakePublisher:
    def __init__(self, success=True):
        self.published_envelopes = []
        self._success = success

    def publish(self, envelope):
        self.published_envelopes.append(envelope)
        if self._success:
            return DefaultMethodResult(True, "Request queued for unpublishing successfully", "1-0")
        return DefaultMethodResult(False, "Redis connection refused", -1)


class FakeOpenInfoService:
    def __init__(self, openinfo_rows=None, pd_rows=None):
        self.openinfo_rows = openinfo_rows or []
        self.pd_rows = pd_rows or []

    def getopeninforequestforunpublishing(self, foiministryrequestid):
        return self.openinfo_rows

    def getpdopeninforequestforunpublishing(self, foiministryrequestid):
        return self.pd_rows


def test_queue_openinfo_unpublish_builds_correct_envelope(monkeypatch):
    monkeypatch.setenv("OPENINFO_PUBLICATION_BUCKET", "dev-openinfopub")
    monkeypatch.setenv(
        "PUBLICATION_PUBLIC_BASE_URL",
        "https://citz-foi-prod.objectstore.gov.bc.ca/dev-openinfopub/packages",
    )

    from request_api.services.publication_events.unpublish_service import UnpublishEventService

    publisher = FakePublisher()
    service = UnpublishEventService(
        openinfo_service=FakeOpenInfoService(
            openinfo_rows=[
                {
                    "openinfoid": 42,
                    "foiministryrequestid": 100,
                    "foirequest_id": 200,
                    "axisrequestid": "EDU-2024-12345",
                    "sitemap_pages": "sitemap_pages_1.xml",
                    "type": "unpublish",
                    "bcgovcode": "edu",
                    "publicationdate": "2026-04-27",
                }
            ]
        ),
        publisher=publisher,
    )

    result = service.queue_openinfo_unpublish(100)

    assert result.success is True
    assert result.identifier == "1-0"
    envelope = publisher.published_envelopes[0].to_dict()
    assert envelope["event_type"] == PublicationEventType.UNPUBLISH_REQUESTED
    assert envelope["payload"]["kind"] == "openinfo"
    assert envelope["correlation_id"] == "openinfo-unpublish-42"
    assert envelope["payload"]["tenant_id"] == str(uuid.uuid5(uuid.NAMESPACE_DNS, "bcgov:edu"))
    assert envelope["payload"]["publication_id"] == "EDU-2024-12345"
    assert (
        envelope["payload"]["public_url"]
        == "https://citz-foi-prod.objectstore.gov.bc.ca/dev-openinfopub/packages/EDU-2024-12345/openinfo/EDU-2024-12345.html"
    )
    assert envelope["payload"]["public_repository"]["bucket"] == "dev-openinfopub"
    assert envelope["payload"]["public_repository"]["prefix"] == "openinfo/EDU-2024-12345"
    assert envelope["payload"]["last_modified"] == "2026-04-27"
    assert envelope["payload"]["foirequest_id"] == 200
    assert envelope["payload"]["foiministryrequest_id"] == 100
    assert envelope["schema_version"] == "1.0.0"
    assert envelope["source"] == "request-management-api"
    assert "meta" in envelope


def test_queue_pd_unpublish_builds_correct_envelope(monkeypatch):
    monkeypatch.setenv("OPENINFO_PUBLICATION_BUCKET", "dev-openinfopub")
    monkeypatch.setenv(
        "PUBLICATION_PUBLIC_BASE_URL",
        "https://citz-foi-prod.objectstore.gov.bc.ca/dev-openinfopub/packages",
    )

    from request_api.services.publication_events.unpublish_service import UnpublishEventService

    publisher = FakePublisher()
    service = UnpublishEventService(
        openinfo_service=FakeOpenInfoService(
            pd_rows=[
                {
                    "proactivedisclosureid": 99,
                    "foiministryrequestid": 300,
                    "foirequest_id": 400,
                    "axisrequestid": "PD-FIN-2026-001",
                    "sitemap_pages": "",
                    "type": "unpublish",
                    "bcgovcode": "fin",
                    "publicationdate": "2026-04-20",
                }
            ]
        ),
        publisher=publisher,
    )

    result = service.queue_pd_unpublish(300)

    assert result.success is True
    envelope = publisher.published_envelopes[0].to_dict()
    assert envelope["event_type"] == PublicationEventType.UNPUBLISH_REQUESTED
    assert envelope["payload"]["kind"] == "proactivedisclosure"
    assert envelope["correlation_id"] == "proactivedisclosure-unpublish-99"
    assert envelope["payload"]["publication_id"] == "PD-FIN-2026-001"
    assert (
        envelope["payload"]["public_url"]
        == "https://citz-foi-prod.objectstore.gov.bc.ca/dev-openinfopub/packages/PD-FIN-2026-001/openinfo/PD-FIN-2026-001.html"
    )
    assert envelope["payload"]["public_repository"]["prefix"] == "proactivedisclosure/PD-FIN-2026-001"
    assert envelope["payload"]["foirequest_id"] == 400
    assert envelope["payload"]["foiministryrequest_id"] == 300


def test_queue_openinfo_unpublish_no_data_returns_success():
    from request_api.services.publication_events.unpublish_service import UnpublishEventService

    publisher = FakePublisher()
    service = UnpublishEventService(
        openinfo_service=FakeOpenInfoService(openinfo_rows=[]),
        publisher=publisher,
    )

    result = service.queue_openinfo_unpublish(999)

    assert result.success is True
    assert "No data found" in result.message
    assert len(publisher.published_envelopes) == 0


def test_queue_pd_unpublish_no_data_returns_success():
    from request_api.services.publication_events.unpublish_service import UnpublishEventService

    publisher = FakePublisher()
    service = UnpublishEventService(
        openinfo_service=FakeOpenInfoService(pd_rows=[]),
        publisher=publisher,
    )

    result = service.queue_pd_unpublish(999)

    assert result.success is True
    assert "No data found" in result.message
    assert len(publisher.published_envelopes) == 0


def test_queue_openinfo_unpublish_publisher_failure(monkeypatch):
    monkeypatch.setenv("OPENINFO_PUBLICATION_BUCKET", "dev-openinfopub")

    from request_api.services.publication_events.unpublish_service import UnpublishEventService

    publisher = FakePublisher(success=False)
    service = UnpublishEventService(
        openinfo_service=FakeOpenInfoService(
            openinfo_rows=[
                {
                    "openinfoid": 42,
                    "axisrequestid": "EDU-2024-12345",
                    "bcgovcode": "edu",
                    "publicationdate": "2026-04-27",
                }
            ]
        ),
        publisher=publisher,
    )

    result = service.queue_openinfo_unpublish(100)

    assert result.success is False
    assert result.identifier == -1
