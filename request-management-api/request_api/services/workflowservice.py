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

    @classmethod
    def postunopenedevent(self, id, wfinstanceid, requestsschema, status, ministries=None):
        assignedgroup = requestsschema["assignedGroup"] if 'assignedGroup' in requestsschema  else None
        assignedto = requestsschema["assignedTo"] if 'assignedTo' in requestsschema  else None    
        if status == UnopenedEvent.intakeinprogress.value:
            messagename = MessageType.intakereopen.value if self.__hasreopened(id, "rawrequest") == True else MessageType.iaoopenclaim.value
            return bpmservice.unopenedevent(wfinstanceid, assignedto, messagename)                 
        else:
            if status == UnopenedEvent.open.value:
                metadata = json.dumps({"id": id, "status": status, "ministries": ministries, "assignedGroup": assignedgroup, "assignedTo": assignedto})
            else:            
                metadata = json.dumps({"id": id, "status": status, "assignedGroup": assignedgroup, "assignedTo": assignedto})
            return bpmservice.unopenedcomplete(wfinstanceid, metadata, MessageType.intakecomplete.value) 


    @classmethod
    def postopenedevent(self, id, wfinstanceid, requestsschema, data, newstatus, usertype):
        assignedgroup = self._getvaluefromschema_(requestsschema,"assignedGroup") if usertype == "iao" else self._getvaluefromschema_(requestsschema,"assignedministrygroup") 
        assignedto = self._getvaluefromschema_(requestsschema,"assignedTo") if usertype == "iao" else self._getvaluefromschema_(requestsschema,"assignedministryperson") 
        idnumber = self._getvaluefromschema_(requestsschema,"idNumber") if usertype == "iao" else None
        if data.get("ministries") is not None:
            for ministry in data.get("ministries"): 
                filenumber =  ministry["filenumber"] if (idnumber is None and  usertype == "ministry") else idnumber
                if (ministry["filenumber"] == filenumber and usertype == "iao") or usertype == UserType.ministry.value:
                    oldstatus = self.getministrystatus(filenumber, ministry["version"])
                    activity = self.getministryactivity(oldstatus,newstatus)
                    metadata = json.dumps({"id": filenumber, "status": newstatus, "assignedGroup": assignedgroup, "assignedTo": assignedto, "assignedministrygroup":ministry["assignedministrygroup"]})
                    messagename = self.messagename(id, oldstatus, activity, usertype)    
                    if activity == Activity.complete.value:
                        if self.__hasreopened(id, "ministryrequest") == True:
                            bpmservice.reopenevent(wfinstanceid, metadata, MessageType.iaoreopen.value)
                        else:
                            bpmservice.openedcomplete(filenumber, metadata, messagename)
                    else:
                        bpmservice.openedevent(filenumber, assignedgroup, assignedto, messagename)
                        

    @classmethod                            
    def messagename(self, id, status, activity, usertype):    
        if status == UnopenedEvent.open.value:
            return MessageType.iaoopencomplete.value if activity == Activity.complete.value else MessageType.iaoopenclaim.value
        elif status == OpenedEvent.reopen.value:
            return MessageType.iaoreopen.value
        else:
            if usertype == UserType.ministry.value:
                return MessageType.ministrycomplete.value if activity == Activity.complete.value else MessageType.ministryclaim.value   
            else:
                return MessageType.iaocomplete.value if activity == Activity.complete.value else MessageType.iaoclaim.value       


    @classmethod
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


    @classmethod                            
    def _getvaluefromschema_(self,requestsschema, property):
        return requestsschema.get(property) if property in requestsschema  else None  
    
    @classmethod                            
    def getministrystatus(self,filenumber, version):
        ministryreq = FOIMinistryRequest.getrequestbyfilenumberandversion(filenumber,version-1)
        return ministryreq["requeststatus.name"]    
    
    @classmethod                            
    def getministryactivity(self, oldstatus, newstatus):
        return Activity.save.value if oldstatus == newstatus else Activity.complete.value


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