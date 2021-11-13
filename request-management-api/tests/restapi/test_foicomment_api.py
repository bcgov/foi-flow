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

with open('tests/samplerequestjson/rawrequest.json') as x:
  rawrequestjson = json.load(x)
def test_foirawcomment(app, client):
    rawresponse = client.post('/api/foirawrequests',data=json.dumps(rawrequestjson), headers=factory_auth_header(app, client), content_type='application/json')
    jsondata = json.loads(rawresponse.data)   
    commentjson = {
    "requestid":str(jsondata["id"]),
    "comment": "test comment",
    "isactive": True
    }
    createcommentresponse = client.post('/api/foicomment/rawrequest', data=json.dumps(commentjson), headers=factory_auth_header(app, client), content_type='application/json')
    getcommentresponse = client.get('/api/foicomment/rawrequest/'+str(jsondata["id"]), headers=factory_auth_header(app, client), content_type='application/json')
    assert rawresponse.status_code == 200 and createcommentresponse.status_code == 200 and getcommentresponse.status_code == 200


with open('tests/samplerequestjson/rawrequest.json') as x:
  rawrequestjson = json.load(x)
def test_foirawcommentdisable(app, client):
    rawresponse = client.post('/api/foirawrequests',data=json.dumps(rawrequestjson), headers=factory_auth_header(app, client), content_type='application/json')
    jsondata = json.loads(rawresponse.data)   
    commentjson = {
    "requestid":str(jsondata["id"]),
    "comment": "test comment",
    "isactive": True
    }
    createcommentresponse = client.post('/api/foicomment/rawrequest', data=json.dumps(commentjson), headers=factory_auth_header(app, client), content_type='application/json')
    comment = json.loads(createcommentresponse.data)  
    disablecommentresponse = client.put('/api/foicomment/rawrequest/'+str(comment["id"])+'/disable',data=json.dumps(commentjson), headers=factory_auth_header(app, client), content_type='application/json')
    assert rawresponse.status_code == 200 and createcommentresponse.status_code == 200 and disablecommentresponse.status_code == 200

with open('tests/samplerequestjson/rawrequest.json') as x:
  rawrequestjson = json.load(x)
def test_foirawcommentupdate(app, client):
    rawresponse = client.post('/api/foirawrequests',data=json.dumps(rawrequestjson), headers=factory_auth_header(app, client), content_type='application/json')
    jsondata = json.loads(rawresponse.data)   
    commentjson = {
    "requestid":str(jsondata["id"]),
    "comment": "test comment",
    "isactive": True
    }
    createcommentresponse = client.post('/api/foicomment/rawrequest', data=json.dumps(commentjson), headers=factory_auth_header(app, client), content_type='application/json')
    comment = json.loads(createcommentresponse.data)  
    updatecommentjson = {
    "comment": "test comment - updated",
    }
    updatecommentresponse = client.put('/api/foicomment/rawrequest/'+str(comment["id"]),data=json.dumps(updatecommentjson), headers=factory_auth_header(app, client), content_type='application/json')
    assert rawresponse.status_code == 200 and createcommentresponse.status_code == 200 and updatecommentresponse.status_code == 200

with open('tests/samplerequestjson/rawrequest.json') as x, open('tests/samplerequestjson/foirequest-general.json') as y:
  generalrequestjson = json.load(y)
  rawrequestjson = json.load(x)
def test_foiministrycomment(app, client):
    rawresponse = client.post('/api/foirawrequests',data=json.dumps(rawrequestjson), headers=factory_auth_header(app, client), content_type='application/json')
    jsondata = json.loads(rawresponse.data)    
    foirequest = generalrequestjson
    foirequest["id"] = str(jsondata["id"])
    foirequest["requeststatusid"] = 1
    foiresponse = client.post('/api/foirequests',data=json.dumps(foirequest), headers=factory_auth_header(app, client), content_type='application/json')
    foijsondata = json.loads(foiresponse.data)    
    commentjson = {
    "ministryrequestid":str(foijsondata["id"]),
    "comment": "test comment",
    "isactive": True
    }
    createcommentresponse = client.post('/api/foicomment/ministryrequest', data=json.dumps(commentjson), headers=factory_auth_header(app, client), content_type='application/json')
    getcommentresponse = client.get('/api/foicomment/ministryrequest/'+str(foijsondata["id"]), headers=factory_auth_header(app, client), content_type='application/json')
    assert rawresponse.status_code == 200 and foiresponse.status_code == 200 and createcommentresponse.status_code == 200 and getcommentresponse.status_code == 200 

with open('tests/samplerequestjson/rawrequest.json') as x, open('tests/samplerequestjson/foirequest-general.json') as y:
  generalrequestjson = json.load(y)
  rawrequestjson = json.load(x)
