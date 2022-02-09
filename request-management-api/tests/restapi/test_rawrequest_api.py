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

def factory_auth_header(app, client):
    url = '{0}/auth/realms/{1}/protocol/openid-connect/token'.format(os.getenv('KEYCLOAK_ADMIN_HOST'),os.getenv('KEYCLOAK_ADMIN_REALM'))        
    x = requests.post(url, TEST_USER_PAYLOAD, verify=True).content.decode('utf-8')       
    return {'Authorization': 'Bearer ' + str(ast.literal_eval(x)['access_token'])} 

def test_ping(app, client):
    response = client.get('/api/healthz')
    assert response.status_code == 200

with open('tests/samplerequestjson/rawrequest.json') as f:
  requestjson = json.load(f)
def test_post_foirawrequests(app, client):    
    response = client.post('/api/foirawrequests',data=json.dumps(requestjson), content_type='application/json')
    jsondata = json.loads(response.data)
    print(str(jsondata["id"]))
    wfinstanceid={"wfinstanceid":str(uuid.uuid4())}
    wfupdateresponse = client.put('/api/foirawrequestbpm/addwfinstanceid/'+str(jsondata["id"]),data=json.dumps(wfinstanceid), headers=factory_auth_header(app, client), content_type='application/json')
    assert response.status_code == 200 and wfupdateresponse.status_code == 200  and len(jsondata) >=1

with open('tests/samplerequestjson/rawrequest.json') as x, open('tests/samplerequestjson/foirequest-general.json') as y, open('tests/samplerequestjson/foirequest-general-update.json') as z:
  generalrequestjson = json.load(y)
  generalupdaterequestjson = json.load(z)
  rawrequestjson = json.load(x)
def test_post_foirawrequestspii(app, client):    
    response = client.post('/api/foirawrequests',data=json.dumps(rawrequestjson), content_type='application/json')
    jsondata = json.loads(response.data)    
    updatejson = generalupdaterequestjson
    updatejson["id"] = str(jsondata["id"])
    print(str(jsondata["id"]))    
    updatejson['ispiiredacted'] = True
    updatejson['assignedTo'] = "Intake Team"
    wfupdateresponse = client.post('/api/foirawrequest/'+str(jsondata["id"]),data=json.dumps(updatejson), headers=factory_auth_header(app, client), content_type='application/json')
    assert response.status_code == 200 and wfupdateresponse.status_code == 200  and len(jsondata) >=1
    
with open('tests/samplerequestjson/rawrequest.json') as x, open('tests/samplerequestjson/foirequest-general.json') as y, open('tests/samplerequestjson/foirequest-general-update.json') as z:
  generalrequestjson = json.load(y)
  generalupdaterequestjson = json.load(z)
  rawrequestjson = json.load(x)
def test_post_foirawrequestscancel(app, client):    
    response = client.post('/api/foirawrequests',data=json.dumps(rawrequestjson), content_type='application/json')
    jsondata = json.loads(response.data)
    updatejson = generalupdaterequestjson
    updatejson["id"] = str(jsondata["id"])
    print(str(jsondata["id"]))    
    updatejson['ispiiredacted'] = True
    updatejson['requeststatusid'] = 3
    updatejson['closedate'] = '2021-10-26'
    updatejson['requeststatusid'] = 2
    wfupdateresponse = client.post('/api/foirawrequest/'+str(jsondata["id"]),data=json.dumps(updatejson), headers=factory_auth_header(app, client), content_type='application/json')
    assert response.status_code == 200 and wfupdateresponse.status_code == 200  and len(jsondata) >=1 
    
with open('tests/samplerequestjson/rawrequest.json') as x, open('tests/samplerequestjson/foirequest-general.json') as y, open('tests/samplerequestjson/foirequest-general-update.json') as z:
  generalrequestjson = json.load(y)
  generalupdaterequestjson = json.load(z)
  rawrequestjson = json.load(x)
def test_post_foirawrequestsredirect(app, client):    
    response = client.post('/api/foirawrequests',data=json.dumps(requestjson), content_type='application/json')
    jsondata = json.loads(response.data)
    print(str(jsondata["id"]))
    updatejson = generalupdaterequestjson
    updatejson['ispiiredacted'] = True
    updatejson['assignedTo'] = "Intake Team"
    updatejson['requeststatusid'] = 4
    wfupdateresponse = client.post('/api/foirawrequest/'+str(jsondata["id"]),data=json.dumps(updatejson), headers=factory_auth_header(app, client), content_type='application/json')
    assert response.status_code == 200 and wfupdateresponse.status_code == 200  and len(jsondata) >=1
 
with open('tests/samplerequestjson/rawrequest.json') as x, open('tests/samplerequestjson/foirequest-general.json') as y, open('tests/samplerequestjson/foirequest-general-update.json') as z:
  generalrequestjson = json.load(y)
  generalupdaterequestjson = json.load(z)
  rawrequestjson = json.load(x)
def test_post_foirequest_general(app, client):
    rawresponse = client.post('/api/foirawrequests',data=json.dumps(rawrequestjson), headers=factory_auth_header(app, client), content_type='application/json')
    jsondata = json.loads(rawresponse.data)    
    getrawresponse = client.get('/api/foirawrequest/'+str(jsondata["id"]), headers=factory_auth_header(app, client), content_type='application/json') 
    foirequest = generalrequestjson
    foirequest["id"] = str(jsondata["id"])
    foirequest["requeststatusid"] = 1
    foiresponse = client.post('/api/foirequests',data=json.dumps(foirequest), headers=factory_auth_header(app, client), content_type='application/json')
    getrawresponsefields = client.get('/api/foirawrequest/'+str(jsondata["id"])+'/fields?names=ministries', headers=factory_auth_header(app, client), content_type='application/json') 
    assert rawresponse.status_code == 200 and getrawresponse.status_code == 200  and foiresponse.status_code == 200 and getrawresponsefields.status_code == 200
      

def test_get_programareas(app,client):    
    response = client.get('api/foiflow/programareas', headers=factory_auth_header(app, client), content_type='application/json')    
    jsondata = json.loads(response.data)    
    assert response.status_code == 200  and len(jsondata) >=1

def test_get_applicantcategories(app,client):    
    response = client.get('api/foiflow/applicantcategories', headers=factory_auth_header(app, client), content_type='application/json')    
    jsondata = json.loads(response.data)     
    assert response.status_code == 200 and len(jsondata) >=1





