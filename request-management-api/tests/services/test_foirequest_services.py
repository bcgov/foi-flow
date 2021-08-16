import pytest
from request_api.services.requestservice import requestservice
import json


with open('tests/samplerequestjson/foirequest-general.json') as f:
  generalrequestjson = json.load(f)
with open('tests/samplerequestjson/foirequest-personal.json') as f:
  personalrequestjson = json.load(f)
def pytest_namespace():
    return {'requestidtoupdate': 0}

def test_save_rawrequest(session):
    response = requestservice.saverequest(generalrequestjson)
    assert response.success == True
    requestid = response.identifier
    for item in response.args[0]:     
      assert item['id']
      requestmessage = requestservice.getrequest(requestid,item['id'])
      assert requestmessage["currentState"]

def test_save_rawrequestversion(session):
    response = requestservice.saverequest(personalrequestjson)  
    assert response.success == True
    requestid = response.identifier
    for item in response.args[0]:     
      assert item['id']
      requestmessage = requestservice.getrequest(requestid,item['id'])
      assert requestmessage["currentState"]  


