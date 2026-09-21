"""bpmservice.unopenedsave receives the same complete event metadata every
other engine call gets (a json.dumps(...) string) rather than a pre-built
{"assignedGroup", "assignedTo"} dict - Camunda's claim step only needs those
two fields as individual process variables, so unopenedsave must parse the
full payload and pull just those two out, ignoring everything else in it.
"""
import json
from unittest.mock import MagicMock, patch

from request_api.services.external.bpmservice import bpmservice


@patch("request_api.services.external.bpmservice.requests.post")
def test_unopenedsave_extracts_assignee_fields_from_complete_metadata(mock_post, monkeypatch):
    monkeypatch.setattr(bpmservice, "bpmengineresturl", "https://camunda.example.com")
    mock_post.return_value = MagicMock(ok=True)

    metadata = json.dumps({
        "id": 42, "status": "Intake in Progress",
        "assignedGroup": "Intake Team", "assignedTo": "jdoe",
    })

    bpmservice().unopenedsave("camunda-pid-123", metadata, "foi-intake-claim", token="test-token")

    posted_body = json.loads(mock_post.call_args[1]["data"])
    variables = posted_body["processVariables"]
    assert variables["assignedGroup"]["value"] == "Intake Team"
    assert variables["assignedTo"]["value"] == "jdoe"
    assert "status" not in variables
    assert "id" not in variables


@patch("request_api.services.external.bpmservice.requests.post")
def test_unopenedsave_returns_none_without_configuration(mock_post, monkeypatch):
    monkeypatch.setattr(bpmservice, "bpmengineresturl", None)

    result = bpmservice().unopenedsave("camunda-pid-123", json.dumps({}), "foi-intake-claim", token="test-token")

    assert result is None
    mock_post.assert_not_called()
