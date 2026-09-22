import json
from unittest.mock import MagicMock, patch

import pytest

from request_api.services.external.bpmservice import MessageType
from request_api.services.external.commonworkflowservice import commonworkflowservice


@pytest.fixture(autouse=True)
def _n8n_env(monkeypatch):
    monkeypatch.setattr(commonworkflowservice, "n8nbaseurl", "https://n8n.example.com")
    monkeypatch.setattr(commonworkflowservice, "n8nroutingwebhookpath", "/webhook/foi-request-routing")
    monkeypatch.setattr(commonworkflowservice, "n8nwebhookauthheadername", "X-N8N-Auth")
    monkeypatch.setattr(commonworkflowservice, "n8nwebhookauthheadervalue", "secret")


def _mock_response(ok=True, body=None):
    resp = MagicMock()
    resp.ok = ok
    resp.content = json.dumps(body).encode() if body is not None else b""
    return resp


@patch("request_api.services.external.commonworkflowservice.requests.post")
def test_unopenedcomplete_posts_to_fixed_routing_webhook_with_event_field(mock_post):
    mock_post.return_value = _mock_response(True, {})
    result = commonworkflowservice().unopenedcomplete(
        None, json.dumps({"id": 1}), MessageType.intakecomplete.value
    )
    assert result == {}
    called_url = mock_post.call_args[0][0]
    assert called_url == "https://n8n.example.com/webhook/foi-request-routing"
    body = json.loads(mock_post.call_args[1]["data"])
    assert body["event"] == MessageType.intakecomplete.value
    headers = mock_post.call_args[1]["headers"]
    assert headers["X-N8N-Auth"] == "secret"


@patch("request_api.services.external.commonworkflowservice.requests.post")
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


@patch("request_api.services.external.commonworkflowservice.requests.post")
def test_openedcomplete_includes_filenumber(mock_post):
    mock_post.return_value = _mock_response(True, {})
    commonworkflowservice().openedcomplete(None, "FILE-1", json.dumps({}), MessageType.iaocomplete.value)
    body = json.loads(mock_post.call_args[1]["data"])
    assert body["id"] == "FILE-1"
    assert body["event"] == MessageType.iaocomplete.value


@patch("request_api.services.external.commonworkflowservice.requests.post")
def test_feeevent_uses_managepayment_event(mock_post):
    mock_post.return_value = _mock_response(True, {})
    commonworkflowservice().feeevent("AXIS-1", json.dumps({}), "PAID")
    body = json.loads(mock_post.call_args[1]["data"])
    assert body["event"] == MessageType.managepayment.value
    assert body["paymentstatus"] == "PAID"


@patch("request_api.services.external.commonworkflowservice.requests.post")
def test_correspondanceevent_uses_correspondence_event(mock_post):
    mock_post.return_value = _mock_response(True, {})
    commonworkflowservice().correspondanceevent(None, "FILE-1", json.dumps({}))
    body = json.loads(mock_post.call_args[1]["data"])
    assert body["event"] == MessageType.iaocorrenspodence.value


@patch("request_api.services.external.commonworkflowservice.requests.post")
def test_reopenevent_delegates_to_unopenedcomplete(mock_post):
    mock_post.return_value = _mock_response(True, {})
    commonworkflowservice().reopenevent(None, json.dumps({}), MessageType.iaoreopen.value)
    body = json.loads(mock_post.call_args[1]["data"])
    assert body["event"] == MessageType.iaoreopen.value


def test_post_event_returns_none_without_base_url_configured(monkeypatch):
    monkeypatch.setattr(commonworkflowservice, "n8nbaseurl", None)
    assert commonworkflowservice().unopenedcomplete(None, json.dumps({}), MessageType.intakecomplete.value) is None


@patch("request_api.services.external.commonworkflowservice.requests.post")
def test_post_event_returns_none_when_request_fails(mock_post):
    mock_post.return_value = _mock_response(False)
    assert commonworkflowservice().unopenedcomplete(None, json.dumps({}), MessageType.intakecomplete.value) is None


def test_gated_methods_raise_not_implemented():
    engine = commonworkflowservice()
    with pytest.raises(NotImplementedError):
        engine.getinstancevariables({"foiRequestId": 7})
    with pytest.raises(NotImplementedError):
        engine.searchinstancebyvariable("foi-request", [{"name": "id", "value": 7}])
    with pytest.raises(NotImplementedError):
        engine.searchprocessinstance("555")
