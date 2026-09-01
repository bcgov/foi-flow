import os
import logging

from request_api.services.external.bpmservice import bpmservice
from request_api.services.external.commonworkflowservice import commonworkflowservice

"""
Resolves which workflow-engine backend (Camunda or n8n) owns a given
request, per the Option 1 parallel-run strategy: existing/in-flight
requests keep whatever engine is already on their record; only requests
with no engine on record yet fall back to WF_DEFAULT_ENGINE.

"""

class WFEngine:
    camunda = "camunda"
    n8n = "n8n"


def resolve_engine_name(wfengine_on_record):
    """Returns the engine name ('camunda' | 'n8n') that owns a request.

    Uses the record's own wfengine when it is already set; otherwise falls
    back to WF_DEFAULT_ENGINE. The configured default is only ever consulted
    when wfengine_on_record is None/empty - it never overrides an explicit
    value already on the record.
    """
    if wfengine_on_record not in (None, ""):
        logging.info("workflowengine.resolve_engine_name: using wfengine already on record: %r", wfengine_on_record)
        return wfengine_on_record
    raw_default = os.getenv("WF_DEFAULT_ENGINE")
    default_engine = raw_default if raw_default not in (None, "") else WFEngine.camunda
    logging.info(
        "workflowengine.resolve_engine_name: no wfengine on record - WF_DEFAULT_ENGINE env var=%r -> resolved default=%r",
        raw_default, default_engine
    )
    return default_engine


def resolve_engine(wfengine_on_record):
    """Returns the workflow-engine service instance that owns a request."""
    enginename = resolve_engine_name(wfengine_on_record)
    engine = commonworkflowservice() if enginename == WFEngine.n8n else bpmservice()
    logging.info("workflowengine.resolve_engine: wfengine_on_record=%r -> routing to %s (%s)",
                 wfengine_on_record, enginename, type(engine).__name__)
    return engine
