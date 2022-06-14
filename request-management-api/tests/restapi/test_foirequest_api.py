import json
import uuid
import jwt, os
import requests
import ast

TEST_USER_PAYLOAD = {
    'client_id': 'forms-flow-web',
    'grant_type': 'password',
    'username' : os.getenv('TEST_INTAKE_USERID'),
    'password': os.getenv('TEST_INTAKE_PASSWORD')
}

TEST_MINISTRYUSER_PAYLOAD = {
    'client_id': 'forms-flow-web',
    'grant_type': 'password',
    'username' : os.getenv('TEST_MINISTRY_USERID'),
    'password': os.getenv('TEST_MINISTRY_PASSWORD')
}

def factory_user_auth_header(app, client):
    url = '{0}/auth/realms/{1}/protocol/openid-connect/token'.format(os.getenv('KEYCLOAK_ADMIN_HOST'),os.getenv('KEYCLOAK_ADMIN_REALM'))        
    x = requests.post(url, TEST_USER_PAYLOAD, verify=True).content.decode('utf-8')       
    return {'Authorization': 'Bearer ' + str(ast.literal_eval(x)['access_token'])} 

def factory_ministryuser_auth_header(app, client):
    url = '{0}/auth/realms/{1}/protocol/openid-connect/token'.format(os.getenv('KEYCLOAK_ADMIN_HOST'),os.getenv('KEYCLOAK_ADMIN_REALM'))        
    x = requests.post(url, TEST_MINISTRYUSER_PAYLOAD, verify=True).content.decode('utf-8')
    return {'Authorization': 'Bearer ' + str(ast.literal_eval(x)['access_token'])}     

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

with open('tests/samplerequestjson/rawrequest.json') as x, open('tests/samplerequestjson/foirequest-general.json') as y, open('tests/samplerequestjson/foirequest-general-update.json') as z:
  generalrequestjson = json.load(y)
  generalupdaterequestjson = json.load(z)
  rawrequestjson = json.load(x)
def test_post_foirequest_general(app, client):
    rawresponse = client.post('/api/foirawrequests',data=json.dumps(rawrequestjson), headers=factory_user_auth_header(app, client), content_type='application/json')
    jsondata = json.loads(rawresponse.data)    
    getrawresponse = client.get('/api/foirawrequest/'+str(jsondata["id"]), headers=factory_user_auth_header(app, client), content_type='application/json') 
    foirequest = generalrequestjson
    foirequest["id"] = str(jsondata["id"])
    foirequest["requeststatusid"] = 1
    foiresponse = client.post('/api/foirequests',data=json.dumps(foirequest), headers=factory_user_auth_header(app, client), content_type='application/json')
    foijsondata = json.loads(foiresponse.data)    
    wfinstanceid={"wfinstanceid":str(uuid.uuid4())}
    wfupdateresponse = client.put('/api/foirawrequestbpm/addwfinstanceid/'+str(jsondata["id"]),data=json.dumps(wfinstanceid), headers=factory_user_auth_header(app, client), content_type='application/json')
    foiupdaterequest = generalupdaterequestjson
    foiupdaterequest["id"] = str(foijsondata["id"])
    foiupdaterequest["idNumber"] = str(foijsondata["ministryRequests"][0]["filenumber"])
    foiupdaterequest["cfrDueDate"] = '2020-01-02'
    foiassignresponse = client.post('/api/foirequests/'+str(foijsondata["id"])+'/ministryrequest/'+str(foijsondata["ministryRequests"][0]["id"]),data=json.dumps(foiupdaterequest), headers=factory_user_auth_header(app, client), content_type='application/json')
    assert foiresponse.status_code == 200 and getrawresponse.status_code == 200 and wfupdateresponse.status_code == 200 and foiassignresponse.status_code == 200

with open('tests/samplerequestjson/rawrequest.json') as x, open('tests/samplerequestjson/foirequest-personal.json') as y:
  personalrequestjson = json.load(y)
  rawrequestjson = json.load(x)
def test_post_foirequest_personal(app, client):
    rawresponse = client.post('/api/foirawrequests',data=json.dumps(rawrequestjson), headers=factory_user_auth_header(app, client), content_type='application/json')
    jsondata = json.loads(rawresponse.data)
    getrawresponse = client.get('/api/foirawrequest/'+str(jsondata["id"]), headers=factory_user_auth_header(app, client), content_type='application/json')
    getrawjsondata = json.loads(getrawresponse.data)
    #assert rawresponse.status_code == 200
    foirequest = personalrequestjson
    foirequest["id"] = str(jsondata["id"])
    foirequest["requeststatusid"] = 1
    foiresponse = client.post('/api/foirequests',data=json.dumps(foirequest), headers=factory_user_auth_header(app, client), content_type='application/json')
    foijsondata = json.loads(foiresponse.data)
    wfinstanceid={"wfinstanceid":str(uuid.uuid4())}
    wfupdateresponse = client.put('/api/foirawrequestbpm/addwfinstanceid/'+str(jsondata["id"]),data=json.dumps(wfinstanceid), headers=factory_user_auth_header(app, client), content_type='application/json')
    assert foiresponse.status_code == 200 and wfupdateresponse.status_code == 200


