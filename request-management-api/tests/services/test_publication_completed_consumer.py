from importlib import import_module
from types import SimpleNamespace

import request_api.models.FOIOpenInformationRequests as openinfo_module
from request_api.models.default_method_result import DefaultMethodResult
from request_api.models.FOIOpenInformationRequests import FOIOpenInformationRequests
from request_api.models.FOIProactiveDisclosureRequests import FOIProactiveDisclosureRequests
from request_api.services.publication_events.consumer import (
    OpenInfoPublishCompletedConsumer,
    ProactiveDisclosurePublishCompletedConsumer,
)

proactive_module = import_module("request_api.models.FOIProactiveDisclosureRequests")


class FakeOpenInfoModel:
    def __init__(self, result=None):
        self.calls = []
        self.result = result or DefaultMethodResult(True, "updated", 345)

    def create_published_version_from_openinfo_id(self, openinfo_id, message):
        self.calls.append((openinfo_id, message))
        return self.result


class FakeProactiveDisclosureModel:
    def __init__(self, result=None):
        self.calls = []
        self.result = result or DefaultMethodResult(True, "updated", 71)

    def create_published_version_from_proactive_id(self, proactive_id, message):
        self.calls.append((proactive_id, message))
        return self.result


def completed_envelope(**overrides):
    envelope = {
        "event_id": "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d92",
        "event_type": "openinfo.publish.completed",
        "correlation_id": "openinfo-publish-345",
        "payload": {
            "tenant_id": "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d91",
            "request_event_id": "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d90",
        },
    }
    envelope.update(overrides)
    return envelope


def proactive_completed_envelope(**overrides):
    envelope = {
        "event_id": "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d82",
        "event_type": "proactivedisclosure.publish.completed",
        "correlation_id": "proactivedisclosure-publish-71",
        "payload": {
            "tenant_id": "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d81",
            "request_event_id": "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d80",
        },
    }
    envelope.update(overrides)
    return envelope


def test_handle_openinfo_publish_completed_updates_published_version():
    openinfo_model = FakeOpenInfoModel()
    consumer = OpenInfoPublishCompletedConsumer(openinfo_model=openinfo_model)

    result = consumer.handle(completed_envelope())

    assert result.success is True
    assert openinfo_model.calls == [(345, "Publication completed")]


def test_handle_openinfo_publish_completed_uses_payload_message():
    openinfo_model = FakeOpenInfoModel()
    consumer = OpenInfoPublishCompletedConsumer(openinfo_model=openinfo_model)
    envelope = completed_envelope(
        payload={
            "tenant_id": "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d91",
            "request_event_id": "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d90",
            "message": "Published to OpenInfo",
        }
    )

    result = consumer.handle(envelope)

    assert result.success is True
    assert openinfo_model.calls == [(345, "Published to OpenInfo")]


def test_handle_openinfo_publish_completed_rejects_wrong_event_type():
    openinfo_model = FakeOpenInfoModel()
    consumer = OpenInfoPublishCompletedConsumer(openinfo_model=openinfo_model)
    envelope = completed_envelope(event_type="proactivedisclosure.publish.completed")

    result = consumer.handle(envelope)

    assert result.success is False
    assert result.message == "Unsupported event type"
    assert openinfo_model.calls == []


def test_handle_openinfo_publish_completed_rejects_invalid_correlation_id():
    openinfo_model = FakeOpenInfoModel()
    consumer = OpenInfoPublishCompletedConsumer(openinfo_model=openinfo_model)
    envelope = completed_envelope(correlation_id="corr-123")

    result = consumer.handle(envelope)

    assert result.success is False
    assert result.message == "Invalid OpenInfo publish correlation_id"
    assert openinfo_model.calls == []


def test_handle_openinfo_publish_completed_requires_payload_fields():
    openinfo_model = FakeOpenInfoModel()
    consumer = OpenInfoPublishCompletedConsumer(openinfo_model=openinfo_model)
    envelope = completed_envelope(payload={"tenant_id": "tenant-1"})

    result = consumer.handle(envelope)

    assert result.success is False
    assert result.message == "Missing required payload fields: request_event_id"
    assert openinfo_model.calls == []


def test_handle_openinfo_publish_completed_returns_model_failure():
    openinfo_model = FakeOpenInfoModel(
        result=DefaultMethodResult(False, "FOIOpenInfo request not found", 345)
    )
    consumer = OpenInfoPublishCompletedConsumer(openinfo_model=openinfo_model)

    result = consumer.handle(completed_envelope())

    assert result.success is False
    assert result.message == "FOIOpenInfo request not found"
    assert result.identifier == 345
    assert openinfo_model.calls == [(345, "Publication completed")]


def test_handle_proactive_disclosure_publish_completed_updates_published_version():
    proactive_model = FakeProactiveDisclosureModel()
    consumer = ProactiveDisclosurePublishCompletedConsumer(proactive_model=proactive_model)

    result = consumer.handle(proactive_completed_envelope())

    assert result.success is True
    assert proactive_model.calls == [(71, "Publication completed")]


