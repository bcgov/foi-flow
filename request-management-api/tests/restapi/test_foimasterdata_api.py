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
  response = client.get('/api/foiflow/divisions/edu', headers=factory_user_auth_header(app, client), content_type='application/json')
  assert response.status_code == 200

def test_get_closereasons(app, client):
  response = client.get('/api/foiflow/closereasons', headers=factory_user_auth_header(app, client), content_type='application/json')
  assert response.status_code == 200

with open('tests/samplerequestjson/s3storagerequest.json') as f:
  s3requestjson = json.load(f)
def test_post_fois3storagerequests(app, client):    
    response = client.post('api/foiflow/oss/authheader',headers=factory_user_auth_header(app, client),data=json.dumps(s3requestjson), content_type='application/json')
    jsonresponse = json.loads(response.data)
    for item in jsonresponse:
        assert item['authheader'] is not None and  item['filepath'] is not None
    assert response.status_code == 200 and len(jsonresponse) >=1  

def test_get_extensionreasons(app, client):
  response = client.get('/api/foiflow/extensionreasons', headers=factory_user_auth_header(app, client), content_type='application/json')
  assert response.status_code == 200

def test_get_all_divisions(app, client):
   response = client.get('/api/foiflow/divisions', headers=factory_user_auth_header(app, client), content_type='application/json')
   assert response.status_code == 200