with open('tests/samplerequestjson/rawrequest.json') as x, open('tests/samplerequestjson/foirequest-general.json') as y, open('tests/samplerequestjson/foirequest-general-update.json') as z:
  generalrequestjson = json.load(y)
  generalupdaterequestjson = json.load(z)
  rawrequestjson = json.load(x)
def test_post_foirequest_general_closed(app, client):
    rawresponse = client.post('/api/foirawrequests',data=json.dumps(rawrequestjson), headers=factory_user_auth_header(app, client), content_type='application/json')
    jsondata = json.loads(rawresponse.data)    
    getrawresponse = client.get('/api/foirawrequest/'+str(jsondata["id"]), headers=factory_user_auth_header(app, client), content_type='application/json') 
    foirequest = generalrequestjson
    foirequest["id"] = str(jsondata["id"])
    foirequest["requeststatusid"] = 1
    foiresponse = client.post('/api/foirequests',data=json.dumps(foirequest), headers=factory_user_auth_header(app, client), content_type='application/json')
    foijsondata = json.loads(foiresponse.data)    
    wfinstanceid={"wfinstanceid":str(uuid.uuid4())}
    wfupdateresponse = client.put('/api/foirawrequestbpm/addwfinstanceid/'+str(jsondata["id"]),data=json.dumps(wfinstanceid), headers=factory_user_auth_header(app, client), content_type='application/json')
    foiupdaterequest = generalupdaterequestjson
    foiupdaterequest["id"] = str(foijsondata["id"])
    foiupdaterequest["idNumber"] = str(foijsondata["ministryRequests"][0]["filenumber"])
    foiupdaterequest["requeststatusid"] = 3
    foiassignresponse = client.post('/api/foirequests/'+str(foijsondata["id"])+'/ministryrequest/'+str(foijsondata["ministryRequests"][0]["id"]),data=json.dumps(foiupdaterequest), headers=factory_user_auth_header(app, client), content_type='application/json')
    assert foiresponse.status_code == 200 and getrawresponse.status_code == 200 and wfupdateresponse.status_code == 200 and foiassignresponse.status_code == 200


with open('tests/samplerequestjson/rawrequest.json') as x, open('tests/samplerequestjson/foirequest-general.json') as y, open('tests/samplerequestjson/foirequest-general-update.json') as z:
  generalrequestjson = json.load(y)
  generalupdaterequestjson = json.load(z)
  rawrequestjson = json.load(x)
def test_post_foirequest_general_cfr(app, client):
    rawresponse = client.post('/api/foirawrequests',data=json.dumps(rawrequestjson), headers=factory_user_auth_header(app, client), content_type='application/json')
    jsondata = json.loads(rawresponse.data)    
    getrawresponse = client.get('/api/foirawrequest/'+str(jsondata["id"]), headers=factory_user_auth_header(app, client), content_type='application/json') 
    foirequest = generalrequestjson
    foirequest["id"] = str(jsondata["id"])
    foirequest["requeststatusid"] = 1
    foiresponse = client.post('/api/foirequests',data=json.dumps(foirequest), headers=factory_user_auth_header(app, client), content_type='application/json')
    foijsondata = json.loads(foiresponse.data)    
    wfinstanceid={"wfinstanceid":str(uuid.uuid4())}
    wfupdateresponse = client.put('/api/foirawrequestbpm/addwfinstanceid/'+str(jsondata["id"]),data=json.dumps(wfinstanceid), headers=factory_user_auth_header(app, client), content_type='application/json')
    foiupdaterequest = generalupdaterequestjson
    foiupdaterequest["id"] = str(foijsondata["id"])
    foiupdaterequest["idNumber"] = str(foijsondata["ministryRequests"][0]["filenumber"])
    foiupdaterequest["requeststatusid"] = 2
    foiassignresponse = client.post('/api/foirequests/'+str(foijsondata["id"])+'/ministryrequest/'+str(foijsondata["ministryRequests"][0]["id"]),data=json.dumps(foiupdaterequest), headers=factory_user_auth_header(app, client), content_type='application/json')
    print('/api/foirequests/'+str(foijsondata["id"])+'/ministryrequest/'+str(foijsondata["ministryRequests"][0]["id"])+'/ministry')
    foiministryreqResponse = client.get('/api/foirequests/'+str(foijsondata["id"])+'/ministryrequest/'+str(foijsondata["ministryRequests"][0]["id"])+'/ministry',headers=factory_ministryuser_auth_header(app, client), content_type='application/json')
    assert foiministryreqResponse.status_code == 200 and foiresponse.status_code == 200 and getrawresponse.status_code == 200 and wfupdateresponse.status_code == 200 and foiassignresponse.status_code == 200

