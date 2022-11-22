import requests
import os
import json
from enum import Enum
from request_api.exceptions import BusinessException
from request_api.utils.redispublisher import RedisPublisherService
from request_api.services.external.bpmservice import MessageType, bpmservice
from request_api.services.cfrfeeservice import cfrfeeservice
from request_api.models.FOIRawRequests import FOIRawRequest
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIRequests import FOIRequest
import logging
"""
This class is reserved for workflow services integration.
Supported operations: claim

__author__      = "sumathi.thirumani@aot-technologies.com"

"""
class workflowservice:

    def createinstance(self, definitionkey, message):
        response = bpmservice().createinstance(definitionkey, json.loads(message))
        if response.status_code != 200:
            raise BusinessException("Unable to create instance for key"+ definitionkey)
        return response


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

    def postopenedevent(self, id, wfinstanceid, requestsschema, data, newstatus, usertype, issync=False):
        assignedgroup = self.__getopenedassigneevalue(requestsschema, "assignedgroup",usertype) 
        assignedto = self.__getopenedassigneevalue(requestsschema, "assignedto",usertype)
        paymentexpirydate = self.__getvaluefromschema(requestsschema,"paymentExpiryDate")
        axisrequestid = self.__getvaluefromschema(requestsschema,"axisRequestId")
        if data.get("ministries") is not None:
            for ministry in data.get("ministries"): 
                filenumber =  ministry["filenumber"] 
                if int(ministry["id"]) == int(id):    
                    previousstatus =  self.__getpreviousministrystatus(id) if issync == False else self.__getprevioustatusbyversion(id, int(ministry["version"]))
                    oldstatus = self.__getministrystatus(filenumber, ministry["version"]) if issync == False else previousstatus                
                    activity = self.__getministryactivity(oldstatus,newstatus) if issync == False else Activity.complete.value
                    isprocessing = self.__isprocessing(id) if issync == False else False          
                    messagename = self.__messagename(oldstatus, activity, usertype, isprocessing)                
                    metadata = json.dumps({"id": filenumber, "previousstatus":previousstatus, "status": ministry["status"] , "assignedGroup": assignedgroup, "assignedTo": assignedto, "assignedministrygroup":ministry["assignedministrygroup"], "ministryRequestID": id, "isPaymentActive": self.__ispaymentactive(ministry["foirequestid"], id), "paymentExpiryDate": paymentexpirydate, "axisRequestId": axisrequestid})
                    self.__postopenedevent(id, filenumber, metadata, messagename, assignedgroup, assignedto, wfinstanceid, activity)

    def postfeeevent(self, requestid, ministryrequestid, requestsschema, paymentstatus, nextstatename=None):
        metadata = json.dumps({
            "id": requestsschema["idNumber"], 
            "status": requestsschema["currentState"], 
            "assignedGroup": requestsschema["assignedGroup"], 
            "assignedTo": requestsschema["assignedTo"],
            "assignedministrygroup" : requestsschema["assignedministrygroup"],
            "ministryRequestID" : ministryrequestid,
			"foiRequestID" :requestid,
            "nextStateName": nextstatename
            })
        return bpmservice().feeevent(requestsschema["axisRequestId"], metadata, paymentstatus)    
    
    def postcorrenspodenceevent(self, ministryid, requestsschema, applicantcorrespondenceid, templatename, attributes):
        paymentexpirydate = self.__getvaluefromlist(attributes,"paymentExpiryDate")
        axisrequestid = self.__getvaluefromschema(requestsschema,"axisRequestId")
        filenumber = self.__getvaluefromschema(requestsschema,"idNumber")
        status = self.__getvaluefromschema(requestsschema,"currentState")
        metadata = json.dumps({"id": filenumber, "status": status , "ministryRequestID": ministryid, "paymentExpiryDate": paymentexpirydate, "axisRequestId": axisrequestid, "applicantcorrespondenceid": applicantcorrespondenceid, "templatename": templatename.replace(" ", "")})
        bpmservice().correspondanceevent(filenumber, metadata)

    def syncwfinstance(self, requesttype, requestid, isallactivity=False):        
        _raw_metadata = FOIRawRequest.getworkflowinstancebyraw(requestid) if requesttype == "rawrequest" else FOIRawRequest.getworkflowinstancebyministry(requestid)
        # Check raw request instance creation - Reconcile with new instance creation
        if _raw_metadata.wfinstanceid in (None, ""):
            self.create_unopened_instance(_raw_metadata)
        if requesttype == "ministryrequest":
            _req_instance = FOIRequest.getworkflowinstance(requestid)            
            if _req_instance in (None, ""):
                self.create_opened_instance(requestid, _raw_metadata)            
            # Check foi request instance creation - Reconcile by transition to Open
            _all_activity_desc = FOIMinistryRequest.getactivitybyid(requestid)             
            _req_instance_n = FOIRequest.getworkflowinstance(requestid)            
            # Check Current status in WF engine
            if _req_instance_n in (None, ""):
                self.syncwfinstance("ministryrequest", requestid, isallactivity)
            else:
                self.__sync_state_transition(requestid, _req_instance_n, _all_activity_desc, isallactivity)
            return True

    def __sync_state_transition(self, requestid, wfinstanceid, _all_activity_desc, isallactivity):
        _all_activity_asc = FOIMinistryRequest.getactivitybyid(requestid)[::-1]  
        _activity_itr = _all_activity_asc if isallactivity == True else _all_activity_asc[:-1]        
        _variables = bpmservice().getinstancevariables(wfinstanceid)  
        entry_n_minus_1 = _activity_itr[-1]      
        print("previous state"+entry_n_minus_1["status"])
        if "status" not in _variables and entry_n_minus_1["status"] not in ("Open"):
            for entry in _all_activity_desc:
                if entry["status"] == OpenedEvent.callforrecords.value:
                    self.__sync_complete_event(requestid, wfinstanceid, entry)
                    _variables = bpmservice().getinstancevariables(wfinstanceid)
                    break            
            if entry_n_minus_1["status"] not in (UnopenedEvent.open.value,OpenedEvent.callforrecords.value) and _variables["status"]["value"] != entry_n_minus_1["status"]:
                self.__sync_complete_event(requestid, wfinstanceid, entry_n_minus_1)
            


    def __sync_complete_event(self, requestid, wfinstanceid, minrequest):
        requestsschema, data = self.__prepare_ministry_complete(minrequest)   
        self.postopenedevent(requestid, wfinstanceid, requestsschema, data, minrequest["status"], self.__getusertype(minrequest["status"]), True)        

    def create_unopened_instance(self, _rawinstance):
        try:
            return self.createinstance(RedisPublisherService().foirequestqueueredischannel, json.dumps(self.__prepare_raw_requestobj(_rawinstance)))
        except Exception as ex:
            logging.error(ex)

    def create_opened_instance(self, requestid, _rawinstance):    
        _req_ministries = FOIMinistryRequest.getministriesopenedbyuid(_rawinstance.requestid)    
        try:
            return self.postunopenedevent(requestid, _rawinstance.wfinstanceid, self.__prepare_raw_requestobj(_rawinstance), "Open", _req_ministries)
        except Exception as ex:
            logging.error(ex)

    def __prepare_raw_requestobj(self, _rawinstance):
        data = {}
        data['id'] = _rawinstance.requestid
        data['assignedGroup'] = _rawinstance.assignedgroup
        data['assignedTo'] = _rawinstance.assignedto
        return data 

    def __prepare_ministry_complete(self, ministryrequest):
        data = {}
        data['axisRequestId'] = ministryrequest["axisrequestid"]
        data['assignedgroup'] = ministryrequest["assignedgroup"]
        data['assignedto'] = ministryrequest["assignedto"]
        data['paymentExpiryDate'] = ""
        ministry = []
        ministry.append(ministryrequest)
        return data, {"ministries": ministry}

    def __getusertype(self, status):
        if status in ["Fee Estimate", "Harms Assessment", "Deduplication", "Records Review","Ministry Sign Off"]:
            return "ministry"
        return "iao"

    def __postopenedevent(self, id, filenumber, metadata, messagename, assignedgroup, assignedto, wfinstanceid, activity):
        if activity == Activity.complete.value:

            if self.__hasreopened(id, "ministryrequest") == True:
                bpmservice().reopenevent(wfinstanceid, metadata, MessageType.iaoreopen.value)
            else:
                bpmservice().openedcomplete(filenumber, metadata, messagename)   
        else:
            bpmservice().openedevent(filenumber, assignedgroup, assignedto, messagename)
         
    
    def __getopenedassigneevalue(self, requestsschema, property, usertype):
        if property == "assignedgroup":
            return self.__getvaluefromschema(requestsschema,"assignedgroup") if 'assignedgroup' in requestsschema else self.__getvaluefromschema(requestsschema,"assignedministrygroup")
        elif property == "assignedto":
            return self.__getvaluefromschema(requestsschema,"assignedto") if 'assignedto' in requestsschema else self.__getvaluefromschema(requestsschema,"assignedministryperson")
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

    def __ispaymentactive(self, foirequestid, ministryid):
        _payment = cfrfeeservice().getactivepayment(foirequestid, ministryid)
        return True if _payment is not None else False

    def __getvaluefromschema(self,requestsschema, property):
        return requestsschema.get(property) if property in requestsschema  else None 

    def __getvaluefromlist(self,attributes, property):
        for attribute in attributes:
            if property in attribute:
                return attribute.get(property)
            return ""
    
    def __getministrystatus(self,filenumber, version):
        ministryreq = FOIMinistryRequest.getrequestbyfilenumberandversion(filenumber,version-1)
        return ministryreq["requeststatus.name"]   

    def __getpreviousministrystatus(self,id):
        ministryreq = FOIMinistryRequest.getstatesummary(id)
        _len = len(ministryreq)
        if _len > 1:
            return ministryreq[1]["status"]
        elif _len == 1:
            return UnopenedEvent.intakeinprogress.value
        else:
            return None   

    def __getprevioustatusbyversion(self,id, version):
        ministryreq = FOIMinistryRequest.getstatesummary(id)
        _len = len(ministryreq)
        if _len > 1:
            for entry in ministryreq:
                if int(entry["version"]) < version:
                    return entry["status"]
        elif _len == 1:
            return UnopenedEvent.intakeinprogress.value
        else:
            return None  
    
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