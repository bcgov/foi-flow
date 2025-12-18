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

def test_get_foiassigneesforgeneralopen(app, client):
    response = client.get('/api/foiassignees/general/open', headers=factory_auth_header(app, client), content_type='application/json')
    jsondata = json.loads(response.data)    
    assert response.status_code == 200 and len(jsondata) >=1
    
def test_get_foiassigneesforgeneralcfr(app, client):
    response = client.get('/api/foiassignees/general/callforrecords/edu', headers=factory_auth_header(app, client), content_type='application/json')
    jsondata = json.loads(response.data)    
    assert response.status_code == 200 and len(jsondata) >=1

def test_get_foiassigneesforpersonalopen(app, client):
    response = client.get('/api/foiassignees/personal/open', headers=factory_auth_header(app, client), content_type='application/json')
    jsondata = json.loads(response.data)    
    assert response.status_code == 200 and len(jsondata) >=1
    
def test_get_foiassigneesforpersonalinvalidstatus(app, client):
    response = client.get('/api/foiassignees/test', headers=factory_auth_header(app, client), content_type='application/json')
    assert response.status_code == 404

def test_get_foiassigneesforgroup(app, client):
    response = client.get('/api/foiassignees/group/intaketeam', headers=factory_auth_header(app, client), content_type='application/json')  #invalid condition    
    jsondata = json.loads(response.data)    
    assert response.status_code == 200 and len(jsondata) >=1
    
def test_get_foiassigneesgeneralteams(app, client):
    response = client.get('/api/foiassignees/processingteams/general', headers=factory_auth_header(app, client), content_type='application/json')  #invalid condition    
    jsondata = json.loads(response.data)    
    assert response.status_code == 200 and len(jsondata) >=1
    
def test_get_foiassigneespersonalteams(app, client):
    response = client.get('/api/foiassignees/processingteams/personal', headers=factory_auth_header(app, client), content_type='application/json')  #invalid condition    
    jsondata = json.loads(response.data)    
    assert response.status_code == 200 and len(jsondata) >=1