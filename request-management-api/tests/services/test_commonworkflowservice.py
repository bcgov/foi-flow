import json
import uuid
from unittest.mock import MagicMock, patch

import pytest
import requests

from request_api.services.external.bpmservice import MessageType
from request_api.services.external.commonworkflowservice import commonworkflowservice

POST = "request_api.services.external.commonworkflowservice.requests.post"
OUTBOX = "request_api.services.external.commonworkflowservice.workflowoutboxservice"

PAYLOAD = {"event": MessageType.intakecomplete.value, "event_id": "11111111-1111-4111-8111-111111111111"}


@pytest.fixture(autouse=True)
def _n8n_env(monkeypatch):
    monkeypatch.setenv("N8N_BASE_URL", "https://n8n.example.com")
    monkeypatch.setenv("N8N_ROUTING_WEBHOOK_PATH", "/webhook/foi-request-routing")
    monkeypatch.setenv("N8N_WEBHOOK_AUTH_HEADER_NAME", "X-N8N-Auth")
    monkeypatch.setenv("N8N_WEBHOOK_AUTH_HEADER_VALUE", "secret")
    monkeypatch.delenv("N8N_WEBHOOK_TIMEOUT_SECONDS", raising=False)


@pytest.fixture
def outbox():
    with patch(OUTBOX) as outbox_class:
        yield outbox_class.return_value


def _mock_response(ok=True, body=None, status_code=None):
    resp = MagicMock()
    resp.ok = ok
    resp.status_code = status_code if status_code is not None else (200 if ok else 400)
    resp.content = json.dumps(body).encode() if body is not None else b""
    return resp


def _unopenedcomplete():
    return commonworkflowservice().unopenedcomplete(None, json.dumps({"id": 1}), MessageType.intakecomplete.value)


def _enqueued(outbox):
    return [call[0][0] for call in outbox.enqueue.call_args_list]


# --- producing events: outbox write, no direct POST -------------------------------------------

@patch(POST)
def test_events_are_written_to_the_outbox_and_not_posted_directly(mock_post, outbox):
    assert _unopenedcomplete() is None
    mock_post.assert_not_called()
    outbox.enqueue.assert_called_once()
    payload = _enqueued(outbox)[0]
    assert payload["event"] == MessageType.intakecomplete.value
    assert payload["foiRequestMetaData"] == json.dumps({"id": 1})


def test_unopenedsave_nests_complete_metadata_under_foireuestmetadata(outbox):
    """unopenedsave's metadata argument is the same complete event payload
    every other engine call receives (a json.dumps(...) string), nested under
    foiRequestMetaData exactly like every other event method."""
    metadata = json.dumps({"id": 42, "status": "Intake in Progress", "assignedGroup": "Intake Team", "assignedTo": "jdoe"})
    commonworkflowservice().unopenedsave(None, metadata, MessageType.intakeclaim.value)
    payload = _enqueued(outbox)[0]
    assert payload["event"] == MessageType.intakeclaim.value
    assert payload["foiRequestMetaData"] == metadata


def test_openedcomplete_includes_filenumber(outbox):
    commonworkflowservice().openedcomplete(None, "FILE-1", json.dumps({}), MessageType.iaocomplete.value)
    payload = _enqueued(outbox)[0]
    assert payload["id"] == "FILE-1"
    assert payload["event"] == MessageType.iaocomplete.value


def test_feeevent_uses_managepayment_event(outbox):
    commonworkflowservice().feeevent("AXIS-1", json.dumps({}), "PAID")
    payload = _enqueued(outbox)[0]
    assert payload["event"] == MessageType.managepayment.value
    assert payload["paymentstatus"] == "PAID"


def test_correspondanceevent_uses_correspondence_event(outbox):
    commonworkflowservice().correspondanceevent(None, "FILE-1", json.dumps({}))
    assert _enqueued(outbox)[0]["event"] == MessageType.iaocorrenspodence.value


def test_reopenevent_delegates_to_unopenedcomplete(outbox):
    commonworkflowservice().reopenevent(None, json.dumps({}), MessageType.iaoreopen.value)
    assert _enqueued(outbox)[0]["event"] == MessageType.iaoreopen.value


def test_every_event_method_adds_a_unique_uuid4_event_id(outbox):
    engine = commonworkflowservice()
    engine.unopenedsave(None, json.dumps({}), MessageType.intakeclaim.value)
    engine.unopenedcomplete(None, json.dumps({}), MessageType.intakecomplete.value)
    engine.openedcomplete(None, "FILE-1", json.dumps({}), MessageType.iaocomplete.value)
    engine.feeevent("AXIS-1", json.dumps({}), "PAID")
    engine.correspondanceevent(None, "FILE-1", json.dumps({}))
    engine.reopenevent(None, json.dumps({}), MessageType.iaoreopen.value)
    event_ids = [payload["event_id"] for payload in _enqueued(outbox)]
    assert len(event_ids) == 6
    assert all(uuid.UUID(event_id).version == 4 for event_id in event_ids)
    assert len(set(event_ids)) == 6


def test_outbox_failure_is_logged_not_raised(outbox, caplog):
    outbox.enqueue.side_effect = Exception("db down")
    assert _unopenedcomplete() is None
    assert "unable to save n8n event" in caplog.text


