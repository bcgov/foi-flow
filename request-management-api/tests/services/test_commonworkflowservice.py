import json
import uuid
from unittest.mock import MagicMock, patch

import pytest
import requests

from request_api.services.external.bpmservice import MessageType
from request_api.services.external.commonworkflowservice import commonworkflowservice

POST = "request_api.services.external.commonworkflowservice.requests.post"
RETRY_QUEUE = "request_api.services.external.commonworkflowservice.n8nwebhookretryqueue"


@pytest.fixture(autouse=True)
def _n8n_env(monkeypatch):
    monkeypatch.setenv("N8N_BASE_URL", "https://n8n.example.com")
    monkeypatch.setenv("N8N_ROUTING_WEBHOOK_PATH", "/webhook/foi-request-routing")
    monkeypatch.setenv("N8N_WEBHOOK_AUTH_HEADER_NAME", "X-N8N-Auth")
    monkeypatch.setenv("N8N_WEBHOOK_AUTH_HEADER_VALUE", "secret")
    monkeypatch.delenv("N8N_WEBHOOK_TIMEOUT_SECONDS", raising=False)


@pytest.fixture
def retry_queue():
    with patch(RETRY_QUEUE) as queue_class:
        yield queue_class.return_value


def _mock_response(ok=True, body=None, status_code=None):
    resp = MagicMock()
    resp.ok = ok
    resp.status_code = status_code if status_code is not None else (200 if ok else 400)
    resp.content = json.dumps(body).encode() if body is not None else b""
    return resp


def _unopenedcomplete():
    return commonworkflowservice().unopenedcomplete(None, json.dumps({"id": 1}), MessageType.intakecomplete.value)


@patch(POST)
def test_unopenedcomplete_posts_to_fixed_routing_webhook_with_event_field(mock_post):
    mock_post.return_value = _mock_response(True, {})
    result = _unopenedcomplete()
    assert result == {}
    called_url = mock_post.call_args[0][0]
    assert called_url == "https://n8n.example.com/webhook/foi-request-routing"
    body = json.loads(mock_post.call_args[1]["data"])
    assert body["event"] == MessageType.intakecomplete.value
    headers = mock_post.call_args[1]["headers"]
    assert headers["X-N8N-Auth"] == "secret"


@patch(POST)
def test_unopenedsave_nests_complete_metadata_under_foireuestmetadata(mock_post):
    """unopenedsave's metadata argument is the same complete event payload
    every other engine call receives (a json.dumps(...) string), nested under
    foiRequestMetaData exactly like every other event method."""
    mock_post.return_value = _mock_response(True, {})
    metadata = json.dumps({"id": 42, "status": "Intake in Progress", "assignedGroup": "Intake Team", "assignedTo": "jdoe"})

    commonworkflowservice().unopenedsave(None, metadata, MessageType.intakeclaim.value)

    called_url = mock_post.call_args[0][0]
    assert called_url == "https://n8n.example.com/webhook/foi-request-routing"
    body = json.loads(mock_post.call_args[1]["data"])
    assert body["event"] == MessageType.intakeclaim.value
    assert body["foiRequestMetaData"] == metadata


@patch(POST)
def test_openedcomplete_includes_filenumber(mock_post):
    mock_post.return_value = _mock_response(True, {})
    commonworkflowservice().openedcomplete(None, "FILE-1", json.dumps({}), MessageType.iaocomplete.value)
    body = json.loads(mock_post.call_args[1]["data"])
    assert body["id"] == "FILE-1"
    assert body["event"] == MessageType.iaocomplete.value


@patch(POST)
def test_feeevent_uses_managepayment_event(mock_post):
    mock_post.return_value = _mock_response(True, {})
    commonworkflowservice().feeevent("AXIS-1", json.dumps({}), "PAID")
    body = json.loads(mock_post.call_args[1]["data"])
    assert body["event"] == MessageType.managepayment.value
    assert body["paymentstatus"] == "PAID"


@patch(POST)
def test_correspondanceevent_uses_correspondence_event(mock_post):
    mock_post.return_value = _mock_response(True, {})
    commonworkflowservice().correspondanceevent(None, "FILE-1", json.dumps({}))
    body = json.loads(mock_post.call_args[1]["data"])
    assert body["event"] == MessageType.iaocorrenspodence.value


@patch(POST)
def test_reopenevent_delegates_to_unopenedcomplete(mock_post):
    mock_post.return_value = _mock_response(True, {})
    commonworkflowservice().reopenevent(None, json.dumps({}), MessageType.iaoreopen.value)
    body = json.loads(mock_post.call_args[1]["data"])
    assert body["event"] == MessageType.iaoreopen.value


@patch(POST)
def test_every_event_method_adds_a_uuid4_event_id(mock_post):
    mock_post.return_value = _mock_response(True, {})
    engine = commonworkflowservice()
    engine.unopenedsave(None, json.dumps({}), MessageType.intakeclaim.value)
    engine.unopenedcomplete(None, json.dumps({}), MessageType.intakecomplete.value)
    engine.openedcomplete(None, "FILE-1", json.dumps({}), MessageType.iaocomplete.value)
    engine.feeevent("AXIS-1", json.dumps({}), "PAID")
    engine.correspondanceevent(None, "FILE-1", json.dumps({}))
    engine.reopenevent(None, json.dumps({}), MessageType.iaoreopen.value)
    eventIds = [json.loads(call[1]["data"])["eventId"] for call in mock_post.call_args_list]
    assert len(eventIds) == 6
    assert all(uuid.UUID(eventId).version == 4 for eventId in eventIds)
    assert len(set(eventIds)) == 6


