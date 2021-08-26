import requests
import os
import json
from enum import Enum
from request_api.schemas.external.bpmschema import MessageSchema, VariableSchema 

"""
This class is reserved for workflow services integration.
Supported operations: claim

__author__      = "sumathi.thirumani@aot-technologies.com"

"""
class bpmservice:
    
    bpmEngineRestUrl = os.getenv('BPM_ENGINE_REST_URL')
    bpmTokenUrl =  os.getenv("BPM_TOKEN_URL")
    bpmClientId =  os.getenv("BPM_CLIENT_ID")
    bpmClientSecret =  os.getenv("BPM_CLIENT_SECRET")
    bpmGrantType =  os.getenv("BPM_GRANT_TYPE")
    
    @classmethod
    def unopenedClaim(self,processInstanceId, userId, token=None):
        if self._isEnabled == True:
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
        if self._isEnabled == True:
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
    def complete(self,processInstanceId, data, token=None): 
        if self._isEnabled == True:
            messageSchema = MessageSchema().dump({"processInstanceId": processInstanceId,
                                              "messageName": MessageType.openrequest.value, 
                                              "processVariables":{
                                                  "foiRequestMetaData": VariableSchema().dump({"data" : VariableType.String.value, "value": data})
                                                  }
                                              })
            return requests.post(self._getUrl_(self,MessageType.openrequest.value), data=json.dumps(messageSchema), headers = self._getHeaders_(self,token))
        else:
            return

    def _getUrl_(self, messageType):
        if(MessageType.unopenedClaim.value == messageType or MessageType.openrequest.value == messageType or MessageType.openedClaim.value == messageType):
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

    def _isEnabled(self):
        print(self.bpmEngineRestUrl)
        if self.bpmEngineRestUrl is not None:
            return True
        else:
            return False

class MessageType(Enum):
    unopenedClaim = "foi-unopened-assignment"
    openedClaim = "foi-opened-assignment"
    openrequest = "foi-open-request"
    
class VariableType(Enum):
    String = "String"
             
     