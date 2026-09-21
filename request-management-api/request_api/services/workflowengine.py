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
    """Returns the engine name ('camunda' | 'n8n') from WF_DEFAULT_ENGINE."""
    raw_default = os.getenv("WF_DEFAULT_ENGINE")
    default_engine = raw_default if raw_default not in (None, "") else WFEngine.camunda
    logging.info(
        "workflowengine.resolve_engine_name: WF_DEFAULT_ENGINE env var=%r -> resolved=%r",
        raw_default, default_engine
    )
    return default_engine


def resolve_engine():
    """Returns the workflow-engine service instance for the current WF_DEFAULT_ENGINE."""
    enginename = resolve_engine_name()
    engine = commonworkflowservice() if enginename == WFEngine.n8n else bpmservice()
    logging.info("workflowengine.resolve_engine: routing to %s (%s)", enginename, type(engine).__name__)
    return engine
