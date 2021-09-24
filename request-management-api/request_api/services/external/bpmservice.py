import requests
import os
import json
from enum import Enum

from request_api.schemas.external.bpmschema import MessageSchema, VariableSchema 
from request_api.services.external.camundaservice import camundaservice, VariableType 

"""
This class is reserved for workflow services integration.
Supported operations: claim

__author__      = "sumathi.thirumani@aot-technologies.com"

"""
class bpmservice(camundaservice):
    
     
    @classmethod
    def unopenedClaim(self,processInstanceId, userId, token=None):
        if self.bpmEngineRestUrl is not None:
            messageSchema = MessageSchema().dump({"processInstanceId": processInstanceId,
                                              "messageName": MessageType.unopenedClaim.value, 
                                              "processVariables":{
                                                  "assignedTo": VariableSchema().dump({"type" : VariableType.String.value, "value": userId})
                                                  }
                                              })
            return requests.post(self._getUrl_(self,MessageType.unopenedClaim.value), data=json.dumps(messageSchema), headers = self._getHeaders_(self,token))
        else:
            return
    @classmethod
    def openedclaim(self,fileNumber, groupName, userId, token=None):
        if self.bpmEngineRestUrl is not None:
            messageSchema = MessageSchema().dump({"messageName": MessageType.openedClaim.value,
                                              "localCorrelationKeys":{
                                                  "id": VariableSchema().dump({"type" : VariableType.String.value, "value": fileNumber})
                                                  },
                                              "processVariables":{
                                                  "filenumber": VariableSchema().dump({"type" : VariableType.String.value, "value": fileNumber}),
                                                  "assignedGroup": VariableSchema().dump({"type" : VariableType.String.value, "value": groupName}),
                                                  "assignedTo": VariableSchema().dump({"type" : VariableType.String.value, "value": userId})
                                                  }
                                              })
            return requests.post(self._getUrl_(self,MessageType.openedClaim.value), data=json.dumps(messageSchema), headers = self._getHeaders_(self,token))
        else:
            return     
        
    @classmethod
    def openedcomplete(self,fileNumber, data, messagetype, token=None):
        if self.bpmEngineRestUrl is not None:
            messageSchema = MessageSchema().dump({"messageName": messagetype,
                                              "localCorrelationKeys":{
                                                  "id": VariableSchema().dump({"type" : VariableType.String.value, "value": fileNumber})
                                                  },
                                              "processVariables":{
                                                  "foiRequestMetaData": VariableSchema().dump({"data" : VariableType.String.value, "value": data})}
                                              })
            return requests.post(self._getUrl_(self,messagetype), data=json.dumps(messageSchema), headers = self._getHeaders_(self,token))
        else:
            return    
 
    @classmethod
    def complete(self,processInstanceId, data, messagetype, token=None): 
        print(messagetype)
        if self.bpmEngineRestUrl is not None:
            print('before post')
            messageSchema = MessageSchema().dump({"processInstanceId": processInstanceId,
                                              "messageName": messagetype, 
                                              "processVariables":{
                                                  "foiRequestMetaData": VariableSchema().dump({"data" : VariableType.String.value, "value": data})
                                                  }
                                              })
            return requests.post(self._getUrl_(self,messagetype), data=json.dumps(messageSchema), headers = self._getHeaders_(self,token))
        else:
            return

    def _getUrl_(self, messageType):
        if(MessageType.unopenedClaim.value == messageType or MessageType.openrequest.value == messageType or MessageType.openedClaim.value == messageType or MessageType.openedcomplete.value == messageType):
            return self.bpmEngineRestUrl+"/message"
        return self.bpmEngineRestUrl
    
    
    def _getServiceAccountToken_(self):
        auth_response = requests.post(self.bpmTokenUrl, auth=(self.bpmClientId, self.bpmClientSecret), headers={
            'Content-Type': 'application/x-www-form-urlencoded'}, data='grant_type=client_credentials')
        return auth_response.json().get('access_token')
    
    
    def _getHeaders_(self, token):
        """Generate headers."""
        if token is None:
            token = self._getServiceAccountToken_(self);
        return {
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json",
        }



class MessageType(Enum):
    unopenedClaim = "foi-unopened-assignment"
    openedClaim = "foi-opened-assignment"
    openrequest = "foi-open-request"
    openedcomplete = "foi-opened-complete"
    

             
     