with open('tests/samplerequestjson/rawrequest.json') as x, open('tests/samplerequestjson/foirequest-general.json') as y, open('tests/samplerequestjson/foirequest-general-update.json') as z:
  generalrequestjson = json.load(y)
  generalupdaterequestjson = json.load(z)
  rawrequestjson = json.load(x)
def test_post_foirequest_general_cfrtoopen(app, client):
    rawresponse = client.post('/api/foirawrequests',data=json.dumps(rawrequestjson), headers=factory_user_auth_header(app, client), content_type='application/json')
    jsondata = json.loads(rawresponse.data)    
    getrawresponse = client.get('/api/foirawrequest/'+str(jsondata["id"]), headers=factory_user_auth_header(app, client), content_type='application/json') 
    foirequest = generalrequestjson
    foirequest["id"] = str(jsondata["id"])
    foirequest["requeststatusid"] = 1
    foiresponse = client.post('/api/foirequests',data=json.dumps(foirequest), headers=factory_user_auth_header(app, client), content_type='application/json')
    foijsondata = json.loads(foiresponse.data)    
    wfinstanceid={"wfinstanceid":str(uuid.uuid4())}
    wfupdateresponse = client.put('/api/foirawrequestbpm/addwfinstanceid/'+str(jsondata["id"]),data=json.dumps(wfinstanceid), headers=factory_user_auth_header(app, client), content_type='application/json')
    foiupdaterequest = generalupdaterequestjson
    foiupdaterequest["id"] = str(foijsondata["id"])
    foiupdaterequest["idNumber"] = str(foijsondata["ministryRequests"][0]["filenumber"])
    foiupdaterequest["requeststatusid"] = 2
    foiassignresponse = client.post('/api/foirequests/'+str(foijsondata["id"])+'/ministryrequest/'+str(foijsondata["ministryRequests"][0]["id"]),data=json.dumps(foiupdaterequest), headers=factory_user_auth_header(app, client), content_type='application/json')
    foiupdaterequest["requeststatusid"] = 1
    foireqresponse = client.post('/api/foirequests/'+str(foijsondata["id"])+'/ministryrequest/'+str(foijsondata["ministryRequests"][0]["id"]),data=json.dumps(foiupdaterequest), headers=factory_user_auth_header(app, client), content_type='application/json')  
    assert foiresponse.status_code == 200 and getrawresponse.status_code == 200 and wfupdateresponse.status_code == 200 and foiassignresponse.status_code == 200 and foireqresponse.status_code == 200

with open('tests/samplerequestjson/rawrequest.json') as x, open('tests/samplerequestjson/foirequest-general.json') as y, open('tests/samplerequestjson/foirequest-general-update.json') as z:
  generalrequestjson = json.load(y)
  generalupdaterequestjson = json.load(z)
  rawrequestjson = json.load(x)
def test_post_foirequest_general_cfrtoreview(app, client):
    rawresponse = client.post('/api/foirawrequests',data=json.dumps(rawrequestjson), headers=factory_user_auth_header(app, client), content_type='application/json')
    jsondata = json.loads(rawresponse.data)    
    getrawresponse = client.get('/api/foirawrequest/'+str(jsondata["id"]), headers=factory_user_auth_header(app, client), content_type='application/json') 
    foirequest = generalrequestjson
    foirequest["id"] = str(jsondata["id"])
    foirequest["requeststatusid"] = 1
    foiresponse = client.post('/api/foirequests',data=json.dumps(foirequest), headers=factory_user_auth_header(app, client), content_type='application/json')
    foijsondata = json.loads(foiresponse.data)    
    wfinstanceid={"wfinstanceid":str(uuid.uuid4())}
    wfupdateresponse = client.put('/api/foirawrequestbpm/addwfinstanceid/'+str(jsondata["id"]),data=json.dumps(wfinstanceid), headers=factory_user_auth_header(app, client), content_type='application/json')
    foiupdaterequest = generalupdaterequestjson
    foiupdaterequest["id"] = str(foijsondata["id"])
    foiupdaterequest["idNumber"] = str(foijsondata["ministryRequests"][0]["filenumber"])
    foiupdaterequest["requeststatusid"] = 2
    foiassignresponse = client.post('/api/foirequests/'+str(foijsondata["id"])+'/ministryrequest/'+str(foijsondata["ministryRequests"][0]["id"]),data=json.dumps(foiupdaterequest), headers=factory_user_auth_header(app, client), content_type='application/json')
    foiupdaterequest["requeststatusid"] = 7
    foireqresponse = client.post('/api/foirequests/'+str(foijsondata["id"])+'/ministryrequest/'+str(foijsondata["ministryRequests"][0]["id"]),data=json.dumps(foiupdaterequest), headers=factory_user_auth_header(app, client), content_type='application/json')  
    assert foiresponse.status_code == 200 and getrawresponse.status_code == 200 and wfupdateresponse.status_code == 200 and foiassignresponse.status_code == 200 and foireqresponse.status_code == 200

