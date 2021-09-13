import requests
import os
import json
import ast
from enum import Enum
from request_api.schemas.external.bpmschema import VariableMessageSchema, VariableSchema 
from request_api.services.external.camundaservice import camundaservice, VariableType 
"""
This class is reserved for workflow DMNs integration.

__author__      = "sumathi.thirumani@aot-technologies.com"

"""
class dmnservice(camundaservice):
    
 
    @classmethod
    def evaluateAction(self, requestType, status, token=None):
        if self.bpmEngineRestUrl is not None:
            dataSchema = VariableMessageSchema().dump({ 
                                              "variables":{
                                                  "category": VariableSchema().dump({"type" : VariableType.String.value, "value": requestType}),
                                                  "status": VariableSchema().dump({"type" : VariableType.String.value, "value": status})
                                                  }
                                              })
            response = requests.post(self._getUrl_(self, BusinessRuleType.stateTransition.value), data=json.dumps(dataSchema), headers = self._getHeaders_(self,token))
            content =  response.content.decode('utf-8')
            if response.status_code == 200 and content != "[]":  
                result = json.loads(content)             
                return self.responseFormatter(self,result[0]["output"]["value"])
            else:
                return None
        return
    
     
        
    @classmethod
    def evaluateGroup(self, requestType, status, token=None):
        if self.bpmEngineRestUrl is not None:
            dataSchema = VariableMessageSchema().dump({ 
                                              "variables":{
                                                  "category": VariableSchema().dump({"type" : VariableType.String.value, "value": requestType}),
                                                  "status": VariableSchema().dump({"type" : VariableType.String.value, "value": status})
                                                  }
                                              })
            return requests.post(self._getUrl_(self, BusinessRuleType.groupMapping.value), data=json.dumps(dataSchema), headers = self._getHeaders_(self,token))
        else:
            return


    def _getUrl_(self, ruleType, skip = True):
        if skip == False:
             return self.bpmEngineRestUrl+"/decision-definition/key/"+ruleType+"/xml"
        else:
            return self.bpmEngineRestUrl+"/decision-definition/key/"+ruleType+"/evaluate"
    
    
    def responseFormatter(self, data):
        return data.replace("\n","").replace('"','').replace("'",'"')
    
class BusinessRuleType(Enum):
    groupMapping = "group-mapping"
    stateTransition = "state-transition-mapping"

