import logging
import uuid

import requests

from request_api.models.FOIOpenInformationRequests import FOIOpenInformationRequests
from request_api.models.FOIProactiveDisclosureRequests import FOIProactiveDisclosureRequests
from request_api.models.db import db
from request_api.models.default_method_result import DefaultMethodResult
from request_api.services.publication_events.rest_client import PublicationRestClient
from request_api.services.publication_events.rest_service import PublishNowRestService


class FakeOpenInfoService:
    def __init__(self, openinfo_rows=None, proactive_row=None):
        self.openinfo_rows = openinfo_rows or []
        self.proactive_row = proactive_row

    def getopeninforequestforpublishing(self, foiministryrequestid):
        return self.openinfo_rows

    def getpdopeninforequestforpublishing(self, foiministryrequestid):
        return self.proactive_row


class FakePublicationClient:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def publish(self, publication_type, payload):
        self.calls.append((publication_type, payload))
        return self.response


class FailingPublicationClient:
    def publish(self, publication_type, payload):
        raise RuntimeError("publication service unavailable")


class FakePublicationStatusUpdater:
    def __init__(self):
        self.openinfo_updates = []
        self.proactive_updates = []

    def mark_openinfo_ready_for_crawling(self, foiministryrequestid, sitemap_page):
        self.openinfo_updates.append((foiministryrequestid, sitemap_page))
        return DefaultMethodResult(True, "OpenInfo publication status updated", foiministryrequestid)

    def mark_proactive_disclosure_ready_for_crawling(self, foiministryrequestid, sitemap_page):
        self.proactive_updates.append((foiministryrequestid, sitemap_page))
        return DefaultMethodResult(True, "Proactive Disclosure publication status updated", foiministryrequestid)


class FakeHttpResponse:
    def __init__(self, status_code=200, payload=None, text="", url="http://localhost:9085/publications"):
        self.status_code = status_code
        self.payload = payload or {}
        self.text = text
        self.url = url

    def json(self):
        return self.payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} upstream error", response=self)


class FakeHttpClient:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def post(self, url, json, headers, timeout):
        self.calls.append(
            {
                "url": url,
                "json": json,
                "headers": headers,
                "timeout": timeout,
            }
        )
        return self.response


class FakeDbResult:
    def __init__(self, rowcount=1):
        self.rowcount = rowcount


class FakeDbSession:
    def __init__(self, rowcounts=None):
        self.calls = []
        self.rowcounts = rowcounts or []
        self.committed = False
        self.rolled_back = False
        self.closed = False

    def execute(self, sql, params):
        self.calls.append((str(sql), params))
        rowcount = self.rowcounts.pop(0) if self.rowcounts else 1
        return FakeDbResult(rowcount)

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True

    def close(self):
        self.closed = True


def test_publish_openinfo_posts_rest_wrapper_and_updates_sitemap_page(monkeypatch):
    monkeypatch.setenv("OPENINFO_PUBLICATION_BUCKET", "dev-openinfopub")
    monkeypatch.setenv("OPENINFO_SOURCE_BUCKET_SUFFIX", "dev-e")
    monkeypatch.setenv("FLASK_ENV", "production")
    updater = FakePublicationStatusUpdater()
    client = FakePublicationClient(
        {
            "status": "completed",
            "publication_type": "openinfo",
            "publication_id": "FIN-2026-047533",
            "sitemap_page_key": "openinfopub/sitemap/sitemap_pages_1.xml",
        }
    )
    service = PublishNowRestService(
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
        publication_client=client,
        publication_status_updater=updater,
    )

    result = service.publish_openinfo_now(22318)

    assert result.success is True
    assert result.identifier == "FIN-2026-047533"
    assert client.calls[0][0] == "openinfo"
    payload = client.calls[0][1]
    assert payload["tenant_id"] == str(uuid.uuid5(uuid.NAMESPACE_DNS, "bcgov:fin"))
    assert payload["axis_request_id"] == "FIN-2026-047533"
    assert payload["source"]["bucket"] == "fin-dev-e"
    assert payload["source"]["prefix"] == "FIN-2026-047533/openinfo/"
    assert payload["destination"]["bucket"] == "dev-openinfopub"
    assert payload["destination"]["prefix"] == "packages/FIN-2026-047533/openinfo/"
    assert updater.openinfo_updates == [(22318, "sitemap_pages_1.xml")]


