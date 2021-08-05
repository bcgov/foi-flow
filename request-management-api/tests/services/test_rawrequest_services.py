import pytest
from request_api.services.rawrequestservice import rawrequestservice
import json
import uuid




with open('tests/samplerequestjson/rawrequest.json') as f:
  requestjson = json.load(f)

def pytest_namespace():
    return {'requestidtoupdate': 0}

def test_save_rawrequest(session):
    response = rawrequestservice.saverawrequest(requestjson,'onlineform')
    requestid = response.identifier
    pytest.approxrequestidtoupdate = requestid
    wfupdateresponse = rawrequestservice.updateworkflowinstance(str(uuid.uuid4()),requestid)
    assert response.success == True and wfupdateresponse.success == True

def test_save_rawrequestversion(session):
    request = rawrequestservice.getrawrequests().pop()
    response = rawrequestservice.saverawrequestversion(requestjson,request['id'],"testuser@idir",'intake in progress')
    requestid = response.identifier    
    assert response.success == True  

def test_get_rawrequests(session):
    response = rawrequestservice.getrawrequests()
    assert response
    requestid =''   
    for item in response:
        requestid = item['id']        
        assert item['id'] and item['requestType']
    getresponse = rawrequestservice.getrawrequest(requestid)
    assert getresponse['id'] and getresponse['requestType']        


