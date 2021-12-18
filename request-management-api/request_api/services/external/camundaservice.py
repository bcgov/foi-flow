import requests
import os
from enum import Enum

"""
This class is reserved for workflow services integration.
Supported operations: claim

__author__      = "sumathi.thirumani@aot-technologies.com"

"""
class camundaservice:
    
    bpmEngineRestUrl = os.getenv('BPM_ENGINE_REST_URL')
    bpmTokenUrl =  os.getenv("BPM_TOKEN_URL")
    bpmClientId =  os.getenv("BPM_CLIENT_ID")
    bpmClientSecret =  os.getenv("BPM_CLIENT_SECRET")
    bpmGrantType =  os.getenv("BPM_GRANT_TYPE")
    
    
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

class VariableType(Enum):
    String = "String"