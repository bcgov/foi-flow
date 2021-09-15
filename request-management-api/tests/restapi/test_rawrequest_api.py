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

with open('tests/samplerequestjson/rawrequest.json') as f:
  requestjson = json.load(f)
def test_post_foirawrequestspii(app, client):    
    response = client.post('/api/foirawrequests',data=json.dumps(requestjson), content_type='application/json')
    jsondata = json.loads(response.data)
    print(str(jsondata["id"]))
    updatejson = jsondata
    updatejson['ispiiredacted'] = True
    updatejson['assignedTo'] = "Intake Team"
    wfupdateresponse = client.post('/api/foirawrequest/'+str(jsondata["id"]),data=json.dumps(updatejson), headers=factory_auth_header(app, client), content_type='application/json')
    assert response.status_code == 200 and wfupdateresponse.status_code == 200  and len(jsondata) >=1

def test_get_programareas(app,client):    
    response = client.get('api/foiflow/programareas', headers=factory_auth_header(app, client), content_type='application/json')    
    jsondata = json.loads(response.data)    
    assert response.status_code == 200  and len(jsondata) >=1

def test_get_applicantcategories(app,client):    
    response = client.get('api/foiflow/applicantcategories', headers=factory_auth_header(app, client), content_type='application/json')    
    jsondata = json.loads(response.data)     
    assert response.status_code == 200 and len(jsondata) >=1





