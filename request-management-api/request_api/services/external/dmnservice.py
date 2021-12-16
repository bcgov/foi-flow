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
    
 
    def evaluateAction(self, requesttype, status, token=None):
        if self.bpmEngineRestUrl is not None:
            dataschema = VariableMessageSchema().dump({ 
                                              "variables":{
                                                  "category": VariableSchema().dump({"type" : VariableType.String.value, "value": requesttype}),
                                                  "status": VariableSchema().dump({"type" : VariableType.String.value, "value": status})
                                                  }
                                              })
            response = requests.post(self._getUrl_(self, BusinessRuleType.stateTransition.value), data=json.dumps(dataschema), headers = self._getHeaders_(self,token))
            content =  response.content.decode('utf-8')
            if response.status_code == 200 and content != "[]":  
                result = json.loads(content)             
                return self.__responseformatter(result[0]["output"]["value"])
            else:
                return None
    
     
        
    def evaluateGroup(self, requesttype, status, token=None):
        if self.bpmEngineRestUrl is not None:
            dataschema = VariableMessageSchema().dump({ 
                                              "variables":{
                                                  "category": VariableSchema().dump({"type" : VariableType.String.value, "value": requesttype}),
                                                  "status": VariableSchema().dump({"type" : VariableType.String.value, "value": status})
                                                  }
                                              })
            return requests.post(self._getUrl_(self, BusinessRuleType.groupMapping.value), data=json.dumps(dataschema), headers = self._getHeaders_(self,token))
        else:
            return


    def _getUrl_(self, ruletype, skip = True):
        if skip == False:
             return self.bpmEngineRestUrl+"/decision-definition/key/"+ruletype+"/xml"
        else:
            return self.bpmEngineRestUrl+"/decision-definition/key/"+ruletype+"/evaluate"
    
    
    def __responseformatter(self, data):
        return data.replace("\n","").replace('"','').replace("'",'"')
    
class BusinessRuleType(Enum):
    groupMapping = "group-mapping"
    stateTransition = "state-transition-mapping"

