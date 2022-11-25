import requests
import os
import json
from enum import Enum
from request_api.exceptions import BusinessException
from request_api.utils.redispublisher import RedisPublisherService
from request_api.services.external.bpmservice import MessageType, bpmservice
from request_api.services.cfrfeeservice import cfrfeeservice
from request_api.services.paymentservice import paymentservice
from request_api.models.FOIRawRequests import FOIRawRequest
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIRequests import FOIRequest
from request_api.utils.enums import StateName
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
        if wfinstanceid in (None,""):
            logging.error("WF INSTANCE IS INVALID")
            return
        assignedgroup = requestsschema["assignedGroup"] if 'assignedGroup' in requestsschema  else None
        assignedto = requestsschema["assignedTo"] if 'assignedTo' in requestsschema  else None 
        if status == UnopenedEvent.intakeinprogress.value:
            messagename = MessageType.intakereopen.value if self.__hasreopened(id, "rawrequest") == True else MessageType.intakeclaim.value
            return bpmservice().unopenedsave(wfinstanceid, assignedto, messagename)                 
        else:
            if status == UnopenedEvent.open.value:
                metadata = json.dumps({"id": id, "status": status, "ministries": ministries, "assignedGroup": assignedgroup, "assignedTo": assignedto})
            else:            
                metadata = json.dumps({"id": id, "status": status, "assignedGroup": assignedgroup, "assignedTo": assignedto})
            return bpmservice().unopenedcomplete(wfinstanceid, metadata, MessageType.intakecomplete.value) 

    def postopenedevent(self, id, wfinstanceid, requestsschema, data, newstatus, usertype, issync=False):
        assignedgroup = self.__getopenedassigneevalue(requestsschema, "assignedgroup",usertype) 
        assignedto = self.__getopenedassigneevalue(requestsschema, "assignedto",usertype)        
        axisrequestid = self.__getvaluefromschema(requestsschema,"axisRequestId")
        if data.get("ministries") is not None:
            for ministry in data.get("ministries"): 
                filenumber =  ministry["filenumber"] 
                if int(ministry["id"]) == int(id): 
                    paymentexpirydate = paymentservice().getpaymentexpirydate(int(ministry["foirequestid"]), int(ministry["id"]))                     
                    previousstatus =  self.__getpreviousministrystatus(id) if issync == False else self.__getprevioustatusbyversion(id, int(ministry["version"]))
                    oldstatus = self.__getministrystatus(filenumber, ministry["version"]) if issync == False else previousstatus                
                    activity = self.__getministryactivity(oldstatus,newstatus) if issync == False else Activity.complete.value
                    isprocessing = self.__isprocessing(id) if issync == False else False  
                    messagename = self.__messagename(oldstatus, activity, usertype, isprocessing)
                    metadata = json.dumps({"id": filenumber, "previousstatus":previousstatus, "status": ministry["status"] , "assignedGroup": assignedgroup, "assignedTo": assignedto, "assignedministrygroup":ministry["assignedministrygroup"], "ministryRequestID": id, "isPaymentActive": self.__ispaymentactive(ministry["foirequestid"], id), "paymentExpiryDate": paymentexpirydate, "axisRequestId": axisrequestid, "issync": issync})
                    if issync == True:                        
                        _variables = bpmservice().getinstancevariables(wfinstanceid)    
                        if ministry["status"] == OpenedEvent.callforrecords.value:
                            messagename = MessageType.iaoopencomplete.value
                        if _variables not in (None, []) and "status" in _variables and _variables["status"]["value"] == "Closed":
                            return bpmservice().reopenevent(wfinstanceid, metadata, MessageType.iaoreopen.value)                     
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
    
    def postcorrenspodenceevent(self, wfinstanceid, ministryid, requestsschema, applicantcorrespondenceid, templatename, attributes):
        paymentexpirydate = self.__getvaluefromlist(attributes,"paymentExpiryDate")
        axisrequestid = self.__getvaluefromschema(requestsschema,"axisRequestId")
        filenumber = self.__getvaluefromschema(requestsschema,"idNumber")
        status = self.__getvaluefromschema(requestsschema,"currentState")
        metadata = json.dumps({"id": filenumber, "status": status , "ministryRequestID": ministryid, "paymentExpiryDate": paymentexpirydate, "axisRequestId": axisrequestid, "applicantcorrespondenceid": applicantcorrespondenceid, "templatename": templatename.replace(" ", "")})
        bpmservice().correspondanceevent(wfinstanceid, filenumber, metadata)

    def syncwfinstance(self, requesttype, requestid, isallactivity=False):      
        try:
            _raw_metadata = FOIRawRequest.getworkflowinstancebyraw(requestid) if requesttype == "rawrequest" else FOIRawRequest.getworkflowinstancebyministry(requestid)
            # Check raw request instance creation - Reconcile with new instance creation
            if _raw_metadata.wfinstanceid in (None, ""):
                self.createinstance(RedisPublisherService().foirequestqueueredischannel, json.dumps(self.__prepare_raw_requestobj(_raw_metadata)))
            #Get updated raw PID
            _raw_metadata_n = FOIRawRequest.getworkflowinstancebyraw(requestid) if requesttype == "rawrequest" else FOIRawRequest.getworkflowinstancebyministry(requestid)
            if requesttype == "ministryrequest":
                _req_metadata = FOIRequest.getworkflowinstance(requestid)   #address correlation N 
                #Search WF Engine using raw PID                
                wf_foirequest_pid = bpmservice().searchinstancebyvariable("foi-request-processing", "rawRequestPID", _raw_metadata_n.wfinstanceid)
                # FOI - NO | WF - YES 
                if _req_metadata.wfinstanceid in (None, "") and wf_foirequest_pid not in (None, ""):
                    FOIRequest.updateWFInstance(_req_metadata.foirequestid, wf_foirequest_pid, "System")  
                    _req_metadata.__dict__.update({"wfinstanceid":wf_foirequest_pid})
                # FOI - YES | WF - NO and FOI - NO  | WF - NO 
                if (_req_metadata.wfinstanceid not in (None, "") and wf_foirequest_pid in (None, "")) or (_req_metadata.wfinstanceid in (None, "") and wf_foirequest_pid in (None, "")): 
                    _req_ministries = FOIMinistryRequest.getministriesopenedbyuid(_raw_metadata_n.requestid) 
                    self.postunopenedevent(requestid, _raw_metadata_n.wfinstanceid, self.__prepare_raw_requestobj(_raw_metadata_n), UnopenedEvent.open.value, _req_ministries)
                # WF - YES | FOI - YES - No Action Required

                # Check foi request instance creation - Reconcile by transition to Open
                _all_activity_desc = FOIMinistryRequest.getactivitybyid(requestid)             
                _req_metadata_n = FOIRequest.getworkflowinstance(requestid)            
                # Check Current status in WF engine
                #if _req_metadata_n.wfinstanceid in (None, ""):
                    #self.syncwfinstance("ministryrequest", requestid, isallactivity)
                #else:
                self.__sync_state_transition(requestid, _req_metadata_n.wfinstanceid, _all_activity_desc, isallactivity)
                return _req_metadata_n.wfinstanceid
            
            return _raw_metadata_n.wfinstanceid 
        except Exception as ex:
            logging.error(ex)
        return None

    def __sync_state_transition(self, requestid, wfinstanceid, _all_activity_desc, isallactivity): 
        current = _all_activity_desc[0]
        previous = _all_activity_desc[1] if len(_all_activity_desc) > 1 else _all_activity_desc[0]
        _activity_itr_desc = _all_activity_desc
        if isallactivity == False:
            _activity_itr_desc.pop(0)
        _variables = bpmservice().getinstancevariables(wfinstanceid)  
                
        # No instance or (WF in Open state) and (previous state != Open) -> Move from Open to CFR
        #and entry_n["status"] not in (UnopenedEvent.open.value)
        if _variables in (None, []) or (_variables not in (None, []) and "status" not in _variables):
            for entry in _activity_itr_desc:
                if entry["status"] == OpenedEvent.callforrecords.value and current["status"] != OpenedEvent.callforrecords.value:
                    self.__sync_complete_event(requestid, wfinstanceid, entry)
                    break
        # Sync action
        data = current if isallactivity == True else previous
        _variables = bpmservice().getinstancevariables(wfinstanceid)
        if _variables in (None, []) or (_variables not in (None, []) and "status" in _variables and _variables["status"]["value"] != data["status"]):
            self.__sync_complete_event(requestid, wfinstanceid, data)            

    def __sync_complete_event(self, requestid, wfinstanceid, minrequest):
        requestsschema, data = self.__prepare_ministry_complete(minrequest)   
        self.postopenedevent(requestid, wfinstanceid, requestsschema, data, minrequest["status"], self.__getusertype(minrequest["status"]), True)        

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
        if status in [StateName.feeestimate.value, StateName.harmsassessment.value, StateName.deduplication.value, StateName.recordsreview.value, StateName.ministrysignoff.value]:
            return UserType.ministry.value
        return UserType.iao.value

    def __postopenedevent(self, id, filenumber, metadata, messagename, assignedgroup, assignedto, wfinstanceid, activity):
        if activity == Activity.complete.value:

            if self.__hasreopened(id, "ministryrequest") == True:
                bpmservice().reopenevent(wfinstanceid, metadata, MessageType.iaoreopen.value)
            else:
                bpmservice().openedcomplete(wfinstanceid, filenumber, metadata, messagename)   
        else:
            bpmservice().unopenedsave(filenumber, assignedgroup, assignedto, messagename)
         
    
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
            if newstate != oldstate and oldstate == UnopenedEvent.closed.value:
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