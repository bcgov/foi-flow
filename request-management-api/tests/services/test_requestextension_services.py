import pytest
from request_api.services.extensionservice import extensionservice
import json
import uuid




with open('tests/samplerequestjson/foirequest-extension-oipc.json') as f:
  requestjson = json.load(f)

def pytest_namespace():
    return {'requestidtoupdate': 0}

def test_create_extension(session):
    #ministryrequestid, version, extensionschema['extension'], userid
    ministryrequestid = 1
    response = extensionservice().createrequestextnesion(ministryrequestid, requestjson, userid='dviswana@idir')
    requestid = response.identifier
    pytest.approxrequestidtoupdate = requestid    
    assert response.success == True      