# --- deliver(): one POST, used by the dispatcher -----------------------------------------------

@pytest.mark.parametrize("base,path", [
    ("https://n8n.example.com/", "/webhook/foi-request-routing"),
    ("https://n8n.example.com", "webhook/foi-request-routing"),
    ("https://n8n.example.com/", "webhook/foi-request-routing"),
    ("https://n8n.example.com///", " //webhook/foi-request-routing "),
])
@patch(POST)
def test_deliver_url_has_single_slash_between_base_and_path(mock_post, monkeypatch, base, path):
    monkeypatch.setenv("N8N_BASE_URL", base)
    monkeypatch.setenv("N8N_ROUTING_WEBHOOK_PATH", path)
    mock_post.return_value = _mock_response(True, {})
    commonworkflowservice().deliver(PAYLOAD)
    assert mock_post.call_args[0][0] == "https://n8n.example.com/webhook/foi-request-routing"


@patch(POST)
def test_deliver_posts_to_fixed_routing_webhook_with_auth_header(mock_post):
    mock_post.return_value = _mock_response(True, {})
    result = commonworkflowservice().deliver(PAYLOAD)
    assert result.delivered is True
    assert mock_post.call_args[0][0] == "https://n8n.example.com/webhook/foi-request-routing"
    assert mock_post.call_args[1]["headers"]["X-N8N-Auth"] == "secret"
    assert json.loads(mock_post.call_args[1]["data"]) == PAYLOAD


@patch(POST)
def test_redelivery_of_a_stored_payload_resends_the_same_event_id(mock_post):
    mock_post.return_value = _mock_response(True, {})
    commonworkflowservice().deliver(PAYLOAD)
    commonworkflowservice().deliver(PAYLOAD)
    sent = [json.loads(call[1]["data"])["event_id"] for call in mock_post.call_args_list]
    assert sent == [PAYLOAD["event_id"]] * 2


@patch(POST)
def test_deliver_uses_default_timeout(mock_post):
    mock_post.return_value = _mock_response(True, {})
    commonworkflowservice().deliver(PAYLOAD)
    assert mock_post.call_args[1]["timeout"] == 10


@patch(POST)
def test_deliver_uses_configured_timeout(mock_post, monkeypatch):
    monkeypatch.setenv("N8N_WEBHOOK_TIMEOUT_SECONDS", "3")
    mock_post.return_value = _mock_response(True, {})
    commonworkflowservice().deliver(PAYLOAD)
    assert mock_post.call_args[1]["timeout"] == 3


@patch(POST)
def test_empty_routing_path_falls_back_to_default(mock_post, monkeypatch):
    monkeypatch.setenv("N8N_ROUTING_WEBHOOK_PATH", "")
    mock_post.return_value = _mock_response(True, {})
    commonworkflowservice().deliver(PAYLOAD)
    assert mock_post.call_args[0][0] == "https://n8n.example.com/webhook/foi-request-routing"


@pytest.mark.parametrize("base_url", [None, "", "   "])
@patch(POST)
def test_missing_base_url_is_logged_not_sent_and_not_retryable(mock_post, monkeypatch, caplog, base_url):
    if base_url is None:
        monkeypatch.delenv("N8N_BASE_URL", raising=False)
    else:
        monkeypatch.setenv("N8N_BASE_URL", base_url)
    result = commonworkflowservice().deliver(PAYLOAD)
    assert (result.delivered, result.retryable) == (False, False)
    mock_post.assert_not_called()
    assert "N8N_BASE_URL is not configured" in caplog.text


@pytest.mark.parametrize("error", [requests.Timeout("timed out"), requests.ConnectionError("refused")])
@patch(POST)
def test_network_failure_is_retryable(mock_post, error):
    mock_post.side_effect = error
    result = commonworkflowservice().deliver(PAYLOAD)
    assert (result.delivered, result.retryable, result.error) == (False, True, type(error).__name__)


@pytest.mark.parametrize("status_code", [429, 500, 503])
@patch(POST)
def test_retryable_http_status(mock_post, status_code):
    mock_post.return_value = _mock_response(False, status_code=status_code)
    result = commonworkflowservice().deliver(PAYLOAD)
    assert (result.delivered, result.retryable, result.error) == (False, True, "HTTP %s" % status_code)


@pytest.mark.parametrize("status_code", [400, 401, 403, 404])
@patch(POST)
def test_non_retryable_http_status(mock_post, status_code):
    mock_post.return_value = _mock_response(False, status_code=status_code)
    result = commonworkflowservice().deliver(PAYLOAD)
    assert (result.delivered, result.retryable) == (False, False)


@patch(POST)
def test_success_with_non_json_body_is_delivered(mock_post):
    response = _mock_response(True)
    response.content = b"Workflow was started"
    mock_post.return_value = response
    result = commonworkflowservice().deliver(PAYLOAD)
    assert result.delivered is True
    assert result.content is None


@patch(POST)
def test_logs_do_not_contain_payload_or_response_body(mock_post, caplog):
    caplog.set_level("INFO")
    mock_post.return_value = _mock_response(True, {"secret": "response-body"})
    commonworkflowservice().deliver({**PAYLOAD, "foiRequestMetaData": json.dumps({"assignedTo": "jdoe@example.com"})})
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