def test_foiministrycommentdisable(app, client):
    rawresponse = client.post('/api/foirawrequests',data=json.dumps(rawrequestjson), headers=factory_auth_header(app, client), content_type='application/json')
    jsondata = json.loads(rawresponse.data)    
    foirequest = generalrequestjson
    foirequest["id"] = str(jsondata["id"])
    foirequest["requeststatusid"] = 1
    foiresponse = client.post('/api/foirequests',data=json.dumps(foirequest), headers=factory_auth_header(app, client), content_type='application/json')
    foijsondata = json.loads(foiresponse.data)    
    commentjson = {
    "ministryrequestid":str(foijsondata["id"]),
    "comment": "test comment",
    "isactive": True
    }
    createcommentresponse = client.post('/api/foicomment/ministryrequest', data=json.dumps(commentjson), headers=factory_auth_header(app, client), content_type='application/json')
    comment = json.loads(createcommentresponse.data)  
    childcommentjson = {
    "ministryrequestid":str(foijsondata["id"]),
    "comment": "test comment",
    "isactive": True,
    "parentcommentid": str(comment["id"])
    }
    createcommentresponse2 = client.post('/api/foicomment/ministryrequest', data=json.dumps(childcommentjson), headers=factory_auth_header(app, client), content_type='application/json')
    disablecommentresponse = client.put('/api/foicomment/rawrequest/'+str(comment["id"])+'/disable',data=json.dumps(commentjson), headers=factory_auth_header(app, client), content_type='application/json')
    assert rawresponse.status_code == 200 and foiresponse.status_code == 200 and createcommentresponse.status_code == 200 and createcommentresponse2.status_code == 200 and disablecommentresponse.status_code == 200 
      
with open('tests/samplerequestjson/rawrequest.json') as x, open('tests/samplerequestjson/foirequest-general.json') as y:
  generalrequestjson = json.load(y)
  rawrequestjson = json.load(x)
def test_foiministrycommentupdate(app, client):
    rawresponse = client.post('/api/foirawrequests',data=json.dumps(rawrequestjson), headers=factory_auth_header(app, client), content_type='application/json')
    jsondata = json.loads(rawresponse.data)    
    foirequest = generalrequestjson
    foirequest["id"] = str(jsondata["id"])
    foirequest["requeststatusid"] = 1
    foiresponse = client.post('/api/foirequests',data=json.dumps(foirequest), headers=factory_auth_header(app, client), content_type='application/json')
    foijsondata = json.loads(foiresponse.data)    
    commentjson = {
    "ministryrequestid":str(foijsondata["id"]),
    "comment": "test comment",
    "isactive": True
    }
    createcommentresponse = client.post('/api/foicomment/ministryrequest', data=json.dumps(commentjson), headers=factory_auth_header(app, client), content_type='application/json')
    comment = json.loads(createcommentresponse.data)  
    updatecommentjson = {
    "comment": "test comment - updated",
    }
    updatecommentresponse = client.put('/api/foicomment/ministryrequest/'+str(comment["id"]),data=json.dumps(updatecommentjson), headers=factory_auth_header(app, client), content_type='application/json')
    assert rawresponse.status_code == 200 and foiresponse.status_code == 200 and createcommentresponse.status_code == 200 and updatecommentresponse.status_code == 200 
      
    
with open('tests/samplerequestjson/rawrequest.json') as x, open('tests/samplerequestjson/foirequest-general.json') as y:
  generalrequestjson = json.load(y)
  rawrequestjson = json.load(x)
def test_foiministrycommentmigrate(app, client):
    rawresponse = client.post('/api/foirawrequests',data=json.dumps(rawrequestjson), headers=factory_auth_header(app, client), content_type='application/json')
    jsondata = json.loads(rawresponse.data)    
    foirequest = generalrequestjson
    foirequest["id"] = str(jsondata["id"])
    foirequest["requeststatusid"] = 1
    commentjson = {
    "requestid":str(jsondata["id"]),
    "comment": "test comment",
    "isactive": True
    }
    createcommentresponse1 = client.post('/api/foicomment/rawrequest', data=json.dumps(commentjson), headers=factory_auth_header(app, client), content_type='application/json')
    comment = json.loads(createcommentresponse1.data)  
    childcommentjson = {
    "requestid":str(jsondata["id"]),
    "comment": "test comment",
    "isactive": True,
    "parentcommentid": str(comment["id"])
    }
    createcommentresponse2 = client.post('/api/foicomment/rawrequest', data=json.dumps(childcommentjson), headers=factory_auth_header(app, client), content_type='application/json')
    foiresponse = client.post('/api/foirequests',data=json.dumps(foirequest), headers=factory_auth_header(app, client), content_type='application/json')
    assert rawresponse.status_code == 200 and createcommentresponse1.status_code == 200 and createcommentresponse2.status_code == 200 and foiresponse.status_code == 200