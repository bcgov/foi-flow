import requests
import os
import json
from enum import Enum
from request_api.exceptions import BusinessException
from request_api.utils.redispublisher import RedisPublisherService
from request_api.services.external.bpmservice import MessageType, bpmservice, ProcessDefinitionKey
from request_api.services.cfrfeeservice import cfrfeeservice
from request_api.services.paymentservice import paymentservice
from request_api.models.FOIRawRequests import FOIRawRequest
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIRequests import FOIRequest
from request_api.utils.enums import StateName
import logging
from request_api.schemas.external.bpmschema import VariableSchema
from request_api.services.external.camundaservice import VariableType 
"""
This class is reserved for workflow services integration.
Supported operations: claim

__author__      = "sumathi.thirumani@aot-technologies.com"

"""
class workflowservice:

    def createinstance(self, definitionkey, message):
        response = bpmservice().createinstance(definitionkey, json.loads(message))
        if response is None:
            raise BusinessException("Unable to create instance for key"+ definitionkey)
        return response

    def postunopenedevent(self, id, wfinstanceid, requestsschema, status, ministries=None):        
        if wfinstanceid in (None,""):
            logging.error("WF INSTANCE IS INVALID")
            return
        assignedgroup = requestsschema["assignedGroup"] if 'assignedGroup' in requestsschema  else None
        assignedto = requestsschema["assignedTo"] if 'assignedTo' in requestsschema  else None
        print("id = ", id)
        print("status === ",status)
        if status == UnopenedEvent.intakeinprogress.value:
            messagename = MessageType.intakereopen.value if self.__hasreopened(id, "rawrequest") == True else MessageType.intakeclaim.value
            print("messagename == ",messagename)
            return bpmservice().unopenedsave(wfinstanceid, assignedto, messagename)                 
        else:
            if status == UnopenedEvent.open.value:
                metadata = json.dumps({"id": id, "status": status, "ministries": ministries, "assignedGroup": assignedgroup, "assignedTo": assignedto})
            else:            
                metadata = json.dumps({"id": id, "status": status, "assignedGroup": assignedgroup, "assignedTo": assignedto})
            print("metadata = ",metadata)
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
                    print("issync == ", issync)
                    print("ministry == ", ministry)
                    print("postopenedevent metadata === ", metadata)
                    if issync == True:                        
                        _variables = bpmservice().getinstancevariables(wfinstanceid)    
                        if ministry["status"] == OpenedEvent.callforrecords.value and (("status" not in _variables) or (_variables not in (None, []) and "status" in _variables and _variables["status"]["value"] != OpenedEvent.callforrecords.value)):
                            messagename = MessageType.iaoopencomplete.value
                        elif  _variables not in (None, []) and ("status" in _variables and _variables["status"]["value"] == "Closed"):
                            return bpmservice().reopenevent(wfinstanceid, metadata, MessageType.iaoreopen.value)                     
                        else:
                            return bpmservice().openedcomplete(wfinstanceid, filenumber, metadata, messagename)       
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
            # Sync and get raw instance details from FOI DB
            raw_metadata = self.__sync_raw_request(requesttype, requestid)
            if requesttype == "ministryrequest":
                req_metadata = self.__sync_foi_request(requestid, raw_metadata)     
                # Check foi request instance creation - Reconcile by transition to Open
                _all_activity_desc = FOIMinistryRequest.getactivitybyid(requestid)             
                self.__sync_state_transition(requestid, str(req_metadata.wfinstanceid), _all_activity_desc, isallactivity)
                return req_metadata.wfinstanceid            
            return raw_metadata.wfinstanceid 
        except Exception as ex:
            logging.error(ex)
        return None

    def __sync_raw_request(self, requesttype, requestid):
        # Search for WF ID 
        requestid = int(requestid)
        _raw_metadata = FOIRawRequest.getworkflowinstancebyraw(requestid) if requesttype == "rawrequest" else FOIRawRequest.getworkflowinstancebyministry(requestid)
        wf_rawrequest_pid = self.__get_wf_pid("rawrequest", _raw_metadata)    
        # Check for exists - Reconcile with new instance creation
        if wf_rawrequest_pid not in  (None, "") and _raw_metadata.wfinstanceid not in (None, "") and str(_raw_metadata.wfinstanceid) == wf_rawrequest_pid:
            return _raw_metadata
        # WF Instance is not present
        if wf_rawrequest_pid in (None, ""):
            print("Recreate instance")
            self.createinstance(RedisPublisherService().foirequestqueueredischannel, json.dumps(self.__prepare_raw_requestobj(_raw_metadata)))
        else:
            if _raw_metadata.wfinstanceid in (None, "") or str(_raw_metadata.wfinstanceid) != wf_rawrequest_pid:
                FOIRawRequest.updateworkflowinstance_n(wf_rawrequest_pid, int(_raw_metadata.requestid), "System")
        return FOIRawRequest.getworkflowinstancebyraw(requestid) if requesttype == "rawrequest" else FOIRawRequest.getworkflowinstancebyministry(requestid)      

    def __sync_foi_request(self, requestid, raw_metadata):
        requestid = int(requestid)
        _req_metadata = FOIRequest.getworkflowinstance(requestid)
        wf_foirequest_pid = self.__get_wf_pid("ministryrequest", raw_metadata, _req_metadata)
        print("wf_foirequest_pid == ", wf_foirequest_pid)
        if wf_foirequest_pid not in (None, "") and _req_metadata.wfinstanceid not in (None, "") and str(_req_metadata.wfinstanceid) == wf_foirequest_pid:
            return _req_metadata
        if wf_foirequest_pid in (None, ""):
            print("wf_foirequest_pid None")
            _req_ministries = FOIMinistryRequest.getministriesopenedbyuid(raw_metadata.requestid) 
            self.postunopenedevent(requestid, raw_metadata.wfinstanceid, self.__prepare_raw_requestobj(raw_metadata), UnopenedEvent.open.value, _req_ministries)
        else:
            if _req_metadata.wfinstanceid in (None, "") or str(_req_metadata.wfinstanceid) != wf_foirequest_pid:
                FOIRequest.updateWFInstance(_req_metadata.foirequestid, wf_foirequest_pid, "System")  
        return FOIRequest.getworkflowinstance(requestid)

    def __get_wf_pid(self, requesttype, _raw_metadata, _req_metadata=None):
        if requesttype == "rawrequest":
            searchby = [{"name":"id" ,"operator":"eq","value": int(_raw_metadata.requestid)}]
            return bpmservice().searchinstancebyvariable(ProcessDefinitionKey.rawrequest.value, searchby)  
        elif requesttype == "ministryrequest":
            searchby = [{"name":"foiRequestID","operator":"eq","value": int(_req_metadata.foirequestid)},
                    {"name": "rawRequestPID","operator":"eq","value": str(_raw_metadata.wfinstanceid)}]
            wf_foirequest_pid = bpmservice().searchinstancebyvariable(ProcessDefinitionKey.ministryrequest.value, searchby)
            if wf_foirequest_pid in (None, ""):
                searchby = [{"name":"foiRequestID","operator":"eq","value": str(_req_metadata.foirequestid)},
                    {"name": "rawRequestPID","operator":"eq","value": str(_raw_metadata.wfinstanceid)}]
                wf_foirequest_pid = bpmservice().searchinstancebyvariable(ProcessDefinitionKey.ministryrequest.value, searchby) 
            return wf_foirequest_pid   
        else:
            logging.info("Unknown requestype %s", requesttype)
            return None

    def __sync_state_transition(self, requestid, wfinstanceid, _all_activity_desc, isallactivity): 
        current = _all_activity_desc[0]
        previous = _all_activity_desc[1] if len(_all_activity_desc) > 1 else _all_activity_desc[0]
        _activity_itr_desc = _all_activity_desc
        if isallactivity == False:
            _activity_itr_desc.pop(0)
        _variables = bpmservice().getinstancevariables(wfinstanceid)  
        # SP: Stuck in Open -> Move from Open to CFR
        if _variables not in (None, []) and "status" not in _variables:
            for entry in _activity_itr_desc:
                if entry["status"] == OpenedEvent.callforrecords.value and ((isallactivity == True) or (isallactivity == False and current["status"] != OpenedEvent.callforrecords.value)):
                    self.__sync_complete_event(requestid, wfinstanceid, entry)
                    break
        # Sync action
        _variables = bpmservice().getinstancevariables(wfinstanceid)
        oldstatus = self.__getministrystatus(current["filenumber"], current["version"])             
        activity = Activity.save.value if isallactivity == True else self.__getministryactivity(oldstatus,current["status"])
        if _variables not in (None, []) and "status" in _variables:
            if activity == Activity.save.value and _variables["status"]["value"] != current["status"]:
                self.__sync_complete_event(requestid, wfinstanceid, current)   
            if activity == Activity.complete.value and _variables["status"]["value"] != previous["status"]:   
                self.__sync_complete_event(requestid, wfinstanceid, previous)        

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
        print("activity == ", activity)
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