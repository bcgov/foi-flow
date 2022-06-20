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
def test_ping(app, client):
    response = client.get('/api/healthz')
    assert response.status_code == 200


with open('tests/samplerequestjson/rawrequest.json') as x, open('tests/samplerequestjson/foirequest-general.json') as y, open('tests/samplerequestjson/foirequest-general-update.json') as z:
  generalrequestjson = json.load(y)
  generalupdaterequestjson = json.load(z)
  rawrequestjson = json.load(x)
def test_post_get_foirequest_general_cfr_notification(app, client):
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
    foiministryreqresponse = client.get('/api/foirequests/'+str(foijsondata["id"])+'/ministryrequest/'+str(foijsondata["ministryRequests"][0]["id"])+'/ministry',headers=factory_ministryuser_auth_header(app, client), content_type='application/json')
    foinotification = client.get('/api/foinotifications',headers=factory_ministryuser_auth_header(app, client), content_type='application/json')
    assert foiministryreqresponse.status_code == 200 and foiresponse.status_code == 200 and getrawresponse.status_code == 200 and wfupdateresponse.status_code == 200 and foiassignresponse.status_code == 200 and foinotification.status_code == 200


with open('tests/samplerequestjson/rawrequest.json') as x, open('tests/samplerequestjson/foirequest-general.json') as y, open('tests/samplerequestjson/foirequest-general-update.json') as z:
  generalrequestjson = json.load(y)
  generalupdaterequestjson = json.load(z)
  rawrequestjson = json.load(x)
def test_dismiss_foirequest_general_cfr_notification(app, client):
    rawresponse = client.post('/api/foirawrequests',data=json.dumps(rawrequestjson), headers=factory_user_auth_header(app, client), content_type='application/json')
    jsondata = json.loads(rawresponse.data)   
    watcherjson = {
    "requestid":str(jsondata["id"]),
    "watchedbygroup": "Intake Team",
    "watchedby": "sumathi",
    "isactive": True
    }
    createwatcherresponse = client.post('/api/foiwatcher/rawrequest', data=json.dumps(watcherjson), headers=factory_user_auth_header(app, client), content_type='application/json')    
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
    foiministryreqresponse = client.get('/api/foirequests/'+str(foijsondata["id"])+'/ministryrequest/'+str(foijsondata["ministryRequests"][0]["id"])+'/ministry',headers=factory_ministryuser_auth_header(app, client), content_type='application/json')
    foinotification = client.get('/api/foinotifications',headers=factory_ministryuser_auth_header(app, client), content_type='application/json')
    foinotificationdata = json.loads(foinotification.data)
    deletefoinotification = client.delete('/api/foinotifications/watcher',headers=factory_ministryuser_auth_header(app, client), content_type='application/json')
    assert foiministryreqresponse.status_code == 200 and foiresponse.status_code == 200 and getrawresponse.status_code == 200 and wfupdateresponse.status_code == 200 and foiassignresponse.status_code == 200 and foinotification.status_code == 200 and createwatcherresponse.status_code == 200 and deletefoinotification.status_code == 200


with open('tests/samplerequestjson/rawrequest.json') as x, open('tests/samplerequestjson/foirequest-general.json') as y, open('tests/samplerequestjson/foirequest-general-update.json') as z:
  generalrequestjson = json.load(y)
  generalupdaterequestjson = json.load(z)
  rawrequestjson = json.load(x)
def test_dismissall_foirequest_general_cfr_notification(app, client):
    rawresponse = client.post('/api/foirawrequests',data=json.dumps(rawrequestjson), headers=factory_user_auth_header(app, client), content_type='application/json')
    jsondata = json.loads(rawresponse.data)   
    watcherjson = {
    "requestid":str(jsondata["id"]),
    "watchedbygroup": "Intake Team",
    "watchedby": "sumathi",
    "isactive": True
    }
    createwatcherresponse = client.post('/api/foiwatcher/rawrequest', data=json.dumps(watcherjson), headers=factory_user_auth_header(app, client), content_type='application/json')    
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
    foiministryreqresponse = client.get('/api/foirequests/'+str(foijsondata["id"])+'/ministryrequest/'+str(foijsondata["ministryRequests"][0]["id"])+'/ministry',headers=factory_ministryuser_auth_header(app, client), content_type='application/json')
    foinotification = client.get('/api/foinotifications',headers=factory_user_auth_header(app, client), content_type='application/json')
    deletefoinotification = client.delete('/api/foinotifications',headers=factory_user_auth_header(app, client), content_type='application/json')
    assert foiministryreqresponse.status_code == 200 and foiresponse.status_code == 200 and getrawresponse.status_code == 200 and wfupdateresponse.status_code == 200 and foiassignresponse.status_code == 200 and foinotification.status_code == 200 and createwatcherresponse.status_code == 200 and deletefoinotification.status_code == 200

with open('tests/samplerequestjson/rawrequest.json') as x, open('tests/samplerequestjson/foirequest-general.json') as y, open('tests/samplerequestjson/foirequest-general-update.json') as z:
  generalrequestjson = json.load(y)
  generalupdaterequestjson = json.load(z)
  rawrequestjson = json.load(x)
def test_foirequest_general_cfr_notification_reminder(app, client):
    rawresponse = client.post('/api/foirawrequests',data=json.dumps(rawrequestjson), headers=factory_user_auth_header(app, client), content_type='application/json')
    jsondata = json.loads(rawresponse.data)   
    watcherjson = {
    "requestid":str(jsondata["id"]),
    "watchedbygroup": "Intake Team",
    "watchedby": "sumathi",
    "isactive": True
    }
    createwatcherresponse = client.post('/api/foiwatcher/rawrequest', data=json.dumps(watcherjson), headers=factory_user_auth_header(app, client), content_type='application/json')    
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
    foiministryreqresponse = client.get('/api/foirequests/'+str(foijsondata["id"])+'/ministryrequest/'+str(foijsondata["ministryRequests"][0]["id"])+'/ministry',headers=factory_ministryuser_auth_header(app, client), content_type='application/json')
    foinotification = client.get('/api/foinotifications',headers=factory_user_auth_header(app, client), content_type='application/json')
    reminderfoinotification = client.post('/api/foinotifications/reminder',headers=factory_user_auth_header(app, client), content_type='application/json')
    assert foiministryreqresponse.status_code == 200 and foiresponse.status_code == 200 and getrawresponse.status_code == 200 and wfupdateresponse.status_code == 200 and foiassignresponse.status_code == 200 and foinotification.status_code == 200 and createwatcherresponse.status_code == 200 and reminderfoinotification.status_code == 200
