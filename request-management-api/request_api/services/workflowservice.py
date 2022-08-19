import requests
import os
import json
from enum import Enum

from request_api.services.external.bpmservice import MessageType, bpmservice
from request_api.models.FOIRawRequests import FOIRawRequest
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
"""
This class is reserved for workflow services integration.
Supported operations: claim

__author__      = "sumathi.thirumani@aot-technologies.com"

"""
class workflowservice:

    def postunopenedevent(self, id, wfinstanceid, requestsschema, status, ministries=None):
        assignedgroup = requestsschema["assignedGroup"] if 'assignedGroup' in requestsschema  else None
        assignedto = requestsschema["assignedTo"] if 'assignedTo' in requestsschema  else None    
        if status == UnopenedEvent.intakeinprogress.value:
            messagename = MessageType.intakereopen.value if self.__hasreopened(id, "rawrequest") == True else MessageType.intakeclaim.value
            return bpmservice().unopenedevent(wfinstanceid, assignedto, messagename)                 
        else:
            if status == UnopenedEvent.open.value:
                metadata = json.dumps({"id": id, "status": status, "ministries": ministries, "assignedGroup": assignedgroup, "assignedTo": assignedto})
            else:            
                metadata = json.dumps({"id": id, "status": status, "assignedGroup": assignedgroup, "assignedTo": assignedto})
            return bpmservice().unopenedcomplete(wfinstanceid, metadata, MessageType.intakecomplete.value) 

    def postopenedevent(self, id, wfinstanceid, requestsschema, data, newstatus, usertype):
        assignedgroup = self.__getopenedassigneevalue(requestsschema, "assignedgroup") 
        assignedto = self.__getopenedassigneevalue(requestsschema, "assignedto")
        idnumber = self.__getvaluefromschema(requestsschema,"idNumber") if usertype == "iao" else None
        paymentexpirydate = self.__getvaluefromschema(requestsschema,"paymentExpiryDate")
        axisRequestId = self.__getvaluefromschema(requestsschema,"axisRequestId")
        if data.get("ministries") is not None:
            for ministry in data.get("ministries"): 
                filenumber =  ministry["filenumber"] if (idnumber is None and  usertype == "ministry") else idnumber
                if (ministry["filenumber"] == filenumber and usertype == "iao") or usertype == UserType.ministry.value:
                    oldstatus = self.__getministrystatus(filenumber, ministry["version"])
                    activity = self.__getministryactivity(oldstatus,newstatus)
                    metadata = json.dumps({"id": filenumber, "status": newstatus, "assignedGroup": assignedgroup, "assignedTo": assignedto, "assignedministrygroup":ministry["assignedministrygroup"], "ministryRequestID": id, "paymentExpiryDate": paymentexpirydate, "axisRequestId": axisRequestId})
                    messagename = self.__messagename(oldstatus, activity, usertype, self.__isprocessing(id))
                    self.__postopenedevent(id, filenumber, metadata, messagename, assignedgroup, assignedto, wfinstanceid, activity)

    def postfeeevent(self, requestid, ministryrequestid, requestsschema, status):
        metadata = json.dumps({
            "id": requestsschema["idNumber"], 
            "status": "Call For Records", 
            "assignedGroup": requestsschema["assignedGroup"], 
            "assignedTo": requestsschema["assignedTo"],
            "assignedministrygroup" : requestsschema["assignedministrygroup"],
            "ministryRequestID" : ministryrequestid,
			"foiRequestID" :requestid
            })
        return bpmservice().feeevent(requestsschema["axisRequestId"], metadata, status)    
    
    def __postopenedevent(self, id, filenumber, metadata, messagename, assignedgroup, assignedto, wfinstanceid, activity):
        if activity == Activity.complete.value:
            if self.__hasreopened(id, "ministryrequest") == True:
                bpmservice().reopenevent(wfinstanceid, metadata, MessageType.iaoreopen.value)
            else:
                bpmservice().openedcomplete(filenumber, metadata, messagename)   
        else:
            bpmservice().openedevent(filenumber, assignedgroup, assignedto, messagename)
         
    
    def __getopenedassigneevalue(self, requestsschema, property):
        if property == "assignedgroup":
            return self.__getvaluefromschema(requestsschema,"assignedgroup") 
        elif property == "assignedto":
            return self.__getvaluefromschema(requestsschema,"assignedto") 
        else:
            return None
        
             
    def __messagename(self, status, activity, usertype, isprocessing=False):   
        if status == UnopenedEvent.open.value and isprocessing == False:
            return MessageType.iaoopencomplete.value if activity == Activity.complete.value else MessageType.iaoopenclaim.value
        elif status == OpenedEvent.reopen.value:
            return MessageType.iaoreopen.value
        else:
            if usertype == UserType.ministry.value:
                return MessageType.ministrycomplete.value if activity == Activity.complete.value else MessageType.ministryclaim.value   
            else:
                return MessageType.iaocomplete.value if activity == Activity.complete.value else MessageType.iaoclaim.value       


    def __hasreopened(self, requestid, requesttype):
        if requesttype == "rawrequest":
            states =  FOIRawRequest.getstatenavigation(requestid)
        else:
            states =  FOIMinistryRequest.getstatenavigation(requestid)
        if len(states) == 2:
            newstate = states[0]
            oldstate = states[1]
            if newstate != oldstate and oldstate == "Closed":
                return True
        return False 

    def __isprocessing(self, requestid):
        states =  FOIMinistryRequest.getallstatenavigation(requestid)
        for state in states:
            if state == OpenedEvent.callforrecords.value and states[0] != OpenedEvent.callforrecords.value :
                return True
        return False 

    def __getvaluefromschema(self,requestsschema, property):
        return requestsschema.get(property) if property in requestsschema  else None  
    
    def __getministrystatus(self,filenumber, version):
        ministryreq = FOIMinistryRequest.getrequestbyfilenumberandversion(filenumber,version-1)
        return ministryreq["requeststatus.name"]    
    
    def __getministryactivity(self, oldstatus, newstatus):
        return  Activity.complete.value if newstatus is not None and oldstatus != newstatus else Activity.save.value


class UserType(Enum):
    iao = "iao"    
    ministry = "ministry" 
    
class Activity(Enum):
    save = "save"    
    complete = "complete"       
    
class UnopenedEvent(Enum):
    intakeinprogress = "Intake in Progress"    
    open = "Open"
    redirect = "Redirect"
    closed = "Closed"
    reopen = "Reopen"  
     
class OpenedEvent(Enum):
    callforrecords = "Call For Records" 
    reopen = "Reopen" 