def test_handle_proactive_disclosure_publish_completed_uses_payload_message():
    proactive_model = FakeProactiveDisclosureModel()
    consumer = ProactiveDisclosurePublishCompletedConsumer(proactive_model=proactive_model)
    envelope = proactive_completed_envelope(
        payload={
            "tenant_id": "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d81",
            "request_event_id": "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d80",
            "message": "Proactive disclosure published",
        }
    )

    result = consumer.handle(envelope)

    assert result.success is True
    assert proactive_model.calls == [(71, "Proactive disclosure published")]


def test_handle_proactive_disclosure_publish_completed_rejects_wrong_event_type():
    proactive_model = FakeProactiveDisclosureModel()
    consumer = ProactiveDisclosurePublishCompletedConsumer(proactive_model=proactive_model)
    envelope = proactive_completed_envelope(event_type="openinfo.publish.completed")

    result = consumer.handle(envelope)

    assert result.success is False
    assert result.message == "Unsupported event type"
    assert proactive_model.calls == []


def test_handle_proactive_disclosure_publish_completed_rejects_invalid_correlation_id():
    proactive_model = FakeProactiveDisclosureModel()
    consumer = ProactiveDisclosurePublishCompletedConsumer(proactive_model=proactive_model)
    envelope = proactive_completed_envelope(correlation_id="proactive-71")

    result = consumer.handle(envelope)

    assert result.success is False
    assert result.message == "Invalid Proactive Disclosure publish correlation_id"
    assert proactive_model.calls == []


def test_handle_proactive_disclosure_publish_completed_requires_payload_fields():
    proactive_model = FakeProactiveDisclosureModel()
    consumer = ProactiveDisclosurePublishCompletedConsumer(proactive_model=proactive_model)
    envelope = proactive_completed_envelope(payload={"tenant_id": "tenant-1"})

    result = consumer.handle(envelope)

    assert result.success is False
    assert result.message == "Missing required payload fields: request_event_id"
    assert proactive_model.calls == []


def test_handle_proactive_disclosure_publish_completed_returns_model_failure():
    proactive_model = FakeProactiveDisclosureModel(
        result=DefaultMethodResult(False, "FOI Proactive Disclosure request not found", 71)
    )
    consumer = ProactiveDisclosurePublishCompletedConsumer(proactive_model=proactive_model)

    result = consumer.handle(proactive_completed_envelope())

    assert result.success is False
    assert result.message == "FOI Proactive Disclosure request not found"
    assert result.identifier == 71
    assert proactive_model.calls == [(71, "Publication completed")]


class FakeQuery:
    def __init__(self, session):
        self.session = session

    def filter(self, *_args):
        return self

    def order_by(self, *_args):
        return self

    def first(self):
        return self.session.first_results.pop(0)

    def all(self):
        return self.session.active_rows


class FakeSession:
    def __init__(self, first_results, active_rows):
        self.first_results = list(first_results)
        self.active_rows = active_rows
        self.added = []
        self.committed = False
        self.closed = False
        self.rolled_back = False

    def query(self, *_args):
        return FakeQuery(self)

    def add(self, row):
        self.added.append(row)

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True

    def close(self):
        self.closed = True


def openinfo_row(**overrides):
    row = SimpleNamespace(
        foiopeninforequestid=345,
        version=2,
        foiministryrequest_id=22318,
        foiministryrequestversion_id=4,
        oipublicationstatus_id=1,
        oiexemption_id=9,
        oiassignedto="idir\\analyst",
        oiexemptionapproved=True,
        pagereference="12-14",
        iaorationale="rationale",
        oifeedback="feedback",
        publicationdate="2026-04-20",
        receiveddate="2026-04-01",
        copyrightsevered=False,
        sitemap_pages="page-a,page-b",
        isactive=True,
        updated_at=None,
        updatedby=None,
    )
    row.__dict__.update(overrides)
    return row


def proactive_row(**overrides):
    row = SimpleNamespace(
        proactivedisclosureid=71,
        version=2,
        foiministryrequest_id=22318,
        foiministryrequestversion_id=4,
        proactivedisclosurecategoryid=6,
        reportperiod="Quarter 1 2026-27",
        publicationdate="2026-04-20",
        earliesteligiblepublicationdate="2026-03-20",
        oipublicationstatus_id=1,
        processingstatus=None,
        processingmessage=None,
        sitemap_pages="page-a,page-b",
        isactive=True,
        updated_at=None,
        updatedby=None,
    )
    row.__dict__.update(overrides)
    return row