@patch(POST)
def test_eventId_is_kept_on_the_payload_queued_for_retry(mock_post, retry_queue):
    mock_post.side_effect = requests.ConnectionError("refused")
    assert _unopenedcomplete() is None
    sent = json.loads(mock_post.call_args[1]["data"])
    queued = retry_queue.enqueue.call_args[0][0]
    assert queued["eventId"] == sent["eventId"]


@patch(POST)
def test_redelivery_of_a_queued_payload_resends_the_same_eventId(mock_post):
    mock_post.return_value = _mock_response(True, {})
    payload = {"event": MessageType.intakecomplete.value, "eventId": "11111111-1111-4111-8111-111111111111"}
    commonworkflowservice().deliver(payload)
    assert json.loads(mock_post.call_args[1]["data"])["eventId"] == payload["eventId"]


@patch(POST)
def test_post_uses_default_timeout(mock_post):
    mock_post.return_value = _mock_response(True, {})
    _unopenedcomplete()
    assert mock_post.call_args[1]["timeout"] == 10


@patch(POST)
def test_post_uses_configured_timeout(mock_post, monkeypatch):
    monkeypatch.setenv("N8N_WEBHOOK_TIMEOUT_SECONDS", "3")
    mock_post.return_value = _mock_response(True, {})
    _unopenedcomplete()
    assert mock_post.call_args[1]["timeout"] == 3


@patch(POST)
def test_empty_routing_path_falls_back_to_default(mock_post, monkeypatch):
    monkeypatch.setenv("N8N_ROUTING_WEBHOOK_PATH", "")
    mock_post.return_value = _mock_response(True, {})
    _unopenedcomplete()
    assert mock_post.call_args[0][0] == "https://n8n.example.com/webhook/foi-request-routing"


@pytest.mark.parametrize("base_url", [None, "", "   "])
@patch(POST)
def test_missing_base_url_is_logged_not_sent_and_not_queued(mock_post, retry_queue, monkeypatch, caplog, base_url):
    if base_url is None:
        monkeypatch.delenv("N8N_BASE_URL", raising=False)
    else:
        monkeypatch.setenv("N8N_BASE_URL", base_url)
    assert _unopenedcomplete() is None
    mock_post.assert_not_called()
    retry_queue.enqueue.assert_not_called()
    assert "N8N_BASE_URL is not configured" in caplog.text


@pytest.mark.parametrize("error", [requests.Timeout("timed out"), requests.ConnectionError("refused")])
@patch(POST)
def test_network_failure_is_queued_for_retry(mock_post, retry_queue, error):
    mock_post.side_effect = error
    assert _unopenedcomplete() is None
    retry_queue.enqueue.assert_called_once()
    payload = retry_queue.enqueue.call_args[0][0]
    assert payload["event"] == MessageType.intakecomplete.value
    assert retry_queue.enqueue.call_args[1]["attempts"] == 1
    assert retry_queue.enqueue.call_args[1]["error"] == type(error).__name__


@pytest.mark.parametrize("status_code", [429, 500, 503])
@patch(POST)
def test_retryable_http_status_is_queued_for_retry(mock_post, retry_queue, status_code):
    mock_post.return_value = _mock_response(False, status_code=status_code)
    assert _unopenedcomplete() is None
    retry_queue.enqueue.assert_called_once()
    assert retry_queue.enqueue.call_args[1]["error"] == "HTTP %s" % status_code


@pytest.mark.parametrize("status_code", [400, 401, 403, 404])
@patch(POST)
def test_non_retryable_http_status_is_not_queued(mock_post, retry_queue, status_code):
    mock_post.return_value = _mock_response(False, status_code=status_code)
    assert _unopenedcomplete() is None
    retry_queue.enqueue.assert_not_called()


@patch(POST)
def test_queue_failure_is_logged_not_raised(mock_post, retry_queue, caplog):
    mock_post.side_effect = requests.ConnectionError("refused")
    retry_queue.enqueue.side_effect = Exception("redis down")
    assert _unopenedcomplete() is None
    assert "unable to queue n8n event" in caplog.text


@patch(POST)
def test_success_with_non_json_body_is_delivered_and_not_queued(mock_post, retry_queue):
    response = _mock_response(True)
    response.content = b"Workflow was started"
    mock_post.return_value = response
    result = commonworkflowservice().deliver({"event": MessageType.intakecomplete.value})
    assert result.delivered is True
    assert result.content is None
    retry_queue.enqueue.assert_not_called()


@patch(POST)
def test_logs_do_not_contain_payload_or_response_body(mock_post, caplog):
    caplog.set_level("INFO")
    mock_post.return_value = _mock_response(True, {"secret": "response-body"})
    commonworkflowservice().unopenedcomplete(None, json.dumps({"assignedTo": "jdoe@example.com"}), MessageType.intakecomplete.value)
    assert "jdoe@example.com" not in caplog.text
    assert "response-body" not in caplog.text


def test_gated_methods_raise_not_implemented():
    engine = commonworkflowservice()
    with pytest.raises(NotImplementedError):
        engine.getinstancevariables({"foiRequestId": 7})
    with pytest.raises(NotImplementedError):
        engine.searchinstancebyvariable("foi-request", [{"name": "id", "value": 7}])
    with pytest.raises(NotImplementedError):
        engine.searchprocessinstance("555")
