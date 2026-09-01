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

Per Option 1 (parallel run):
- bpmservice.py / Camunda is untouched and keeps using wfinstanceid.
- commonworkflowservice.py / n8n stores its own execution info in
  wfmetadata ({"executionId": ..., "resumePath": ...}) rather than
  wfinstanceid. Callers pass the current wfmetadata["resumePath"] value in
  the same argument slot bpmservice uses for the Camunda instance id/
  correlation key, since that is, in both cases, "the address of the
  specific running instance this call should reach."
- N8N_BASE_URL is environment-specific configuration and is never persisted;
  resumePath is combined with it only at call time.

getinstancevariables / searchinstancebyvariable / searchprocessinstance are
intentionally left unimplemented for now.
"""

class commonworkflowservice:

    n8nbaseurl = os.getenv('N8N_BASE_URL')
    n8ncreateinstancepath = os.getenv('N8N_CREATE_INSTANCE_WEBHOOK_PATH')
    n8nwebhookauthheadername = os.getenv('N8N_WEBHOOK_AUTH_HEADER_NAME')
    n8nwebhookauthheadervalue = os.getenv('N8N_WEBHOOK_AUTH_HEADER_VALUE')

    def createinstance(self, messagequeue, message, token=None):
        if self.n8nbaseurl is None or self.n8ncreateinstancepath is None:
            logging.error(
                "commonworkflowservice.createinstance: missing n8n config - N8N_BASE_URL=%r N8N_CREATE_INSTANCE_WEBHOOK_PATH=%r",
                self.n8nbaseurl, self.n8ncreateinstancepath
            )
            return None
        payload = dict(message)
        payload["definitionKey"] = self.__getprocessdefinitionkey(messagequeue)
        url = self.n8nbaseurl + self.n8ncreateinstancepath
        logging.info("commonworkflowservice.createinstance: POST %s payload=%s", url, payload)
        createresponse = requests.post(url, data=json.dumps(payload), headers=self.__getheaders())
        logging.info("commonworkflowservice.createinstance: response status=%s body=%s", createresponse.status_code, createresponse.text)
        if createresponse.ok:
            content = json.loads(createresponse.content) if createresponse.content else {}
            executionid = content.get("pid")
            if executionid is None:
                logging.error("commonworkflowservice.createinstance: n8n response missing pid: %s", content)
                return None
            return {"executionId": executionid}
        return None

    def getinstancevariables(self, instanceid, token=None):
        raise NotImplementedError(
            "commonworkflowservice.getinstancevariables is deferred pending n8n integration "
            "(see docs/Implementation_Approach_Camunda_n8n_Parallel_Run.md, section 2)."
        )

    def searchinstancebyvariable(self, definitionkey, searchby, token=None):
        raise NotImplementedError(
            "commonworkflowservice.searchinstancebyvariable is deferred pending n8n integration "
            "(see docs/Implementation_Approach_Camunda_n8n_Parallel_Run.md, section 2)."
        )

    def searchprocessinstance(self, pid, token=None):
        raise NotImplementedError(
            "commonworkflowservice.searchprocessinstance is deferred pending n8n integration "
            "(see docs/Implementation_Approach_Camunda_n8n_Parallel_Run.md, section 2)."
        )

    def unopenedsave(self, processinstanceid, metadata, messagetype, token=None):
        return self.__post_event(processinstanceid, messagetype, { "foiRequestMetaData": metadata })

    def unopenedcomplete(self, processinstanceid, data, messagetype, token=None):
        return self.__post_event(processinstanceid, messagetype, {"foiRequestMetaData": data})

    def openedcomplete(self, wfinstanceid, filenumber, data, messagetype, token=None):
        return self.__post_event(wfinstanceid, messagetype, {"id": filenumber, "foiRequestMetaData": data})

    def feeevent(self, axisrequestid, data, paymentstatus, token=None):
        return self.__post_event(axisrequestid, MessageType.managepayment.value,
                                  {"foiRequestMetaData": data, "paymentstatus": paymentstatus})

    def correspondanceevent(self, wfinstanceid, filenumber, data, token=None):
        return self.__post_event(wfinstanceid, MessageType.iaocorrenspodence.value,
                                  {"id": filenumber, "foiRequestMetaData": data})

    def reopenevent(self, processinstanceid, data, messagetype, token=None):
        return self.unopenedcomplete(processinstanceid, data, messagetype, token)

    def __post_event(self, resumepath, messagetype, extra):
        if self.n8nbaseurl is None or resumepath in (None, ""):
            logging.error("commonworkflowservice.__post_event: N8N resume path is invalid for event %s (n8nbaseurl=%r, resumepath=%r)",
                          messagetype, self.n8nbaseurl, resumepath)
            return None
        payload = {"event": messagetype}
        payload.update(extra)
        url = self.n8nbaseurl + resumepath
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

    def __getprocessdefinitionkey(self, messagequeue):
        if messagequeue == "foi-rawrequest":
            return "foi-request"
        return None

    def __getheaders(self):
        headers = {"Content-Type": "application/json"}
        if self.n8nwebhookauthheadername:
            headers[self.n8nwebhookauthheadername] = self.n8nwebhookauthheadervalue
        return headers
