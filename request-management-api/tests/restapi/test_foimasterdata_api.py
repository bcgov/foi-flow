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

def factory_user_auth_header(app, client):
    url = '{0}/auth/realms/{1}/protocol/openid-connect/token'.format(os.getenv('KEYCLOAK_ADMIN_HOST'),os.getenv('KEYCLOAK_ADMIN_REALM'))        
    x = requests.post(url, TEST_USER_PAYLOAD, verify=True).content.decode('utf-8')       
    return {'Authorization': 'Bearer ' + str(ast.literal_eval(x)['access_token'])} 

def test_ping(app, client):
    response = client.get('/api/healthz')
    assert response.status_code == 200

def test_get_applicantcategories(app, client):
  response = client.get('/api/foiflow/applicantcategories', headers=factory_user_auth_header(app, client), content_type='application/json')
  assert response.status_code == 200  

def test_get_programareas(app, client):
  response = client.get('/api/foiflow/programareas', headers=factory_user_auth_header(app, client), content_type='application/json')
  assert response.status_code == 200    

def test_get_deliverymodes(app, client):
  response = client.get('/api/foiflow/deliverymodes', headers=factory_user_auth_header(app, client), content_type='application/json')
  assert response.status_code == 200  

def test_get_receivedmodes(app, client):
  response = client.get('/api/foiflow/receivedmodes', headers=factory_user_auth_header(app, client), content_type='application/json')
  assert response.status_code == 200
  
def test_get_divisions(app, client):
  response = client.get('/api/foiflow/divisions/educ', headers=factory_user_auth_header(app, client), content_type='application/json')
  assert response.status_code == 200