with open('tests/samplerequestjson/rawrequest.json') as x, open('tests/samplerequestjson/foirequest-general.json') as y, open('tests/samplerequestjson/foirequest-general-update.json') as z:
  generalrequestjson = json.load(y)
  generalupdaterequestjson = json.load(z)
  rawrequestjson = json.load(x)
def test_post_foirequest_general_reviewtoconsult(app, client):
    rawresponse = client.post('/api/foirawrequests',data=json.dumps(rawrequestjson), headers=factory_user_auth_header(app, client), content_type='application/json')
    jsondata = json.loads(rawresponse.data)    
    getrawresponse = client.get('/api/foirawrequest/'+str(jsondata["id"]), headers=factory_user_auth_header(app, client), content_type='application/json') 
    foirequest = generalrequestjson
    foirequest["id"] = str(jsondata["id"])
    foirequest["requeststatusid"] = 1
    foiresponse = client.post('/api/foirequests',data=json.dumps(foirequest), headers=factory_user_auth_header(app, client), content_type='application/json')
    foijsondata = json.loads(foiresponse.data)    
    wfinstanceid={"wfinstanceid":str(uuid.uuid4())}
    wfupdateresponse = client.put('/api/foirawrequestbpm/addwfinstanceid/'+str(jsondata["id"]),data=json.dumps(wfinstanceid), headers=factory_user_auth_header(app, client), content_type='application/json')
    foiupdaterequest = generalupdaterequestjson
    foiupdaterequest["id"] = str(foijsondata["id"])
    foiupdaterequest["idNumber"] = str(foijsondata["ministryRequests"][0]["filenumber"])
    foiupdaterequest["requeststatusid"] = 2
    foiassignresponse = client.post('/api/foirequests/'+str(foijsondata["id"])+'/ministryrequest/'+str(foijsondata["ministryRequests"][0]["id"]),data=json.dumps(foiupdaterequest), headers=factory_user_auth_header(app, client), content_type='application/json')
    foiupdaterequest["requeststatusid"] = 7
    foireqresponse = client.post('/api/foirequests/'+str(foijsondata["id"])+'/ministryrequest/'+str(foijsondata["ministryRequests"][0]["id"]),data=json.dumps(foiupdaterequest), headers=factory_user_auth_header(app, client), content_type='application/json')  
    foiupdaterequest["requeststatusid"] = 9
    foireqresponse2 = client.post('/api/foirequests/'+str(foijsondata["id"])+'/ministryrequest/'+str(foijsondata["ministryRequests"][0]["id"]),data=json.dumps(foiupdaterequest), headers=factory_user_auth_header(app, client), content_type='application/json')  
    assert foiresponse.status_code == 200 and getrawresponse.status_code == 200 and wfupdateresponse.status_code == 200 and foiassignresponse.status_code == 200 and foireqresponse.status_code == 200 and foireqresponse2.status_code == 200

with open('tests/samplerequestjson/rawrequest.json') as x, open('tests/samplerequestjson/foirequest-general.json') as y, open('tests/samplerequestjson/foirequest-general-update.json') as z:
  generalrequestjson = json.load(y)
  generalupdaterequestjson = json.load(z)
  rawrequestjson = json.load(x)
