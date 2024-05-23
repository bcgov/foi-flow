import pytest
from request_api.services.extensionservice import extensionservice
import json
import uuid




with open('tests/samplerequestjson/foirequest-extension-oipc.json') as f:
  requestjson = json.load(f)

def pytest_namespace():
    return {'requestidtoupdate': 0}

def test_create_extension(session):
    requestid = 1
    ministryrequestid = 1    
    response = extensionservice().createrequestextension(requestid, ministryrequestid, requestjson, userid='dviswana@idir')
    requestid = response.identifier
    pytest.approxrequestidtoupdate = requestid    
    assert response.success == True 

def test_get_request_extensions(session):
    requestid = 1
    extensions = extensionservice().getrequestextensions(requestid)
    for extension in extensions:
      assert extension["extensionreson"]     


