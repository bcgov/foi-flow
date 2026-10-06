import pytest

from request_api.services.workflowengine import resolve_engine, resolve_engine_name, WFEngine
from request_api.services.external.bpmservice import bpmservice
from request_api.services.external.commonworkflowservice import commonworkflowservice


def test_resolve_engine_name_uses_configured_default(monkeypatch):
    monkeypatch.setenv("WF_DEFAULT_ENGINE", "n8n")
    assert resolve_engine_name() == "n8n"

    monkeypatch.setenv("WF_DEFAULT_ENGINE", "camunda")
    assert resolve_engine_name() == "camunda"


def test_resolve_engine_name_defaults_to_camunda_when_unconfigured(monkeypatch):
    monkeypatch.delenv("WF_DEFAULT_ENGINE", raising=False)
    assert resolve_engine_name() == WFEngine.camunda

    monkeypatch.setenv("WF_DEFAULT_ENGINE", "")
    assert resolve_engine_name() == WFEngine.camunda


def test_resolve_engine_returns_bpmservice_for_camunda_default(monkeypatch):
    monkeypatch.setenv("WF_DEFAULT_ENGINE", "camunda")
    assert isinstance(resolve_engine(), bpmservice)


def test_resolve_engine_returns_commonworkflowservice_for_n8n_default(monkeypatch):
    monkeypatch.setenv("WF_DEFAULT_ENGINE", "n8n")
    assert isinstance(resolve_engine(), commonworkflowservice)


def test_resolve_engine_defaults_to_camunda_when_unconfigured(monkeypatch):
    monkeypatch.delenv("WF_DEFAULT_ENGINE", raising=False)
    assert isinstance(resolve_engine(), bpmservice)


from request_api.services.workflowengine import is_n8n


@pytest.mark.parametrize("value", ["n8n", "N8N", " n8n ", "n8n\n"])
def test_resolve_engine_name_normalises_n8n(monkeypatch, value):
    monkeypatch.setenv("WF_DEFAULT_ENGINE", value)
    assert resolve_engine_name() == WFEngine.n8n
    assert is_n8n() is True


@pytest.mark.parametrize("value", [None, "", "  ", "camunda", "CAMUNDA", " Camunda "])
def test_resolve_engine_name_normalises_camunda(monkeypatch, value):
    if value is None:
        monkeypatch.delenv("WF_DEFAULT_ENGINE", raising=False)
    else:
        monkeypatch.setenv("WF_DEFAULT_ENGINE", value)
    assert resolve_engine_name() == WFEngine.camunda
    assert is_n8n() is False


@pytest.mark.parametrize("value", ["foo", "n8", "camunda7"])
def test_resolve_engine_name_rejects_unsupported_values(monkeypatch, value):
    monkeypatch.setenv("WF_DEFAULT_ENGINE", value)
    with pytest.raises(ValueError, match="WF_DEFAULT_ENGINE=%r is not supported" % value):
        resolve_engine_name()


def test_resolve_engine_routes_normalised_n8n_to_commonworkflowservice(monkeypatch):
    monkeypatch.setenv("WF_DEFAULT_ENGINE", " N8N ")
    assert isinstance(resolve_engine(), commonworkflowservice)


def test_create_app_fails_fast_on_unsupported_engine(monkeypatch):
    from request_api import create_app
    monkeypatch.setenv("WF_DEFAULT_ENGINE", "foo")
    with pytest.raises(ValueError, match="WF_DEFAULT_ENGINE"):
        create_app()