def test_post_foirequest_general_reviewtominsignoff(app, client):
    rawresponse = client.post('/api/foirawrequests',data=json.dumps(rawrequestjson), headers=factory_user_auth_header(app, client), content_type='application/json')
    jsondata = json.loads(rawresponse.data)    
    getrawresponse = client.get('/api/foirawrequest/'+str(jsondata["id"]), headers=factory_user_auth_header(app, client), content_type='application/json') 
    foirequest = generalrequestjson
    foirequest["id"] = str(jsondata["id"])
    foirequest["requeststatusid"] = 1
    foiresponse = client.post('/api/foirequests',data=json.dumps(foirequest), headers=factory_user_auth_header(app, client), content_type='application/json')
    foijsondata = json.loads(foiresponse.data)    
    wfinstanceid={"wfinstanceid":str(uuid.uuid4())}
    wfupdateresponse = client.put('/api/foirawrequestbpm/addwfinstanceid/'+str(jsondata["id"]),data=json.dumps(wfinstanceid), headers=factory_user_auth_header(app, client), content_type='application/json')
    foiupdaterequest = generalupdaterequestjson
    foiupdaterequest["id"] = str(foijsondata["id"])
    foiupdaterequest["idNumber"] = str(foijsondata["ministryRequests"][0]["filenumber"])
    foiupdaterequest["requeststatusid"] = 2
    foiassignresponse = client.post('/api/foirequests/'+str(foijsondata["id"])+'/ministryrequest/'+str(foijsondata["ministryRequests"][0]["id"]),data=json.dumps(foiupdaterequest), headers=factory_user_auth_header(app, client), content_type='application/json')
    foiupdaterequest["requeststatusid"] = 7
    foireqresponse = client.post('/api/foirequests/'+str(foijsondata["id"])+'/ministryrequest/'+str(foijsondata["ministryRequests"][0]["id"]),data=json.dumps(foiupdaterequest), headers=factory_user_auth_header(app, client), content_type='application/json')  
    foiupdaterequest["requeststatusid"] = 10
    foireqresponse2 = client.post('/api/foirequests/'+str(foijsondata["id"])+'/ministryrequest/'+str(foijsondata["ministryRequests"][0]["id"]),data=json.dumps(foiupdaterequest), headers=factory_user_auth_header(app, client), content_type='application/json')  
    assert foiresponse.status_code == 200 and getrawresponse.status_code == 200 and wfupdateresponse.status_code == 200 and foiassignresponse.status_code == 200 and foireqresponse.status_code == 200 and foireqresponse2.status_code == 200

with open('tests/samplerequestjson/rawrequest.json') as x, open('tests/samplerequestjson/foirequest-general.json') as y, open('tests/samplerequestjson/foirequest-general-update.json') as z:
  generalrequestjson = json.load(y)
  generalupdaterequestjson = json.load(z)
  rawrequestjson = json.load(x)
def test_post_foirequest_general_consulttoreview(app, client):
    rawresponse = client.post('/api/foirawrequests',data=json.dumps(rawrequestjson), headers=factory_user_auth_header(app, client), content_type='application/json')
    jsondata = json.loads(rawresponse.data)    
    getrawresponse = client.get('/api/foirawrequest/'+str(jsondata["id"]), headers=factory_user_auth_header(app, client), content_type='application/json') 
    foirequest = generalrequestjson
    foirequest["id"] = str(jsondata["id"])
    foirequest["requeststatusid"] = 1
    foiresponse = client.post('/api/foirequests',data=json.dumps(foirequest), headers=factory_user_auth_header(app, client), content_type='application/json')
    foijsondata = json.loads(foiresponse.data)    
    wfinstanceid={"wfinstanceid":str(uuid.uuid4())}
    wfupdateresponse = client.put('/api/foirawrequestbpm/addwfinstanceid/'+str(jsondata["id"]),data=json.dumps(wfinstanceid), headers=factory_user_auth_header(app, client), content_type='application/json')
    foiupdaterequest = generalupdaterequestjson
    foiupdaterequest["id"] = str(foijsondata["id"])
    foiupdaterequest["idNumber"] = str(foijsondata["ministryRequests"][0]["filenumber"])
    foiupdaterequest["requeststatusid"] = 2
    foiassignresponse = client.post('/api/foirequests/'+str(foijsondata["id"])+'/ministryrequest/'+str(foijsondata["ministryRequests"][0]["id"]),data=json.dumps(foiupdaterequest), headers=factory_user_auth_header(app, client), content_type='application/json')
    foiupdaterequest["requeststatusid"] = 7
    foireqresponse = client.post('/api/foirequests/'+str(foijsondata["id"])+'/ministryrequest/'+str(foijsondata["ministryRequests"][0]["id"]),data=json.dumps(foiupdaterequest), headers=factory_user_auth_header(app, client), content_type='application/json')  
    foiupdaterequest["requeststatusid"] = 9
    foireqresponse2 = client.post('/api/foirequests/'+str(foijsondata["id"])+'/ministryrequest/'+str(foijsondata["ministryRequests"][0]["id"]),data=json.dumps(foiupdaterequest), headers=factory_user_auth_header(app, client), content_type='application/json')  
    foiupdaterequest["requeststatusid"] = 7
    foireqresponse3 = client.post('/api/foirequests/'+str(foijsondata["id"])+'/ministryrequest/'+str(foijsondata["ministryRequests"][0]["id"]),data=json.dumps(foiupdaterequest), headers=factory_user_auth_header(app, client), content_type='application/json')    
    assert foiresponse.status_code == 200 and getrawresponse.status_code == 200 and wfupdateresponse.status_code == 200 and foiassignresponse.status_code == 200 and foireqresponse.status_code == 200 and foireqresponse2.status_code == 200 and foireqresponse3.status_code == 200