def test_publish_proactive_disclosure_posts_rest_wrapper_and_updates_sitemap_page(monkeypatch):
    monkeypatch.setenv("OPENINFO_PUBLICATION_BUCKET", "dev-openinfopub")
    monkeypatch.setenv("OPENINFO_SOURCE_BUCKET_SUFFIX", "dev-e")
    monkeypatch.setenv("FLASK_ENV", "production")
    updater = FakePublicationStatusUpdater()
    client = FakePublicationClient(
        {
            "status": "completed",
            "publication_type": "proactivedisclosure",
            "publication_id": "PD-FIN-2026-047533",
            "sitemap_page_key": "pdpublishing/sitemap/sitemap_pages_2.xml",
        }
    )
    service = PublishNowRestService(
        openinfo_service=FakeOpenInfoService(
            proactive_row={
                "proactivedisclosureid": 71,
                "foiministryrequestid": 22318,
                "foirequestid": 22318,
                "axisrequestid": "PD-FIN-2026-047533",
                "description": "Ministerial Directive",
                "published_date": "2026-04-20",
                "contributor": "Ministry of Finance",
                "fees": 0,
                "applicant_type": None,
                "bcgovcode": "fin",
                "sitemap_pages": "",
                "proactivedisclosurecategory": "Calendars",
                "reportperiod": "Quarter 1 2026-27",
                "additionalfiles": [],
                "openinfoid": 0,
            }
        ),
        publication_client=client,
        publication_status_updater=updater,
    )

    result = service.publish_proactive_disclosure_now(22318)

    assert result.success is True
    assert result.identifier == "PD-FIN-2026-047533"
    assert client.calls[0][0] == "proactivedisclosure"
    payload = client.calls[0][1]
    assert payload["proactivedisclosure_category"] == "Calendars"
    assert payload["report_period"] == "Quarter 1 2026-27"
    assert payload["source"]["bucket"] == "fin-dev-e"
    assert payload["source"]["prefix"] == "PD-FIN-2026-047533/openinfo/"
    assert payload["destination"]["bucket"] == "dev-openinfopub"
    assert payload["destination"]["prefix"] == "packages/PD-FIN-2026-047533/openinfo/"
    assert "foiministryrequest_id" not in payload
    assert "additionalfiles" not in payload
    assert "sitemap_pages" not in payload
    assert updater.proactive_updates == [(22318, "sitemap_pages_2.xml")]


def test_publish_openinfo_does_not_update_when_response_is_not_completed():
    updater = FakePublicationStatusUpdater()
    service = PublishNowRestService(
        openinfo_service=FakeOpenInfoService(
            openinfo_rows=[
                {
                    "openinfoid": 345,
                    "axisrequestid": "FIN-2026-047533",
                    "bcgovcode": "fin",
                }
            ]
        ),
        publication_client=FakePublicationClient({"status": "failed", "message": "copy failed"}),
        publication_status_updater=updater,
    )

    result = service.publish_openinfo_now(22318)

    assert result.success is False
    assert "Publication API did not complete" in result.message
    assert updater.openinfo_updates == []


