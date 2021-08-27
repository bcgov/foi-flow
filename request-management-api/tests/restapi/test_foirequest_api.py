import json
import uuid
import jwt, os

TEST_JWT_HEADER = {
    "alg": "RS256",
    "typ": "JWT",
    "kid": "foiunittest"
}

TEST_JWT_CLAIMS = {
    "iss": os.getenv('JWT_OIDC_ISSUER'),
    "sub": "3559e79c-7115-41c1-bb26-1a3dc54bbf5e",
    "typ": "Bearer",
    "aud": [os.getenv('JWT_OIDC_AUDIENCE')],
    "firstname": "Test",
    "lastname": "User",
    "preferred_username": "test@idir",
    "given_name": "TEST",
    "family_name": "TEST",
    "realm_access": {
        "roles": [
            "approver_role"
        ]
    },
    "groups": [   
    "/Flex Team"    
  ],
    "preferred_username": "user"
}

def factory_auth_header(jwt, claims):
    """Produce JWT tokens for use in tests."""
    return {'Authorization': 'Bearer ' + jwt.encode(payload=TEST_JWT_CLAIMS,key="secret",headers=TEST_JWT_HEADER)}

def test_ping(app, client):
    response = client.get('/api/healthz')
    assert response.status_code == 200

with open('tests/samplerequestjson/rawrequest.json') as x, open('tests/samplerequestjson/foirequest-general.json') as y:
  generalrequestjson = json.load(y)
  rawrequestjson = json.load(x)
def test_post_foirequest_general(app, client):
    rawresponse = client.post('/api/foirawrequests',data=json.dumps(rawrequestjson), content_type='application/json')
    jsondata = json.loads(rawresponse.data)    
    getrawresponse = client.get('/api/foirawrequest/'+str(jsondata["id"]), content_type='application/json')
    getrawjsondata = json.loads(getrawresponse.data)    
    #assert rawresponse.status_code == 200
    foirequest = generalrequestjson
    foirequest["id"] = str(jsondata["id"])
    foiresponse = client.post('/api/foirequests',data=json.dumps(foirequest), content_type='application/json')
    foijsondata = json.loads(foiresponse.data)    
    wfinstanceid={"wfinstanceid":str(uuid.uuid4())}
    wfupdateresponse = client.put('/api/foirawrequestbpm/addwfinstanceid/'+str(jsondata["id"]),data=json.dumps(wfinstanceid), content_type='application/json')
    assert foiresponse.status_code == 200 and wfupdateresponse.status_code == 200

with open('tests/samplerequestjson/rawrequest.json') as x, open('tests/samplerequestjson/foirequest-personal.json') as y:
  personalrequestjson = json.load(y)
  rawrequestjson = json.load(x)
def test_post_foirequest_personal(app, client):
    rawresponse = client.post('/api/foirawrequests',data=json.dumps(rawrequestjson), content_type='application/json')
    jsondata = json.loads(rawresponse.data)
    getrawresponse = client.get('/api/foirawrequest/'+str(jsondata["id"]), content_type='application/json')
    getrawjsondata = json.loads(getrawresponse.data)
    #assert rawresponse.status_code == 200
    foirequest = personalrequestjson
    foirequest["id"] = str(jsondata["id"])
    foiresponse = client.post('/api/foirequests',data=json.dumps(foirequest), content_type='application/json')
    foijsondata = json.loads(foiresponse.data)
    wfinstanceid={"wfinstanceid":str(uuid.uuid4())}
    wfupdateresponse = client.put('/api/foirawrequestbpm/addwfinstanceid/'+str(jsondata["id"]),data=json.dumps(wfinstanceid), content_type='application/json')
    assert foiresponse.status_code == 200 and wfupdateresponse.status_code == 200


def test_get_foirequestqueue(app, client):
  headers = factory_auth_header(jwt=jwt, claims=TEST_JWT_CLAIMS)  
  response = client.get('/api/dashboard', headers=headers)    
  jsondata = json.loads(response.data)
  assert response.status_code == 200    

def test_get_foirequestqueuewithoutheader(app, client):    
  response = client.get('/api/dashboard')    
  jsondata = json.loads(response.data)
  assert response.status_code == 401 # expecting Unauthorized - 401 status
