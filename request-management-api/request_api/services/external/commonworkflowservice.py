import requests
import os
import json
import logging

from request_api.services.external.bpmservice import MessageType

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

getinstancevariables / searchinstancebyvariable / searchprocessinstance are
intentionally left unimplemented for now.
"""

class commonworkflowservice:

    n8nbaseurl = os.getenv('N8N_BASE_URL', 'http://localhost:5678')
    n8nroutingwebhookpath = os.getenv('N8N_ROUTING_WEBHOOK_PATH', '/webhook/foi-request-routing')
    n8nwebhookauthheadername = os.getenv('N8N_WEBHOOK_AUTH_HEADER_NAME')
    n8nwebhookauthheadervalue = os.getenv('N8N_WEBHOOK_AUTH_HEADER_VALUE')

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

    def __post_event(self, messagetype, extra):
        if self.n8nbaseurl is None:
            logging.error("commonworkflowservice.__post_event: N8N_BASE_URL is not configured for event %s", messagetype)
            return None
        payload = {"event": messagetype}
        payload.update(extra)
        url = self.n8nbaseurl + self.n8nroutingwebhookpath
        logging.info("commonworkflowservice.__post_event: POST %s event=%s", url, messagetype)
        logging.info("commonworkflowservice.__post_event: payload=%s", payload)
        response = requests.post(url, data=json.dumps(payload), headers=self.__getheaders())
        logging.info("commonworkflowservice.__post_event: response status=%s body=%s", response.status_code, response.text)
        if not response.ok:
            return None
        try:
            content = json.loads(response.content) if response.content else {}
        except ValueError:
            return None
        return content if isinstance(content, dict) else None

    def __getheaders(self):
        headers = {"Content-Type": "application/json"}
        if self.n8nwebhookauthheadername:
            headers[self.n8nwebhookauthheadername] = self.n8nwebhookauthheadervalue
        return headers
