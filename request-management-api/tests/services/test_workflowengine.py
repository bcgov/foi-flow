import pytest

from request_api.services.workflowengine import resolve_engine, resolve_engine_name, validate_engine_config, isn8n, iscamunda, WFEngine
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



@pytest.mark.parametrize("raw,expected", [
    ("n8n", "n8n"), ("N8N", "n8n"), (" n8n ", "n8n"), ("n8n\n", "n8n"),
    ("camunda", "camunda"), ("CAMUNDA", "camunda"), ("  ", "camunda"),
])
def test_resolve_engine_name_normalizes_value(monkeypatch, raw, expected):
    monkeypatch.setenv("WF_DEFAULT_ENGINE", raw)
    assert resolve_engine_name() == expected
    assert isn8n() == (expected == WFEngine.n8n)
    assert iscamunda() == (expected == WFEngine.camunda)


@pytest.mark.parametrize("raw", ["foo", "n8", "n8n,camunda"])
def test_resolve_engine_name_rejects_unsupported_value(monkeypatch, raw):
    monkeypatch.setenv("WF_DEFAULT_ENGINE", raw)
    with pytest.raises(ValueError) as excinfo:
        resolve_engine_name()
    assert repr(raw) in str(excinfo.value)
    assert "camunda" in str(excinfo.value) and "n8n" in str(excinfo.value)


def test_resolve_engine_fails_for_unsupported_value(monkeypatch):
    monkeypatch.setenv("WF_DEFAULT_ENGINE", "foo")
    with pytest.raises(ValueError):
        resolve_engine()


def test_validate_engine_config_returns_name_and_fails_fast(monkeypatch):
    monkeypatch.setenv("WF_DEFAULT_ENGINE", " N8N ")
    assert validate_engine_config() == WFEngine.n8n

    monkeypatch.setenv("WF_DEFAULT_ENGINE", "foo")
    with pytest.raises(ValueError):
        validate_engine_config()

