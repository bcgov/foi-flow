import pytest
from request_api.services.rawrequestservice import rawrequestservice
import json
import uuid




with open('tests/samplerequestjson/rawrequest.json') as f:
  requestjson = json.load(f)

def pytest_namespace():
    return {'requestidtoupdate': 0}

def test_get_rawrequests(session):
    response = rawrequestservice().getrawrequests()
    assert response
    requestid =''   
    for item in response:
        requestid = item['id']        
        assert item['id'] and item['requestType']
    getresponse = rawrequestservice().getrawrequest(requestid)
    assert getresponse['requestType']        


