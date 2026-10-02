import requests
import os
import json
import logging
import uuid

from request_api.services.external.bpmservice import MessageType
from request_api.services.external.n8nwebhookretryqueue import n8nwebhookretryqueue

"""
n8n implementation of the workflow-engine interface consumed by
workflowservice.py. Exposes the same method surface as bpmservice.py so
request_api.services.workflowengine.resolve_engine() can hand back either
engine interchangeably.

All n8n requests are routed through a single fixed webhook
(N8N_BASE_URL + N8N_ROUTING_WEBHOOK_PATH) - n8n itself is responsible for
identifying and routing the request from the payload (the "event" field
plus whatever ids/metadata are already present in the payload), so there is
no per-request instance id/address to store or construct on this side.

Every event carries an "event_id" (uuid4) generated once in __post_event and
stored in the payload, so a retry through the queue re-sends the same id and
FOI Request Routing in n8n can skip an event whose earlier run completed.

A webhook call that fails transiently (network error, timeout, HTTP 429 or
5xx) is logged and queued in n8nwebhookretryqueue; N8NWebhookRetryScheduler
re-sends it later through deliver(). Non-retryable failures (missing
N8N_BASE_URL, other 4xx) are only logged, since resending cannot fix them.

getinstancevariables / searchinstancebyvariable / searchprocessinstance are
intentionally left unimplemented for now.
"""

class n8ndeliveryresult:
    """Outcome of one webhook call: delivered, whether a failure is worth
    retrying, the response body (dict) and a short error description."""

    def __init__(self, delivered, retryable=False, content=None, error=None):
        self.delivered = delivered
        self.retryable = retryable
        self.content = content
        self.error = error


class commonworkflowservice:

    def __init__(self):
        self.n8nbaseurl = (os.getenv('N8N_BASE_URL') or '').strip()
        self.n8nroutingwebhookpath = os.getenv('N8N_ROUTING_WEBHOOK_PATH') or '/webhook/foi-request-routing'
        self.n8nwebhookauthheadername = os.getenv('N8N_WEBHOOK_AUTH_HEADER_NAME')
        self.n8nwebhookauthheadervalue = os.getenv('N8N_WEBHOOK_AUTH_HEADER_VALUE')
        self.n8nwebhooktimeout = float(os.getenv('N8N_WEBHOOK_TIMEOUT_SECONDS') or 10)

    def getinstancevariables(self, instanceid, token=None):
        raise NotImplementedError(
            "commonworkflowservice.getinstancevariables is deferred pending n8n integration."
        )

    def searchinstancebyvariable(self, definitionkey, searchby, token=None):
        raise NotImplementedError(
            "commonworkflowservice.searchinstancebyvariable is deferred pending n8n integration."
        )

    def searchprocessinstance(self, pid, token=None):
        raise NotImplementedError(
            "commonworkflowservice.searchprocessinstance is deferred pending n8n integration."
        )

    def unopenedsave(self, processinstanceid, metadata, messagetype, token=None):
        return self.__post_event(messagetype, { "foiRequestMetaData": metadata })

    def unopenedcomplete(self, processinstanceid, data, messagetype, token=None):
        return self.__post_event(messagetype, {"foiRequestMetaData": data})

    def openedcomplete(self, wfinstanceid, filenumber, data, messagetype, token=None):
        return self.__post_event(messagetype, {"id": filenumber, "foiRequestMetaData": data})

    def feeevent(self, axisrequestid, data, paymentstatus, token=None):
        return self.__post_event(MessageType.managepayment.value,
                                  {"foiRequestMetaData": data, "paymentstatus": paymentstatus})

    def correspondanceevent(self, wfinstanceid, filenumber, data, token=None):
        return self.__post_event(MessageType.iaocorrenspodence.value,
                                  {"id": filenumber, "foiRequestMetaData": data})

    def reopenevent(self, processinstanceid, data, messagetype, token=None):
        return self.unopenedcomplete(processinstanceid, data, messagetype, token)

    def deliver(self, payload):
        """POSTs one event payload to the n8n routing webhook, exactly once.
        Used for the first attempt and by N8NWebhookRetryScheduler for retries."""
        event = payload.get("event")
        if not self.n8nbaseurl:
            logging.error("commonworkflowservice.deliver: N8N_BASE_URL is not configured; event=%s not sent", event)
            return n8ndeliveryresult(False, retryable=False, error="N8N_BASE_URL is not configured")
        url = self.n8nbaseurl + self.n8nroutingwebhookpath
        try:
            response = requests.post(url, data=json.dumps(payload), headers=self.__getheaders(), timeout=self.n8nwebhooktimeout)
        except requests.RequestException as ex:
            logging.exception("commonworkflowservice.deliver: n8n webhook call failed; event=%s error=%s", event, type(ex).__name__)
            return n8ndeliveryresult(False, retryable=True, error=type(ex).__name__)
        if not response.ok:
            retryable = response.status_code == 429 or response.status_code >= 500
            logging.error("commonworkflowservice.deliver: n8n webhook returned an error; event=%s status=%s retryable=%s", event, response.status_code, retryable)
            return n8ndeliveryresult(False, retryable=retryable, error="HTTP %s" % response.status_code)
        logging.info("commonworkflowservice.deliver: n8n webhook accepted event=%s status=%s", event, response.status_code)
        try:
            content = json.loads(response.content) if response.content else {}
        except ValueError:
            content = None
        return n8ndeliveryresult(True, content=content if isinstance(content, dict) else None)

    def __post_event(self, messagetype, extra):
        payload = {"event": messagetype, "eventId": str(uuid.uuid4())}
        payload.update(extra)
        logging.info("commonworkflowservice.__post_event: sending event=%s eventId=%s", messagetype, payload["eventId"])
        result = self.deliver(payload)
        if not result.delivered and result.retryable:
            self.__queueforretry(payload, result.error)
        return result.content if result.delivered else None

    def __queueforretry(self, payload, error):
        try:
            n8nwebhookretryqueue().enqueue(payload, attempts=1, error=error)
        except Exception as ex:
            logging.exception("commonworkflowservice: unable to queue n8n event=%s for retry; event is not delivered: %s", payload.get("event"), type(ex).__name__)

    def __getheaders(self):
        headers = {"Content-Type": "application/json"}
        if self.n8nwebhookauthheadername:
            headers[self.n8nwebhookauthheadername] = self.n8nwebhookauthheadervalue
        return headers
