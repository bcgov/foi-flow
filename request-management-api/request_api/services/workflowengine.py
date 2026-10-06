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
    supported = (camunda, n8n)


def resolve_engine_name():
    """Returns 'camunda' or 'n8n' from WF_DEFAULT_ENGINE.

    The value is trimmed and lower-cased; unset/empty means camunda. Any other
    value raises ValueError so a typo is caught at startup (create_app calls
    this once) instead of silently routing requests down a mixed path."""
    raw = os.getenv("WF_DEFAULT_ENGINE")
    name = (raw or "").strip().lower() or WFEngine.camunda
    if name not in WFEngine.supported:
        raise ValueError("WF_DEFAULT_ENGINE=%r is not supported; use one of: %s" % (raw, ", ".join(WFEngine.supported)))
    logging.debug("workflowengine.resolve_engine_name: WF_DEFAULT_ENGINE=%r -> resolved=%r", raw, name)
    return name


def is_n8n():
    """True when the configured workflow engine is n8n."""
    return resolve_engine_name() == WFEngine.n8n


def resolve_engine():
    """Returns the workflow-engine service instance for the current WF_DEFAULT_ENGINE."""
    engine = commonworkflowservice() if is_n8n() else bpmservice()
    logging.info("workflowengine.resolve_engine: routing to %s", type(engine).__name__)
    return engine
