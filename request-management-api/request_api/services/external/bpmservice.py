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
    def unopenedevent(self,processinstanceid, userid, messagetype, token=None):
        if self.bpmEngineRestUrl is not None:
            messageschema = MessageSchema().dump({"processInstanceId": processinstanceid,
                                              "messageName": messagetype, 
                                              "processVariables":{
                                                  "assignedTo": VariableSchema().dump({"type" : VariableType.String.value, "value": userid})
                                                  }
                                              })
            return requests.post(self._getUrl_(messagetype), data=json.dumps(messageschema), headers = self._getHeaders_(token))
        else:
            return


    @classmethod
    def unopenedcomplete(self,processinstanceid, data, messagetype, token=None): 
        if self.bpmEngineRestUrl is not None:
            messageschema = MessageSchema().dump({"processInstanceId": processinstanceid,
                                              "messageName": messagetype, 
                                              "processVariables":{
                                                  "foiRequestMetaData": VariableSchema().dump({"data" : VariableType.String.value, "value": data})
                                                  }
                                              })
            return requests.post(self._getUrl_(messagetype), data=json.dumps(messageschema), headers = self._getHeaders_(token))
        else:
            return
        
        
    @classmethod
    def openedevent(self, filenumber, groupname, userid, messagetype, token=None):
        if self.bpmEngineRestUrl is not None:
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
 
        
    @classmethod
    def openedcomplete(self,filenumber, data, messagetype, token=None):
        if self.bpmEngineRestUrl is not None:
            messageschema = MessageSchema().dump({"messageName": messagetype,
                                              "localCorrelationKeys":{
                                                  "id": VariableSchema().dump({"type" : VariableType.String.value, "value": filenumber})
                                                  },
                                              "processVariables":{
                                                  "foiRequestMetaData": VariableSchema().dump({"data" : VariableType.String.value, "value": data})}
                                              })
            return requests.post(self._getUrl_(messagetype), data=json.dumps(messageschema), headers = self._getHeaders_(token))
        else:
            return    
 

    @classmethod
    def reopenevent(self,processinstanceid, data, messagetype, token=None): 
        return self.unopenedcomplete(processinstanceid, data, messagetype, token)


    @classmethod
    def _getUrl_(self, messagetype):
        if messagetype is not None:
            return self.bpmEngineRestUrl+"/message"
        return self.bpmEngineRestUrl
    
    @classmethod
    def _getserviceaccounttoken_(self):
        auth_response = requests.post(self.bpmTokenUrl, auth=(self.bpmClientId, self.bpmClientSecret), headers={
            'Content-Type': 'application/x-www-form-urlencoded'}, data='grant_type=client_credentials')
        return auth_response.json().get('access_token')
    
    @classmethod
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
              
     