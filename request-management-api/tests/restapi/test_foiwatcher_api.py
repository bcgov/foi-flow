import json
import uuid
import os
import requests
import ast

TEST_USER_PAYLOAD = {
    'client_id': 'forms-flow-web',
    'grant_type': 'password',
    'username' : os.getenv('TEST_INTAKE_USERID'),
    'password': os.getenv('TEST_INTAKE_PASSWORD')
}

TEST_MINISTRY_USER_PAYLOAD = {
    'client_id': 'forms-flow-web',
    'grant_type': 'password',
    'username' : os.getenv('TEST_MINISTRY_USERID'),
    'password': os.getenv('TEST_MINISTRY_PASSWORD')
}


def factory_auth_header(app, client):
    url = '{0}/auth/realms/{1}/protocol/openid-connect/token'.format(os.getenv('KEYCLOAK_ADMIN_HOST'),os.getenv('KEYCLOAK_ADMIN_REALM'))        
    x = requests.post(url, TEST_USER_PAYLOAD, verify=True).content.decode('utf-8')       
    return {'Authorization': 'Bearer ' + str(ast.literal_eval(x)['access_token'])}  

def factory_ministry_auth_header(app, client):
    url = '{0}/auth/realms/{1}/protocol/openid-connect/token'.format(os.getenv('KEYCLOAK_ADMIN_HOST'),os.getenv('KEYCLOAK_ADMIN_REALM'))        
    x = requests.post(url, TEST_MINISTRY_USER_PAYLOAD, verify=True).content.decode('utf-8')       
    return {'Authorization': 'Bearer ' + str(ast.literal_eval(x)['access_token'])}  


def test_ping(app, client):
    response = client.get('/api/healthz')
    assert response.status_code == 200

with open('tests/samplerequestjson/rawrequest.json') as x:
  rawrequestjson = json.load(x)
def test_foirawwatcher(app, client):
    rawresponse = client.post('/api/foirawrequests',data=json.dumps(rawrequestjson), headers=factory_auth_header(app, client), content_type='application/json')
    jsondata = json.loads(rawresponse.data)   
    watcherjson = {
    "requestid":str(jsondata["id"]),
    "watchedbygroup": "Intake Team",
    "watchedby": "sumathi",
    "isactive": True
    }
    createwatcherresponse = client.post('/api/foiwatcher/rawrequest', data=json.dumps(watcherjson), headers=factory_auth_header(app, client), content_type='application/json')
    getwatcherresponse = client.get('/api/foiwatcher/rawrequest/'+str(jsondata["id"]), headers=factory_auth_header(app, client), content_type='application/json')
    disablewatcherresponse = client.put('/api/foiwatcher/rawrequest/disable/'+str(jsondata["id"]), headers=factory_auth_header(app, client), content_type='application/json')
    assert rawresponse.status_code == 200 and createwatcherresponse.status_code == 200 and getwatcherresponse.status_code == 200 and disablewatcherresponse.status_code == 200


with open('tests/samplerequestjson/rawrequest.json') as x, open('tests/samplerequestjson/foirequest-general.json') as y:
  generalrequestjson = json.load(y)
  rawrequestjson = json.load(x)
def test_foiministrywatcher(app, client):
    rawresponse = client.post('/api/foirawrequests',data=json.dumps(rawrequestjson), headers=factory_auth_header(app, client), content_type='application/json')
    jsondata = json.loads(rawresponse.data)    
    foirequest = generalrequestjson
    foirequest["id"] = str(jsondata["id"])
    foirequest["requeststatusid"] = 1
    foiresponse = client.post('/api/foirequests',data=json.dumps(foirequest), headers=factory_auth_header(app, client), content_type='application/json')
    foijsondata = json.loads(foiresponse.data)    
    watcherjson = {
    "ministryrequestid":str(foijsondata["id"]),
    "watchedbygroup": "Intake Team",
    "watchedby": "sumathi",
    "isactive": True
    }
    createwatcherresponse = client.post('/api/foiwatcher/ministryrequest', data=json.dumps(watcherjson), headers=factory_ministry_auth_header(app, client), content_type='application/json')
    getwatcherresponse = client.get('/api/foiwatcher/ministryrequest/'+str(foijsondata["id"]), headers=factory_ministry_auth_header(app, client), content_type='application/json')
    disablewatcherresponse = client.put('/api/foiwatcher/ministryrequest/disable/'+str(jsondata["id"]), headers=factory_ministry_auth_header(app, client), content_type='application/json')
    assert rawresponse.status_code == 200 and foiresponse.status_code == 200 and createwatcherresponse.status_code == 200 and getwatcherresponse.status_code == 200 and disablewatcherresponse.status_code == 200

    

    
