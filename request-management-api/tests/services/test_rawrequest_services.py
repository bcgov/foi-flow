import pytest
from request_api.services.rawrequestservice import rawrequestservice
import json
import uuid




with open('tests/samplerequestjson/rawrequest.json') as f:
  requestjson = json.load(f)

def pytest_namespace():
    return {'requestidtoupdate': 0}

def test_save_rawrequest(session):
    response = rawrequestservice.saverawrequest(requestjson,'onlineform',None)
    requestid = response.identifier
    pytest.approxrequestidtoupdate = requestid
    wfupdateresponse = rawrequestservice.updateworkflowinstance(str(uuid.uuid4()),requestid,'service-account-forms-flow-bpm')
    assert response.success == True and wfupdateresponse.success == True

def test_save_rawrequestversion(session):
    request = rawrequestservice.getrawrequests().pop()
    print("Raw Request id {0}".format(request['id']))
    #_assigneeGroup, _assignee,status
    response = rawrequestservice.saverawrequestversion(requestjson,request['id'],"testuser@idir",_assignee="testassigne",status='intake in progress')
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
    assert getresponse['requestType']        


