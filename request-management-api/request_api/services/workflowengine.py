import os
import logging

from request_api.services.external.bpmservice import bpmservice
from request_api.services.external.commonworkflowservice import commonworkflowservice

"""
Resolves which workflow-engine backend (Camunda or n8n) is currently active,
purely from the WF_DEFAULT_ENGINE env var - this is a single global switch,
not a per-request decision.

"""

class WFEngine:
    camunda = "camunda"
    n8n = "n8n"


def resolve_engine_name():
    """Returns the normalized engine name ('camunda' | 'n8n') from WF_DEFAULT_ENGINE.

    Whitespace and case are ignored; unset/blank falls back to Camunda. Any other
    value raises ValueError so a typo can never silently route events nowhere.
    Every call site must go through this (or isn8n/iscamunda) rather than reading
    the env var itself."""
    raw = os.getenv("WF_DEFAULT_ENGINE")
    name = (raw or "").strip().lower() or WFEngine.camunda
    if name not in (WFEngine.camunda, WFEngine.n8n):
        raise ValueError(
            "WF_DEFAULT_ENGINE=%r is not supported; use '%s' or '%s'" % (raw, WFEngine.camunda, WFEngine.n8n)
        )
    return name


def isn8n():
    return resolve_engine_name() == WFEngine.n8n


def iscamunda():
    return resolve_engine_name() == WFEngine.camunda


def validate_engine_config():
    """Startup check: fails fast on an invalid WF_DEFAULT_ENGINE and logs the active engine once."""
    name = resolve_engine_name()
    logging.info("workflowengine: active workflow engine=%s (WF_DEFAULT_ENGINE=%r)", name, os.getenv("WF_DEFAULT_ENGINE"))
    return name


def resolve_engine():
    """Returns the workflow-engine service instance for the current WF_DEFAULT_ENGINE."""
    return commonworkflowservice() if isn8n() else bpmservice()