with open('tests/samplerequestjson/rawrequest.json') as x, open('tests/samplerequestjson/foirequest-general.json') as y, open('tests/samplerequestjson/foirequest-general-update.json') as z:
  generalrequestjson = json.load(y)
  generalupdaterequestjson = json.load(z)
  rawrequestjson = json.load(x)
def test_post_foirequest_general_cfr_assignment(app, client):
    rawresponse = client.post('/api/foirawrequests',data=json.dumps(rawrequestjson), headers=factory_user_auth_header(app, client), content_type='application/json')
    jsondata = json.loads(rawresponse.data)    
    getrawresponse = client.get('/api/foirawrequest/'+str(jsondata["id"]), headers=factory_user_auth_header(app, client), content_type='application/json') 
    foirequest = generalrequestjson
    foirequest["id"] = str(jsondata["id"])
    foirequest["requeststatusid"] = 1
    foiresponse = client.post('/api/foirequests',data=json.dumps(foirequest), headers=factory_user_auth_header(app, client), content_type='application/json')
    foijsondata = json.loads(foiresponse.data)    
    wfinstanceid={"wfinstanceid":str(uuid.uuid4())}
    wfupdateresponse = client.put('/api/foirawrequestbpm/addwfinstanceid/'+str(jsondata["id"]),data=json.dumps(wfinstanceid), headers=factory_user_auth_header(app, client), content_type='application/json')
    foiupdaterequest = generalupdaterequestjson
    foiupdaterequest["id"] = str(foijsondata["id"])
    foiupdaterequest["idNumber"] = str(foijsondata["ministryRequests"][0]["filenumber"])
    foiupdaterequest["requeststatusid"] = 2
    foiassignresponse = client.post('/api/foirequests/'+str(foijsondata["id"])+'/ministryrequest/'+str(foijsondata["ministryRequests"][0]["id"]),data=json.dumps(foiupdaterequest), headers=factory_user_auth_header(app, client), content_type='application/json')
    foiministryreqResponse = client.get('/api/foirequests/'+str(foijsondata["id"])+'/ministryrequest/'+str(foijsondata["ministryRequests"][0]["id"])+'/ministry',headers=factory_ministryuser_auth_header(app, client), content_type='application/json')
    foiassignrequest = {
    "assignedGroup":"Intake Team",
    "assignedTo":"foiintake@idir",
    "assignedToFirstName":"FOI",
    "assignedToLastName":"Intake",
    "assignedministrygroup":"EDU Ministry Team",
    "assignedministryperson":"foiedu@idir",
    "assignedministrypersonFirstName":"foiedu",
    "assignedministrypersonLastName":"foiedu"
    }
    foicfrassignresponse = client.post('/api/foirequests/'+str(foijsondata["id"])+'/ministryrequest/'+str(foijsondata["ministryRequests"][0]["id"])+'/ministry',data=json.dumps(foiassignrequest), headers=factory_user_auth_header(app, client), content_type='application/json')
    assert foiministryreqResponse.status_code == 200 and foiresponse.status_code == 200 and getrawresponse.status_code == 200 and wfupdateresponse.status_code == 200 and foiassignresponse.status_code == 200 and foiministryreqResponse.status_code == 200 and foicfrassignresponse.status_code == 200

with open('tests/samplerequestjson/rawrequest.json') as x, open('tests/samplerequestjson/foirequest-general.json') as y, open('tests/samplerequestjson/foirequest-general-update.json') as z:
  generalrequestjson = json.load(y)
  generalupdaterequestjson = json.load(z)
  rawrequestjson = json.load(x)
