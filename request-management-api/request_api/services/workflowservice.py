import requests
import os
import json
from enum import Enum

from request_api.services.external.bpmservice import MessageType, bpmservice
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
"""
This class is reserved for workflow services integration.
Supported operations: claim

__author__      = "sumathi.thirumani@aot-technologies.com"

"""
class workflowservice:

    @classmethod
    def postintakeevent(self, id, wfinstanceid, requestsschema, status, ministries=None):
        assignedgroup = requestsschema["assignedGroup"] if 'assignedGroup' in requestsschema  else None
        assignedto = requestsschema["assignedTo"] if 'assignedTo' in requestsschema  else None    
        if status == "Closed" or status == "Redirect":            
            metadata = json.dumps({"id": id, "status": status, "assignedGroup": assignedgroup, "assignedTo": assignedto})
            return bpmservice.complete(wfinstanceid, metadata, MessageType.intakecomplete.value) 
        elif status == "Intake in Progress":
            return bpmservice.unopenedClaim(wfinstanceid, assignedto)   
        elif status == "Open":
            metadata = json.dumps({"id": id, "status": status, "ministries": ministries, "assignedGroup": assignedgroup, "assignedTo": assignedto})
            return bpmservice.complete(wfinstanceid, metadata, MessageType.intakecomplete.value)      
        else:
            return {"status": "Unknown status"}
        
        
    @classmethod
    def postministryevent(self, requestsschema, data, newstatus):
        assignedgroup = self._getvaluefromschema_(requestsschema,"assignedGroup")
        assignedto = self._getvaluefromschema_(requestsschema,"assignedTo") 
        filenumber = self._getvaluefromschema_(requestsschema,"idNumber")
        if data.get("ministries") is not None:
            for ministry in data.get("ministries"):    
                if ministry["filenumber"] == filenumber:
                    oldstatus = self.getministrystatus(filenumber, ministry["version"])
                    activity = self.getministryactivity(oldstatus,newstatus)
                    metadata = json.dumps({"id": filenumber, "status": newstatus, "assignedGroup": assignedgroup, "assignedTo": assignedto, "assignedministrygroup":ministry["assignedministrygroup"]})
                    messagename = self.messagename(oldstatus, activity)  
                    if activity == "complete" and messagename is not None:
                        bpmservice.openedcomplete(filenumber, metadata, messagename)
                    else:
                        bpmservice.openedclaim(filenumber, assignedgroup, assignedto, messagename)
    
    @classmethod                            
    def messagename(self, status, activity):
        if status == "Open" or status == "Review" or  status == "Consult":
            return MessageType.iaocomplete.value if activity == "complete" else MessageType.iaoclaim.value
        elif status == "Call For Records" :
            return MessageType.ministrycomplete.value if activity == "complete" else MessageType.ministryclaim.value
        else:
            return None 

    @classmethod                            
    def _getvaluefromschema_(self,requestsschema, property):
        return requestsschema.get(property) if property in requestsschema  else None  
    
    @classmethod                            
    def getministrystatus(self,filenumber, version):
        ministryreq = FOIMinistryRequest.getrequestbyfilenumberandversion(filenumber,version-1)
        return ministryreq["requeststatus.name"]    
    
    @classmethod                            
    def getministryactivity(self, oldstatus, newstatus):
        return "save" if oldstatus == newstatus else "complete"