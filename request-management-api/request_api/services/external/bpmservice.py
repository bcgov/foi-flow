import requests
import os
import json
from enum import Enum
from request_api.schemas.external.bpmschema import MessageSchema, ProcessVariableSchema 

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
    def claim(self,processInstanceId, userId, token=None):    
        messageSchema = MessageSchema().dump({"processInstanceId": processInstanceId, 
                                              "messageName": MessageType.claim.value, 
                                              "processVariables":{
                                                  "assignedTo": ProcessVariableSchema().dump({"type" : VariableType.String.value, "value": userId})
                                                  }
                                              })
        return requests.post(self._getUrl_(self,MessageType.claim.value), data=json.dumps(messageSchema), headers = self._getHeaders_(self,token))

    @classmethod
    def complete(self,processInstanceId, data, token=None): 
           
        messageSchema = MessageSchema().dump({"processInstanceId": processInstanceId, 
                                              "messageName": MessageType.openrequest.value, 
                                              "processVariables":{
                                                  "foiRequestMetaData": ProcessVariableSchema().dump({"data" : VariableType.String.value, "value": data})
                                                  }
                                              })
        return requests.post(self._getUrl_(self,MessageType.claim.value), data=json.dumps(messageSchema), headers = self._getHeaders_(self,token))
        

    def _getUrl_(self, messageType):
        if(MessageType.claim.value == messageType or MessageType.openrequest.value == messageType):
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
    claim = "foi-unopened-assignment"
    openrequest = "foi-open-request"
    
class VariableType(Enum):
    String = "String"
             
     