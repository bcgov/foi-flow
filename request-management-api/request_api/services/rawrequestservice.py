
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
from request_api.models.default_method_result import DefaultMethodResult
from request_api.models.FOIRawRequestWatchers import FOIRawRequestWatcher
from request_api.services.foirequest.requestserviceconfigurator import requestserviceconfigurator
from request_api.utils.enums import StateName
import logging

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
        isconsultflag = requestdatajson["isconsultflag"] if 'isconsultflag' in requestdatajson  else False
        
        if axisrequestid is not None:
            isaxisrequestidpresent = self.isaxisrequestidpresent(axisrequestid)
        axissyncdate = requestdatajson["axisSyncDate"] if 'axisSyncDate' in requestdatajson  else None
        linkedrequests = requestdatajson["linkedRequests"] if 'linkedRequests' in requestdatajson  else None
        requirespayment =  rawrequestservice.doesrequirepayment(requestdatajson) if sourceofsubmission == "onlineform"  else False 
        if axisrequestid is None or isaxisrequestidpresent == False:
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
                                                    axissyncdate=axissyncdate,
                                                    linkedrequests=linkedrequests,
                                                    isconsultflag=isconsultflag                                                     
                                                )
        else:            
            raise ValueError("Duplicate AXIS Request ID")
        if result.success:
            redispubservice = RedisPublisherService()
            data = {}
            data['id'] = result.identifier
            data['assignedGroup'] = assigneegroup
            data['assignedTo'] = assignee
            json_data = json.dumps(data)
            try:
                workflowservice().createinstance(redispubservice.foirequestqueueredischannel, json_data)
            except Exception as ex:
                logging.error(ex)
                event_loop = asyncio.get_running_loop()
                asyncio.run_coroutine_threadsafe(redispubservice.publishrequest(json_data), event_loop)
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

    def saverawrequestversion(self, _requestdatajson, _requestid, _assigneegroup, _assignee, status, userid, assigneefirstname, assigneemiddlename, assigneelastname, statuslabel, actiontype=None):
        ispiiredacted = _requestdatajson["ispiiredacted"] if 'ispiiredacted' in _requestdatajson  else False        
        #Get documents
        if actiontype == "assignee":
            result = FOIRawRequest.saverawrequestassigneeversion(_requestid, _assigneegroup, _assignee, userid, assigneefirstname, assigneemiddlename, assigneelastname)
        else:
            result = FOIRawRequest.saverawrequestversion(_requestdatajson, _requestid, _assigneegroup, _assignee, status,ispiiredacted, userid, statuslabel, assigneefirstname, assigneemiddlename, assigneelastname)
        documentservice().createrawrequestdocumentversion(_requestid)
        return result

    def saverawrequestiaorestricted(self,_requestid,_iaorestricted,_updatedby):
        result = FOIRawRequest.saveiaorestrictedrawrequest(_requestid,_iaorestricted,_updatedby)
        return result
   
    def updateworkflowinstance(self, wfinstanceid, requestid, userid):
        return FOIRawRequest.updateworkflowinstance(wfinstanceid, requestid, userid)

    def updateworkflowinstancewithstatus(self, wfinstanceid, requestid,notes, userid):
        return FOIRawRequest.updateworkflowinstancewithstatus(wfinstanceid,requestid,notes, userid)    
    
    def posteventtoworkflow(self, id, requestsschema, status):
        pid = workflowservice().syncwfinstance("rawrequest", id)
        return workflowservice().postunopenedevent(id, pid, requestsschema, status)

    def getrawrequests(self):
        return rawrequestservicegetter().getallrawrequests()

    def getrawrequest(self, requestid):
        return rawrequestservicegetter().getrawrequestforid(requestid)
    
    def getrawrequestfields(self, requestid, fields):
        return rawrequestservicegetter().getrawrequestfieldsforid(requestid, fields) 
        
    def getstatus(self, foirequest):
        statuslabel = foirequest["requeststatuslabel"] if "requeststatuslabel" in foirequest else None
        if statuslabel is not None:
            try:
                return requestserviceconfigurator().getstatusname(statuslabel), statuslabel         
                # if statusid== 4:                    
                #     return 'Redirect'
                # if statusid == 3:                    
                #     return 'Closed' 
                # if statusid == 16:                    
                #     return 'Peer Review'   
            except  KeyError:
                print("Key Error on requeststatusid, ignore will be intake in Progress")
        return StateName.intakeinprogress.value, StateName.intakeinprogress.name

    def getaxisequestids(self):
        return rawrequestservicegetter().getaxisequestids()
    
    def isaxisrequestidpresent(self, axisrequestid):
        countofaxisrequestid = rawrequestservicegetter().getcountofaxisequestidbyaxisequestid(axisrequestid)
        if countofaxisrequestid > 0:
            return True
        return False

    def israwrequestwatcher(self,requestid, userid):
        return FOIRawRequestWatcher.isawatcher(requestid,userid)    