def test_create_published_version_from_openinfo_id_versions_active_record(monkeypatch):
    current = openinfo_row(version=2)
    latest = openinfo_row(version=3, publicationdate="2026-04-21")
    other_active = openinfo_row(
        foiopeninforequestid=346,
        version=1,
        isactive=True,
    )
    fake_session = FakeSession(
        first_results=[current, latest],
        active_rows=[current, other_active],
    )
    monkeypatch.setattr(openinfo_module.db, "session", fake_session)
    monkeypatch.setattr(
        openinfo_module,
        "FOIOpenInformationRequests",
        lambda **kwargs: SimpleNamespace(**kwargs),
    )

    result = FOIOpenInformationRequests.create_published_version_from_openinfo_id(
        345,
        "Published to OpenInfo",
    )

    assert result.success is True
    assert result.message == "OpenInfo publication status updated"
    assert result.identifier == 345
    assert current.isactive is False
    assert other_active.isactive is False
    assert current.updatedby == "publishingservice"
    assert other_active.updatedby == "publishingservice"
    assert fake_session.committed is True
    assert fake_session.closed is True
    assert fake_session.rolled_back is False
    assert len(fake_session.added) == 1

    new_openinfo = fake_session.added[0]
    assert new_openinfo.foiopeninforequestid == 345
    assert new_openinfo.version == 4
    assert new_openinfo.foiministryrequest_id == 22318
    assert new_openinfo.foiministryrequestversion_id == 4
    assert new_openinfo.oipublicationstatus_id == 1
    assert new_openinfo.oiexemption_id == 9
    assert new_openinfo.oiassignedto == "idir\\analyst"
    assert new_openinfo.oiexemptionapproved is True
    assert new_openinfo.pagereference == "12-14"
    assert new_openinfo.iaorationale == "rationale"
    assert new_openinfo.oifeedback == "feedback"
    assert new_openinfo.publicationdate == "2026-04-21"
    assert new_openinfo.receiveddate == "2026-04-01"
    assert new_openinfo.copyrightsevered is False
    assert new_openinfo.processingstatus == "ready for sitemap"
    assert new_openinfo.processingmessage == "Published to OpenInfo"
    assert new_openinfo.sitemap_pages == "page-a,page-b"
    assert new_openinfo.isactive is True
    assert new_openinfo.createdby == "publishingservice"


def test_create_published_version_from_openinfo_id_returns_failure_when_missing(monkeypatch):
    fake_session = FakeSession(first_results=[None], active_rows=[])
    monkeypatch.setattr(openinfo_module.db, "session", fake_session)

    result = FOIOpenInformationRequests.create_published_version_from_openinfo_id(
        999,
        "Publication completed",
    )

    assert result.success is False
    assert result.message == "FOIOpenInfo request not found"
    assert result.identifier == 999
    assert fake_session.added == []
    assert fake_session.committed is False
    assert fake_session.closed is True


def test_create_published_version_from_proactive_id_versions_active_record(monkeypatch):
    current = proactive_row(version=2)
    latest = proactive_row(version=3, publicationdate="2026-04-21")
    other_active = proactive_row(
        proactivedisclosureid=72,
        version=1,
        isactive=True,
    )
    fake_session = FakeSession(
        first_results=[current, latest],
        active_rows=[current, other_active],
    )
    monkeypatch.setattr(proactive_module.db, "session", fake_session)
    monkeypatch.setattr(
        proactive_module,
        "FOIProactiveDisclosureRequests",
        lambda **kwargs: SimpleNamespace(**kwargs),
    )

    result = FOIProactiveDisclosureRequests.create_published_version_from_proactive_id(
        71,
        "Proactive disclosure published",
    )

    assert result.success is True
    assert result.message == "Proactive Disclosure publication status updated"
    assert result.identifier == 71
    assert current.isactive is False
    assert other_active.isactive is False
    assert current.updatedby == "publishingservice"
    assert other_active.updatedby == "publishingservice"
    assert fake_session.committed is True
    assert fake_session.closed is True
    assert fake_session.rolled_back is False
    assert len(fake_session.added) == 1

    new_proactive = fake_session.added[0]
    assert new_proactive.proactivedisclosureid == 71
    assert new_proactive.version == 4
    assert new_proactive.foiministryrequest_id == 22318
    assert new_proactive.foiministryrequestversion_id == 4
    assert new_proactive.proactivedisclosurecategoryid == 6
    assert new_proactive.reportperiod == "Quarter 1 2026-27"
    assert new_proactive.publicationdate == "2026-04-21"
    assert new_proactive.earliesteligiblepublicationdate == "2026-03-20"
    assert new_proactive.oipublicationstatus_id == 1
    assert new_proactive.processingstatus == "ready for sitemap"
    assert new_proactive.processingmessage == "Proactive disclosure published"
    assert new_proactive.sitemap_pages == "page-a,page-b"
    assert new_proactive.isactive is True
    assert new_proactive.createdby == "publishingservice"


def test_create_published_version_from_proactive_id_returns_failure_when_missing(monkeypatch):
    fake_session = FakeSession(first_results=[None], active_rows=[])
    monkeypatch.setattr(proactive_module.db, "session", fake_session)

    result = FOIProactiveDisclosureRequests.create_published_version_from_proactive_id(
        999,
        "Publication completed",
    )

    assert result.success is False
    assert result.message == "FOI Proactive Disclosure request not found"
    assert result.identifier == 999
    assert fake_session.added == []
    assert fake_session.committed is False
    assert fake_session.closed is True