def test_post_foirequest_general_cfr_division(app, client):
    rawresponse = client.post('/api/foirawrequests',data=json.dumps(rawrequestjson), headers=factory_user_auth_header(app, client), content_type='application/json')
    jsondata = json.loads(rawresponse.data)    
    getrawresponse = client.get('/api/foirawrequest/'+str(jsondata["id"]), headers=factory_user_auth_header(app, client), content_type='application/json') 
    foirequest = generalrequestjson
    foirequest["id"] = str(jsondata["id"])
    foirequest["requeststatusid"] = 1
    foiresponse = client.post('/api/foirequests',data=json.dumps(foirequest), headers=factory_user_auth_header(app, client), content_type='application/json')
    foijsondata = json.loads(foiresponse.data)    
    wfinstanceid={"wfinstanceid":str(uuid.uuid4())}
    wfupdateresponse = client.put('/api/foirawrequestbpm/addwfinstanceid/'+str(jsondata["id"]),data=json.dumps(wfinstanceid), headers=factory_user_auth_header(app, client), content_type='application/json')
    foiupdaterequest = generalupdaterequestjson
    foiupdaterequest["id"] = str(foijsondata["id"])
    foiupdaterequest["idNumber"] = str(foijsondata["ministryRequests"][0]["filenumber"])
    foiupdaterequest["requeststatusid"] = 2
    foiassignresponse = client.post('/api/foirequests/'+str(foijsondata["id"])+'/ministryrequest/'+str(foijsondata["ministryRequests"][0]["id"]),data=json.dumps(foiupdaterequest), headers=factory_user_auth_header(app, client), content_type='application/json')
    foiministryreqResponse = client.get('/api/foirequests/'+str(foijsondata["id"])+'/ministryrequest/'+str(foijsondata["ministryRequests"][0]["id"])+'/ministry',headers=factory_ministryuser_auth_header(app, client), content_type='application/json')
    foidivisionrequest = {
    "assignedministrygroup":"EDU Ministry Team",
    "assignedministryperson":"foiedu@idir",
    "assignedministrypersonFirstName":"foiedu",
    "assignedministrypersonLastName":"foiedu",
    "requeststatusid": 2,
     "divisions": [{"divisionid":1,"stageid":1},{"divisionid":2,"stageid":1}]
    }
    foicfrdivisionresponse = client.post('/api/foirequests/'+str(foijsondata["id"])+'/ministryrequest/'+str(foijsondata["ministryRequests"][0]["id"])+'/ministry',data=json.dumps(foidivisionrequest), headers=factory_user_auth_header(app, client), content_type='application/json')
    assert foiministryreqResponse.status_code == 200 and foiresponse.status_code == 200 and getrawresponse.status_code == 200 and wfupdateresponse.status_code == 200 and foiassignresponse.status_code == 200 and foiministryreqResponse.status_code == 200 and foicfrdivisionresponse.status_code == 200

with open('tests/samplerequestjson/rawrequest.json') as x, open('tests/samplerequestjson/foirequest-general.json') as y, open('tests/samplerequestjson/foirequest-general-update.json') as z:
  generalrequestjson = json.load(y)
  generalupdaterequestjson = json.load(z)
  rawrequestjson = json.load(x)
def test_post_foirequest_general_cfr_document(app, client):
    rawresponse = client.post('/api/foirawrequests',data=json.dumps(rawrequestjson), headers=factory_user_auth_header(app, client), content_type='application/json')
    jsondata = json.loads(rawresponse.data)    
    getrawresponse = client.get('/api/foirawrequest/'+str(jsondata["id"]), headers=factory_user_auth_header(app, client), content_type='application/json') 
    foirequest = generalrequestjson
    foirequest["id"] = str(jsondata["id"])
    foirequest["requeststatusid"] = 1
    foiresponse = client.post('/api/foirequests',data=json.dumps(foirequest), headers=factory_user_auth_header(app, client), content_type='application/json')
    foijsondata = json.loads(foiresponse.data)    
    wfinstanceid={"wfinstanceid":str(uuid.uuid4())}
    wfupdateresponse = client.put('/api/foirawrequestbpm/addwfinstanceid/'+str(jsondata["id"]),data=json.dumps(wfinstanceid), headers=factory_user_auth_header(app, client), content_type='application/json')
    foiupdaterequest = generalupdaterequestjson
    foiupdaterequest["id"] = str(foijsondata["id"])
    foiupdaterequest["idNumber"] = str(foijsondata["ministryRequests"][0]["filenumber"])
    foiupdaterequest["requeststatusid"] = 2
    foiassignresponse = client.post('/api/foirequests/'+str(foijsondata["id"])+'/ministryrequest/'+str(foijsondata["ministryRequests"][0]["id"]),data=json.dumps(foiupdaterequest), headers=factory_user_auth_header(app, client), content_type='application/json')
    foiministryreqResponse = client.get('/api/foirequests/'+str(foijsondata["id"])+'/ministryrequest/'+str(foijsondata["ministryRequests"][0]["id"])+'/ministry',headers=factory_ministryuser_auth_header(app, client), content_type='application/json')
    foidivisionrequest = {
    "assignedministrygroup":"EDU Ministry Team",
    "assignedministryperson":"foiedu@idir",
    "assignedministrypersonFirstName":"foiedu",
    "assignedministrypersonLastName":"foiedu",
    "requeststatusid": 2,
    "documents":  [
        {
            "category": "cfr-feeassessed",
            "documentpath":"/EDU/"+str(foijsondata["ministryRequests"][0]["filenumber"])+"/cfr-review/test.docx",
            "filename":"test.docx"
        }
        ]
    }
    foicfrdivisionresponse = client.post('/api/foirequests/'+str(foijsondata["id"])+'/ministryrequest/'+str(foijsondata["ministryRequests"][0]["id"])+'/ministry',data=json.dumps(foidivisionrequest), headers=factory_user_auth_header(app, client), content_type='application/json')
    assert foiministryreqResponse.status_code == 200 and foiresponse.status_code == 200 and getrawresponse.status_code == 200 and wfupdateresponse.status_code == 200 and foiassignresponse.status_code == 200 and foiministryreqResponse.status_code == 200 and foicfrdivisionresponse.status_code == 200


