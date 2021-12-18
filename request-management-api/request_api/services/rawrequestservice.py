
from typing import Counter

from flask.signals import request_started
from request_api.models.FOIRawRequests import FOIRawRequest
import json
import asyncio
from request_api.utils.redispublisher import RedisPublisherService
from request_api.services.workflowservice import workflowservice
from request_api.services.documentservice import documentservice
from request_api.services.eventservice import eventservice
from request_api.services.rawrequest.rawrequestservicegetter import rawrequestservicegetter

class rawrequestservice:
    """ FOI Raw Request management service

    This service class manages all CRUD operations related to an FOI unopened Request

    """

    def saverawrequest(self, requestdatajson, sourceofsubmission, userid):
        assigneegroup = requestdatajson["assignedGroup"] if requestdatajson.get("assignedGroup") != None else None
        assignee = requestdatajson["assignedTo"] if requestdatajson.get("assignedTo") != None else None
        ispiiredacted = requestdatajson["ispiiredacted"] if 'ispiiredacted' in requestdatajson  else False
        result = FOIRawRequest.saverawrequest(requestdatajson,sourceofsubmission,ispiiredacted,userid,assigneegroup,assignee)
        if result.success:
            redispubservice = RedisPublisherService()
            data = {}
            data['id'] = result.identifier
            data['assignedGroup'] = assigneegroup
            data['assignedTo'] = assignee
            json_data = json.dumps(data)
            asyncio.run(redispubservice.publishtoredischannel(json_data))
        return result

    def saverawrequestversion(self, _requestdatajson, _requestid, _assigneegroup, _assignee, status, userid):
        ispiiredacted = _requestdatajson["ispiiredacted"] if 'ispiiredacted' in _requestdatajson  else False
        #Get documents
        result = FOIRawRequest.saverawrequestversion(_requestdatajson, _requestid, _assigneegroup, _assignee, status,ispiiredacted, userid)
        documentservice().createrawrequestdocumentversion(_requestid)
        eventservice().postevent(_requestid,"rawrequest")
        return result

   
    def updateworkflowinstance(self, wfinstanceid, requestid, userid):
        return FOIRawRequest.updateworkflowinstance(wfinstanceid, requestid, userid)

    def updateworkflowinstancewithstatus(self, wfinstanceid, requestid,status,notes, userid):
        return FOIRawRequest.updateworkflowinstancewithstatus(wfinstanceid,requestid,status,notes, userid)    
    
    def posteventtoworkflow(self, id, wfinstanceid, requestsschema, status):
        return workflowservice().postunopenedevent(id, wfinstanceid, requestsschema, status)

    def getrawrequests(self):
        return rawrequestservicegetter().getallrawrequests()

    def getrawrequest(self, requestid):
        return rawrequestservicegetter().getrawrequestforid(requestid)
        
    def getstatus(self, statusid):
        if statusid is not None:
            try:           
                if statusid== 4:                    
                    return 'Redirect'
                if statusid == 3:                    
                    return 'Closed'    
            except  KeyError:
                print("Key Error on requeststatusid, ignore will be intake in Progress")
        return 'Intake in Progress'     