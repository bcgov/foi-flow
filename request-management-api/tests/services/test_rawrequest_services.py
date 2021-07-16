import re
from request_api.services.rawrequestservice import rawrequestservice
import json



with open('tests/samplerequestjson/rawrequest.json') as f:
  requestjson = json.load(f)
def test_save_rawrequest(session):
    response = rawrequestservice.saverawrequest(requestjson)
    requestid = response.identifier        
    assert response.success == True

def test_get_rawrequests(session):
    response = rawrequestservice.getrawrequests()
    assert response
    requestid =''
    # assert the structure is correct by checking for name, description properties in each element
    for item in response:
        requestid = item['id']        
        assert item['id'] and item['requestType']
    getresponse = rawrequestservice.getrawrequest(requestid)
    assert getresponse['id'] and getresponse['requestType']        


