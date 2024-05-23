import json
import os
import uuid
import requests
import ast

TEST_INTAKEUSER_PAYLOAD = {
    'client_id': 'forms-flow-web',
    'grant_type': 'password',
    'username' : os.getenv('TEST_INTAKE_USERID'),
    'password': os.getenv('TEST_INTAKE_PASSWORD')
}

TEST_FLEXUSER_PAYLOAD = {
    'client_id': 'forms-flow-web',
    'grant_type': 'password',
    'username' : os.getenv('TEST_FLEX_USERID'),
    'password': os.getenv('TEST_FLEX_PASSWORD')
}

def factory_intake_auth_header(app, client):
    url = '{0}/auth/realms/{1}/protocol/openid-connect/token'.format(os.getenv('KEYCLOAK_ADMIN_HOST'),os.getenv('KEYCLOAK_ADMIN_REALM'))        
    x = requests.post(url, TEST_INTAKEUSER_PAYLOAD, verify=True).content.decode('utf-8')       
    return {'Authorization': 'Bearer ' + str(ast.literal_eval(x)['access_token'])}  

def factory_flex_auth_header(app, client):
    url = '{0}/auth/realms/{1}/protocol/openid-connect/token'.format(os.getenv('KEYCLOAK_ADMIN_HOST'),os.getenv('KEYCLOAK_ADMIN_REALM'))        
    x = requests.post(url, TEST_FLEXUSER_PAYLOAD, verify=True).content.decode('utf-8')       
    return {'Authorization': 'Bearer ' + str(ast.literal_eval(x)['access_token'])} 

def test_ping(app, client):
    response = client.get('/api/healthz')
    assert response.status_code == 200

with open('tests/samplerequestjson/rawrequest.json') as f:
  requestjson = json.load(f)
def test_get_foiauditfordesccase1(app, client):
    response = client.post('/api/foirawrequests',data=json.dumps(requestjson), content_type='application/json')
    jsondata = json.loads(response.data)
    response = client.get('/api/foiaudit/rawrequest/'+str(jsondata["id"])+'/description', headers=factory_intake_auth_header(app, client), content_type='application/json')
    jsondata = json.loads(response.data)    
    assert response.status_code == 200 and len(jsondata['audit']) >=1

with open('tests/samplerequestjson/rawrequest.json') as x, open('tests/samplerequestjson/foirequest-general.json') as y, open('tests/samplerequestjson/foirequest-general-update.json') as z:
  generalrequestjson = json.load(y)
  generalupdaterequestjson = json.load(z)
  rawrequestjson = json.load(x)
def test_get_foiauditfordesccase2(app, client):
    rawresponse = client.post('/api/foirawrequests',data=json.dumps(rawrequestjson), headers=factory_intake_auth_header(app, client), content_type='application/json')
    jsondata = json.loads(rawresponse.data)    
    foirequest = generalrequestjson
    foirequest["id"] = str(jsondata["id"])
    foirequest['requeststatusid'] = 1    
    foiresponse = client.post('/api/foirequests',data=json.dumps(foirequest), headers=factory_intake_auth_header(app, client), content_type='application/json')
    foijsondata = json.loads(foiresponse.data)      
    foiupdaterequest = generalupdaterequestjson
    foiupdaterequest["id"] = str(foijsondata["id"])
    foiupdaterequest["idNumber"] = str(foijsondata["ministryRequests"][0]["filenumber"])   
    response = client.get('/api/foiaudit/ministryrequest/'+str(foijsondata["ministryRequests"][0]["id"])+'/description', headers=factory_flex_auth_header(app, client), content_type='application/json')
    jsondata = json.loads(response.data)    
    assert response.status_code == 200 and len(jsondata['audit']) >=1
    
def test_get_foiauditfordescinvalid(app, client):
    response = client.get('/api/foiaudit/invalid/1/invalid', headers=factory_intake_auth_header(app, client), content_type='application/json')
    jsondata = json.loads(response.data)    
    assert response.status_code == 400 and len(jsondata) >=1