with open('tests/samplerequestjson/rawrequest.json') as x, open('tests/samplerequestjson/foirequest-general.json') as y, open('tests/samplerequestjson/foirequest-general-update.json') as z:
  generalrequestjson = json.load(y)
  generalupdaterequestjson = json.load(z)
  rawrequestjson = json.load(x)
def test_post_foirequest_general_close(app, client):
    rawresponse = client.post('/api/foirawrequests',data=json.dumps(rawrequestjson), headers=factory_user_auth_header(app, client), content_type='application/json')
    jsondata = json.loads(rawresponse.data)    
    getrawresponse = client.get('/api/foirawrequest/'+str(jsondata["id"]), headers=factory_user_auth_header(app, client), content_type='application/json') 
    foirequest = generalrequestjson
    foirequest["id"] = str(jsondata["id"])
    foirequest["requeststatusid"] = 1
    foiresponse = client.post('/api/foirequests',data=json.dumps(foirequest), headers=factory_user_auth_header(app, client), content_type='application/json')
    foijsondata = json.loads(foiresponse.data)    
    wfinstanceid={"wfinstanceid":str(uuid.uuid4())}
    wfupdateresponse = client.put('/api/foirawrequestbpm/addwfinstanceid/'+str(jsondata["id"]),data=json.dumps(wfinstanceid), headers=factory_user_auth_header(app, client), content_type='application/json')
    foiupdaterequest = generalupdaterequestjson
    foiupdaterequest["id"] = str(foijsondata["id"])
    foiupdaterequest["idNumber"] = str(foijsondata["ministryRequests"][0]["filenumber"])
    foiupdaterequest["requeststatusid"] = 3
    foiupdaterequest["closedate"] = '2021-10-25'
    foiupdaterequest["closereasonid"] = 1
    foiassignresponse = client.post('/api/foirequests/'+str(foijsondata["id"])+'/ministryrequest/'+str(foijsondata["ministryRequests"][0]["id"]),data=json.dumps(foiupdaterequest), headers=factory_user_auth_header(app, client), content_type='application/json')
    assert foiresponse.status_code == 200 and getrawresponse.status_code == 200 and wfupdateresponse.status_code == 200 and foiassignresponse.status_code == 200 

def test_get_foirequestqueue(app, client):
  response = client.get('/api/dashboardpagination?page=1&size=10&sortingitems[]=intakeSorting&sortingitems[]=duedate&sortingorders[]=asc&sortingorders[]=asc&filters[]=firstName&filters[]=lastName&filters[]=requestType&filters[]=idNumber&filters[]=axisRequestId&filters[]=currentState&filters[]=assignedToLastName&filters[]=assignedToFirstName&additionalfilter=myRequests&userid=foiintake@idir', headers=factory_user_auth_header(app, client), content_type='application/json')
  jsondata = json.loads(response.data)  
  assert response.status_code == 200  and len(jsondata) > 0 

def test_get_foiministryrequestqueue(app, client):
  response = client.get('/api/dashboardpagination/ministry?page=1&size=10&sortingitems[]=ministrySorting&sortingitems[]=cfrduedate&sortingorders[]=asc&sortingorders[]=asc&filters[]=applicantcategory&filters[]=requestType&filters[]=idNumber&filters[]=axisRequestId&filters[]=currentState&filters[]=assignedministrypersonLastName&filters[]=assignedministrypersonFirstName&additionalfilter=myRequests&userid=foiedu@idir', headers=factory_ministryuser_auth_header(app, client), content_type='application/json')
  jsondata = json.loads(response.data)
  assert response.status_code == 200  and len(jsondata) > 0   


def test_get_foirequestqueuewithoutheader(app, client):    
  response = client.get('/api/dashboardpagination?page=1&size=10&sortingitems[]=intakeSorting&sortingitems[]=duedate&sortingorders[]=asc&sortingorders[]=asc&filters[]=firstName&filters[]=lastName&filters[]=requestType&filters[]=idNumber&filters[]=axisRequestId&filters[]=currentState&filters[]=assignedToLastName&filters[]=assignedToFirstName&additionalfilter=myRequests&userid=foiintake@idir', content_type='application/json')    
  jsondata = json.loads(response.data)
  assert response.status_code == 500
