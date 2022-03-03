
import re
from typing import Counter

from flask.signals import request_started
from sqlalchemy.sql.expression import false
from request_api.models.FOIRawRequests import FOIRawRequest
import json
import asyncio
from request_api.utils.redispublisher import RedisPublisherService
from request_api.services.workflowservice import workflowservice
from request_api.services.documentservice import documentservice
from request_api.services.eventservice import eventservice
from request_api.services.rawrequest.rawrequestservicegetter import rawrequestservicegetter
from request_api.exceptions import BusinessException, Error

class rawrequestservice:
    """ FOI Raw Request management service

    This service class manages all CRUD operations related to an FOI unopened Request

    """

    def saverawrequest(self, requestdatajson, sourceofsubmission, userid,notes):
        assigneegroup = requestdatajson["assignedGroup"] if requestdatajson.get("assignedGroup") != None else None
        assignee = requestdatajson["assignedTo"] if requestdatajson.get("assignedTo") not in (None,'') else None
        assigneefirstname = requestdatajson["assignedToFirstName"] if requestdatajson.get("assignedToFirstName") != None else None
        assigneemiddlename = requestdatajson["assignedToMiddleName"] if requestdatajson.get("assignedToMiddleName") != None else None
        assigneelastname = requestdatajson["assignedToLastName"] if requestdatajson.get("assignedToLastName") != None else None
        ispiiredacted = requestdatajson["ispiiredacted"] if 'ispiiredacted' in requestdatajson  else False

        axisrequestid = requestdatajson["axisRequestId"] if 'axisRequestId' in requestdatajson  else None
        axissyncdate = requestdatajson["axisSyncDate"] if 'axisSyncDate' in requestdatajson  else None

        requirespayment =  rawrequestservice.doesrequirepayment(requestdatajson) if sourceofsubmission == "onlineform"  else False 
        result = FOIRawRequest.saverawrequest(
                                                _requestrawdata=requestdatajson,
                                                sourceofsubmission= sourceofsubmission,
                                                ispiiredacted=ispiiredacted,
                                                userid= userid,
                                                assigneegroup=assigneegroup,
                                                assignee=assignee,
                                                requirespayment=requirespayment,
                                                notes=notes,
                                                assigneefirstname=assigneefirstname,
                                                assigneemiddlename=assigneemiddlename,
                                                assigneelastname=assigneelastname,
                                                axisrequestid=axisrequestid,
                                                axissyncdate=axissyncdate
                                            )
        if result.success:
            redispubservice = RedisPublisherService()
            data = {}
            data['id'] = result.identifier
            data['assignedGroup'] = assigneegroup
            data['assignedTo'] = assignee
            json_data = json.dumps(data)
            asyncio.create_task(redispubservice.publishrequest(json_data))
        return result

    @staticmethod
    def doesrequirepayment(requestdatajson):        
        if 'requestType' not in requestdatajson or 'requestType' not in requestdatajson['requestType']:            
            raise BusinessException(Error.DATA_NOT_FOUND)
        if requestdatajson['requestType']['requestType'] == "personal":                 
            return False
        if 'contactInfo' in requestdatajson:            
            if requestdatajson['requestType']['requestType'] == "general":                
                if 'IGE' in requestdatajson['contactInfo'] and requestdatajson['contactInfo']['IGE']:                    
                    return False                   
                return True
            elif requestdatajson['requestType']['requestType'] == "personal":                
                return False
        else:
            if 'requiresPayment' not in requestdatajson:                                
                raise BusinessException(Error.DATA_NOT_FOUND)                
            return requestdatajson['requiresPayment']            
        raise BusinessException(Error.DATA_NOT_FOUND)    

    def saverawrequestversion(self, _requestdatajson, _requestid, _assigneegroup, _assignee, status, userid, username, isministryuser, assigneefirstname, assigneemiddlename, assigneelastname):
        ispiiredacted = _requestdatajson["ispiiredacted"] if 'ispiiredacted' in _requestdatajson  else False
        #Get documents
        result = FOIRawRequest.saverawrequestversion(_requestdatajson, _requestid, _assigneegroup, _assignee, status,ispiiredacted, userid, assigneefirstname, assigneemiddlename, assigneelastname)
        documentservice().createrawrequestdocumentversion(_requestid)
        asyncio.create_task(eventservice().postevent(_requestid,"rawrequest",userid, username, isministryuser))
        return result

   
    def updateworkflowinstance(self, wfinstanceid, requestid, userid):
        return FOIRawRequest.updateworkflowinstance(wfinstanceid, requestid, userid)

    def updateworkflowinstancewithstatus(self, wfinstanceid, requestid,notes, userid):
        return FOIRawRequest.updateworkflowinstancewithstatus(wfinstanceid,requestid,notes, userid)    
    
    async def posteventtoworkflow(self, id, wfinstanceid, requestsschema, status):
        return workflowservice().postunopenedevent(id, wfinstanceid, requestsschema, status)

    def getrawrequests(self):
        return rawrequestservicegetter().getallrawrequests()

    def getrawrequest(self, requestid):
        return rawrequestservicegetter().getrawrequestforid(requestid)
    
    def getrawrequestfields(self, requestid, fields):
        return rawrequestservicegetter().getrawrequestfieldsforid(requestid, fields) 
        
    def getstatus(self, foirequest):
        statusid = foirequest["requeststatusid"] if "requeststatusid" in foirequest else None
        if statusid is not None:
            try:           
                if statusid== 4:                    
                    return 'Redirect'
                if statusid == 3:                    
                    return 'Closed'    
            except  KeyError:
                print("Key Error on requeststatusid, ignore will be intake in Progress")
        return 'Intake in Progress'     