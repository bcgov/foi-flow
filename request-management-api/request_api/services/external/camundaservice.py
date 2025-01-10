import requests
import os
from enum import Enum

"""
This class is reserved for workflow services integration.
Supported operations: claim

__author__      = "sumathi.thirumani@aot-technologies.com"

"""
class camundaservice:
    
    bpmengineresturl = os.getenv('BPM_ENGINE_REST_URL')
    bpmtokenurl =  os.getenv("BPM_TOKEN_URL")
    bpmclientid =  os.getenv("BPM_CLIENT_ID")
    bpmclientsecret =  os.getenv("BPM_CLIENT_SECRET")
    bpmgranttype =  os.getenv("BPM_GRANT_TYPE")
    
    
    def _getserviceaccounttoken_(self):
        auth_response = requests.post(self.bpmtokenurl, auth=(self.bpmclientid, self.bpmclientsecret), headers={
            'Content-Type': 'application/x-www-form-urlencoded'}, data='grant_type=client_credentials')
        return auth_response.json().get('access_token')
    
    
    def _getheaders_(self, token):
        """Generate headers."""
        if token is None:
            token = self._getserviceaccounttoken_();
        return {
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json",
        }

class VariableType(Enum):
    String = "String"
    Integer = "Integer"