def test_publish_openinfo_requires_sitemap_page_key():
    updater = FakePublicationStatusUpdater()
    service = PublishNowRestService(
        openinfo_service=FakeOpenInfoService(
            openinfo_rows=[
                {
                    "openinfoid": 345,
                    "axisrequestid": "FIN-2026-047533",
                    "bcgovcode": "fin",
                }
            ]
        ),
        publication_client=FakePublicationClient({"status": "completed"}),
        publication_status_updater=updater,
    )

    result = service.publish_openinfo_now(22318)

    assert result.success is False
    assert "sitemap_page_key" in result.message
    assert updater.openinfo_updates == []


def test_publish_failure_log_includes_context_in_message(caplog):
    service = PublishNowRestService(
        openinfo_service=FakeOpenInfoService(
            proactive_row={
                "proactivedisclosureid": 71,
                "foiministryrequestid": 22318,
                "axisrequestid": "PD-FIN-2026-047533",
                "bcgovcode": "fin",
                "proactivedisclosurecategory": "Calendars",
                "reportperiod": "Quarter 1 2026-27",
            }
        ),
        publication_client=FailingPublicationClient(),
        publication_status_updater=FakePublicationStatusUpdater(),
    )

    with caplog.at_level(logging.ERROR):
        result = service.publish_proactive_disclosure_now(22318)

    assert result.success is False
    assert "publication_type=proactivedisclosure" in caplog.text
    assert "foiministryrequestid=22318" in caplog.text
    assert "axisrequestid=PD-FIN-2026-047533" in caplog.text


def test_publication_rest_client_includes_upstream_error_body():
    http_client = FakeHttpClient(
        FakeHttpResponse(
            status_code=500,
            text='{"detail":"destination bucket pd-published does not exist"}',
        )
    )
    client = PublicationRestClient(
        base_url="http://localhost:9085",
        timeout=5,
        http_client=http_client,
    )

    try:
        client.publish("proactivedisclosure", {"axis_request_id": "PD-2026-001"})
        assert False, "Expected publication client to raise on upstream HTTP error"
    except Exception as exc:
        message = str(exc)

    assert "Publication API request failed with HTTP 500" in message
    assert "destination bucket pd-published does not exist" in message
    assert "http://localhost:9085/publications" in message


def test_openinfo_ready_for_crawling_updates_ministry_oi_status(monkeypatch):
    session = FakeDbSession()
    monkeypatch.setattr(db, "session", session)

    result = FOIOpenInformationRequests.mark_ready_for_crawling(22318, "sitemap_pages_1.xml")

    assert result.success is True
    assert session.committed is True
    assert any('"FOIOpenInformationRequests"' in call[0] for call in session.calls)
    ministry_update = [call for call in session.calls if '"FOIMinistryRequests"' in call[0]][0]
    assert "oistatus_id = :oistatus_id" in ministry_update[0]
    assert ministry_update[1]["foiministryrequestid"] == 22318
    assert ministry_update[1]["oistatus_id"] == 4


def test_proactive_ready_for_crawling_updates_ministry_oi_status(monkeypatch):
    session = FakeDbSession()
    monkeypatch.setattr(db, "session", session)

    result = FOIProactiveDisclosureRequests.mark_ready_for_crawling(22318, "sitemap_pages_2.xml")

    assert result.success is True
    assert session.committed is True
    assert any('"FOIProactiveDisclosureRequests"' in call[0] for call in session.calls)
    ministry_update = [call for call in session.calls if '"FOIMinistryRequests"' in call[0]][0]
    assert "oistatus_id = :oistatus_id" in ministry_update[0]
    assert ministry_update[1]["foiministryrequestid"] == 22318
    assert ministry_update[1]["oistatus_id"] == 4


def test_proactive_ready_for_crawling_fails_when_ministry_status_not_updated(monkeypatch):
    session = FakeDbSession(rowcounts=[1, 0])
    monkeypatch.setattr(db, "session", session)

    result = FOIProactiveDisclosureRequests.mark_ready_for_crawling(22318, "sitemap_pages_2.xml")

    assert result.success is False
    assert "FOIMinistryRequests" in result.message
    assert session.committed is False
    assert session.rolled_back is True
