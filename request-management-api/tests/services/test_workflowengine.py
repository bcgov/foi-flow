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
