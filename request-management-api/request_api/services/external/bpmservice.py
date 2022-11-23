import requests
import os
import json
from enum import Enum

from request_api.schemas.external.bpmschema import MessageSchema, VariableSchema, VariableMessageSchema 
from request_api.services.external.camundaservice import camundaservice, VariableType 

"""
This class is reserved for workflow services integration.
Supported operations: claim

__author__      = "sumathi.thirumani@aot-technologies.com"

"""
class bpmservice(camundaservice):

    def createinstance(self, messagequeue, message, token=None):
        if self.bpmengineresturl is not None:
            _variables = {"variables":{}}
            for key in message:                
                    _variabletype = VariableType.Integer.value if key in ["id"] else  VariableType.String.value
                    _variables["variables"][key] = {"type" : _variabletype, "value": message[key]} 
            variableschema = VariableMessageSchema().dump(_variables)
            return requests.post(self._getUrl_(None,self._geProcessDefinitionKey_(messagequeue)), data=json.dumps(variableschema), headers = self._getHeaders_(token))
        else:
            return

    def getinstancevariables(self, instanceid, token=None):
        if self.bpmengineresturl is not None:
            response = requests.get(self.bpmengineresturl+"/process-instance/"+str(instanceid)+"/variables", headers = self._getHeaders_(token))
            return json.loads(response.content) if response.ok else None
        return None

    def unopenedsave(self,processinstanceid, userid, messagetype, token=None):
        if self.bpmengineresturl is not None:
            messageschema = MessageSchema().dump({"processInstanceId": processinstanceid,
                                              "messageName": messagetype, 
                                              "processVariables":{
                                                  "assignedTo": VariableSchema().dump({"type" : VariableType.String.value, "value": userid})
                                                  }
                                              })
            return self.__post_message(messagetype, messageschema, token)
        else:
            return


    def unopenedcomplete(self,processinstanceid, data, messagetype, token=None): 
        if self.bpmengineresturl is not None:
            messageschema = MessageSchema().dump({"processInstanceId": processinstanceid,
                                              "messageName": messagetype, 
                                              "processVariables":{
                                                  "foiRequestMetaData": VariableSchema().dump({"data" : VariableType.String.value, "value": data})
                                                  }
                                              })
            return self.__post_message(messagetype, messageschema, token)
        else:
            return
        
    """"       
    def opened(self, filenumber, groupname, userid, messagetype, token=None):
        if self.bpmengineresturl is not None:
            messageschema = MessageSchema().dump({"messageName": messagetype,
                                              "localCorrelationKeys":{
                                                  "id": VariableSchema().dump({"type" : VariableType.String.value, "value": filenumber})
                                                  },
                                              "processVariables":{
                                                  "filenumber": VariableSchema().dump({"type" : VariableType.String.value, "value": filenumber}),
                                                  "assignedGroup": VariableSchema().dump({"type" : VariableType.String.value, "value": groupname}),
                                                  "assignedTo": VariableSchema().dump({"type" : VariableType.String.value, "value": userid})
                                                  }
                                              })
            return requests.post(self._getUrl_(messagetype), data=json.dumps(messageschema), headers = self._getHeaders_(token))
        else:
            return   
    """

    def openedcomplete(self,filenumber, data, messagetype, token=None):
        if self.bpmengineresturl is not None:
            messageschema = MessageSchema().dump({"messageName": messagetype,
                                              "localCorrelationKeys":{
                                                  "id": VariableSchema().dump({"type" : VariableType.String.value, "value": filenumber})
                                                  },
                                              "processVariables":{
                                                  "foiRequestMetaData": VariableSchema().dump({"data" : VariableType.String.value, "value": data})}
                                              })
            return self.__post_message(messagetype, messageschema, token)
        else:
            return    
        
    def feeevent(self,axisrequestid, data, paymentstatus, token=None):
        if self.bpmengineresturl is not None:
            messageschema = MessageSchema().dump({"messageName": MessageType.managepayment.value,
                                            "correlationKeys":{
                                                "axisRequestId": VariableSchema().dump({"type" : VariableType.String.value, "value": axisrequestid})
                                            },
                                            "processVariables":{
                                                "foiRequestMetaData": VariableSchema().dump({"data" : VariableType.String.value, "value": data}),
                                                "paymentstatus": VariableSchema().dump({"type" : VariableType.String.value, "value": paymentstatus})}
                                            })
            return self.__post_message(MessageType.managepayment.value, messageschema, token)
        else:
            return

    def correspondanceevent(self,filenumber, data, token=None):
        if self.bpmengineresturl is not None:
            messageschema = MessageSchema().dump({"messageName": MessageType.iaocorrenspodence.value,
                                              "localCorrelationKeys":{
                                                  "id": VariableSchema().dump({"type" : VariableType.String.value, "value": filenumber})
                                                  },
                                              "processVariables":{
                                                  "foiRequestMetaData": VariableSchema().dump({"data" : VariableType.String.value, "value": data})}
                                              })
            return self.__post_message(MessageType.iaocorrenspodence.value, messageschema, token)
        else:
            return 
 
    def reopenevent(self,processinstanceid, data, messagetype, token=None): 
        return self.unopenedcomplete(processinstanceid, data, messagetype, token)

    def __post_message(self, messagetype, messageschema, token=None):
        return requests.post(self._getUrl_(messagetype), data=json.dumps(messageschema), headers = self._getHeaders_(token))

    def _getUrl_(self, messagetype, definitionkey=None):
        if messagetype is not None:
            return self.bpmengineresturl+"/message"
        elif definitionkey is not None:
            return self.bpmengineresturl+"/process-definition/key/"+definitionkey+"/start"
        return self.bpmengineresturl

    def _geProcessDefinitionKey_(self, messagequeue):
        if messagequeue == "foi-rawrequest":
            return "foi-request"
        return None

    def _getserviceaccounttoken_(self):
        auth_response = requests.post(self.bpmtokenurl, auth=(self.bpmclientid, self.bpmclientsecret), headers={
            'Content-Type': 'application/x-www-form-urlencoded'}, data='grant_type=client_credentials')
        return auth_response.json().get('access_token')
    
    def _getHeaders_(self, token):
        """Generate headers."""
        if token is None:
            token = self._getserviceaccounttoken_();
        return {
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json",
        }

class MessageType(Enum):
    intakeclaim = "foi-intake-assignment"    
    intakecomplete = "foi-intake-complete"
    intakereopen = "foi-intake-reopen"
    iaoopenclaim = "foi-iao-open-assignment"
    iaoopencomplete = "foi-iao-open-complete"  
    iaoclaim = "foi-iao-assignment"
    iaocomplete = "foi-iao-complete" 
    iaoreopen = "foi-iao-reopen"  
    ministryclaim = "foi-ministry-assignment"
    ministrycomplete = "foi-ministry-complete"   
    feepayment = "foi-fee-payment"
    managepayment = "foi-manage-payment"
    iaocorrenspodence = "foi-iao-correnspodence"
