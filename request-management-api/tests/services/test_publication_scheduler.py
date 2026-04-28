from datetime import datetime

import request_api.models.FOIOpenInformationRequests as openinfo_module
from request_api.models.FOIOpenInformationRequests import FOIOpenInformationRequests
from request_api.models.default_method_result import DefaultMethodResult
from request_api.services.publication_events.scheduler import PublicationPrePublishingScheduler
from request_api.services.publication_events.scheduled_service import ScheduledPublicationService


class FakeSession:
    def __init__(self, rows=None):
        self.rows = rows or []
        self.statements = []
        self.closed = False

    def execute(self, statement, params=None):
        self.statements.append((str(statement), params))
        return self.rows

    def close(self):
        self.closed = True


class FakeOpenInfoModel:
    def __init__(self, rows):
        self.rows = rows
        self.calls = 0

    def getopeninforecordsforprepublishing(self):
        self.calls += 1
        return self.rows


class FakeMapper:
    def __init__(self):
        self.rows = []

    def map(self, row):
        self.rows.append(row)
        return FakePayload({"axis_request_id": row["axisrequestid"]})

    @staticmethod
    def correlation_id(row):
        return f"openinfo-publish-{row.get('openinfoid')}"


class FakePayload:
    def __init__(self, data):
        self.data = data

    def to_dict(self):
        return self.data


class FakePublicationClient:
    def __init__(self):
        self.calls = []

    def publish(self, publication_type, payload):
        self.calls.append((publication_type, payload))
        return {
            "status": "completed",
            "publication_id": payload["axis_request_id"],
            "sitemap_page_key": "openinfopub/sitemap/sitemap_pages_1.xml",
        }


class FakePublicationStatusUpdater:
    def __init__(self):
        self.calls = []

    def mark_openinfo_ready_for_crawling(self, foiministryrequestid, sitemap_page):
        self.calls.append((foiministryrequestid, sitemap_page))
        return DefaultMethodResult(True, "updated", foiministryrequestid)


class FakePublisher:
    def __init__(self):
        self.envelopes = []

    def publish(self, envelope):
        self.envelopes.append(envelope)
        return DefaultMethodResult(True, "Request queued for publishing successfully", "1-0")


class FakeStopEvent:
    def __init__(self):
        self.waits = []
        self.wait_count = 0

    def is_set(self):
        return self.wait_count > 0

    def wait(self, seconds):
        self.waits.append(seconds)
        self.wait_count += 1
        return True


def test_getopeninforecordsforprepublishing_filters_publishable_rows(monkeypatch):
    fake_session = FakeSession(
        rows=[
            {
                "openinfoid": 345,
                "foiministryrequestid": 22318,
                "axisrequestid": "FIN-2026-047533",
            }
        ]
    )
    monkeypatch.setattr(openinfo_module.db, "session", fake_session)

    rows = FOIOpenInformationRequests.getopeninforecordsforprepublishing(
        now=datetime(2026, 4, 28, 8, 30, 0)
    )

    assert rows == [
        {
            "openinfoid": 345,
            "foiministryrequestid": 22318,
            "axisrequestid": "FIN-2026-047533",
        }
    ]
    sql, params = fake_session.statements[0]
    assert 'oistatus.name IN (:ready_status, :published_status)' in sql
    assert 'oirequesttype.name = :publication_status' in sql
    assert 'oi.processingstatus is NULL' in sql
    assert "oi.publicationdate < :publication_cutoff" in sql
    assert params == {
        "ready_status": "Ready to Publish",
        "published_status": "Published",
        "publication_status": "Publish",
        "publication_cutoff": "2026-04-29",
    }
    assert fake_session.closed is True


def test_scheduled_publication_service_queues_each_prepublishing_record():
    row = {
        "openinfoid": 345,
        "foiministryrequestid": 22318,
        "axisrequestid": "FIN-2026-047533",
    }
    model = FakeOpenInfoModel([row])
    mapper = FakeMapper()
    publisher = FakePublisher()
    service = ScheduledPublicationService(
        openinfo_model=model,
        openinfo_mapper=mapper,
        publisher=publisher,
    )

    results = service.publish_due_openinfo_records()

    assert model.calls == 1
    assert mapper.rows == [row]
    assert len(publisher.envelopes) == 1
    envelope = publisher.envelopes[0].to_dict()
    assert envelope["event_type"] == "openinfo.publish.requested"
    assert envelope["correlation_id"] == "openinfo-publish-345"
    assert envelope["payload"] == {"axis_request_id": "FIN-2026-047533"}
    assert results[0].success is True


def test_scheduler_runs_job_then_waits_configured_interval():
    calls = []
    stop_event = FakeStopEvent()
    scheduler = PublicationPrePublishingScheduler(
        job=lambda: calls.append("ran"),
        interval_seconds=300,
        stop_event=stop_event,
    )

    scheduler.run_forever()

    assert calls == ["ran"]
    assert stop_event.waits == [300]
