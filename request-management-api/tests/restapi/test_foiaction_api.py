import json
import os
import uuid
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


def test_get_foiactionforgeneralcase1(app, client):
    response = client.get('/api/foiaction/general/unopened', headers=factory_auth_header(app, client), content_type='application/json')
    jsondata = json.loads(response.data)    
    assert response.status_code == 200 and len(jsondata) >=1

def test_get_foiactionforgeneralcase2(app, client):
    response = client.get('/api/foiaction/general/intakeinprogress', headers=factory_auth_header(app, client), content_type='application/json')
    jsondata = json.loads(response.data)    
    assert response.status_code == 200 and len(jsondata) >=1
    
def test_get_foiactionforgeneralinvalid(app, client):
    response = client.get('/api/foiaction/invalid/invalid', headers=factory_auth_header(app, client), content_type='application/json')
    jsondata = json.loads(response.data)    
    assert response.status_code == 400 and len(jsondata) >=1
