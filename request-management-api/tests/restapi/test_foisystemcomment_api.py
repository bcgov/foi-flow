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

FOI_DIVISION_BASE_PAYLOAD = {
    "assignedministrygroup":"EDU Ministry Team",
    "assignedministryperson":"foiedu@idir",
    "assignedministrypersonFirstName":"foiedu",
    "assignedministrypersonLastName":"foiedu"    
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

with open('tests/samplerequestjson/rawrequest.json') as x, open('tests/samplerequestjson/foirequest-general.json') as y, open('tests/samplerequestjson/foirequest-general-update.json') as z:
  generalrequestjson = json.load(y)
  generalupdaterequestjson = json.load(z)
  rawrequestjson = json.load(x)
def test_createrawrequest_state_comment_intakeinprogres_to_open(app, client):
    rawresponse = client.post('/api/foirawrequests',data=json.dumps(rawrequestjson), headers=factory_auth_header(app, client), content_type='application/json')
    jsondata = json.loads(rawresponse.data)   
    updatejson = generalupdaterequestjson
    updatejson["id"] = str(jsondata["id"])
    updatejson['ispiiredacted'] = True
    updatejson['requeststatusid'] = 1
    updateresponse = client.post('/api/foirawrequest/'+str(jsondata["id"]),data=json.dumps(updatejson), headers=factory_auth_header(app, client), content_type='application/json')
    getcommentresponse = client.get('/api/foicomment/rawrequest/'+str(jsondata["id"]), headers=factory_auth_header(app, client), content_type='application/json')
    assert rawresponse.status_code == 200 and updateresponse.status_code == 200  and getcommentresponse.status_code == 200  and len(getcommentresponse.data) >=1 
  

with open('tests/samplerequestjson/rawrequest.json') as x, open('tests/samplerequestjson/foirequest-general.json') as y, open('tests/samplerequestjson/foirequest-general-update.json') as z:
  generalrequestjson = json.load(y)
  generalupdaterequestjson = json.load(z)
  rawrequestjson = json.load(x)
def test_createrawrequest_division_comment(app, client):
    rawresponse = client.post('/api/foirawrequests',data=json.dumps(rawrequestjson), headers=factory_auth_header(app, client), content_type='application/json')
    jsondata = json.loads(rawresponse.data)    
    getrawresponse = client.get('/api/foirawrequest/'+str(jsondata["id"]), headers=factory_auth_header(app, client), content_type='application/json') 
    foirequest = generalrequestjson
    foirequest["id"] = str(jsondata["id"])
    foirequest["requeststatusid"] = 1
    foiresponse = client.post('/api/foirequests',data=json.dumps(foirequest), headers=factory_auth_header(app, client), content_type='application/json')
    foijsondata = json.loads(foiresponse.data)    
    wfinstanceid={"wfinstanceid":str(uuid.uuid4())}
    wfupdateresponse = client.put('/api/foirawrequestbpm/addwfinstanceid/'+str(jsondata["id"]),data=json.dumps(wfinstanceid), headers=factory_auth_header(app, client), content_type='application/json')
    foiupdaterequest = generalupdaterequestjson
    foiupdaterequest["id"] = str(foijsondata["id"])
    foiupdaterequest["idNumber"] = str(foijsondata["ministryRequests"][0]["filenumber"])
    foiupdaterequest["requeststatusid"] = 2
    foiassignresponse = client.post('/api/foirequests/'+str(foijsondata["id"])+'/ministryrequest/'+str(foijsondata["ministryRequests"][0]["id"]),data=json.dumps(foiupdaterequest), headers=factory_auth_header(app, client), content_type='application/json')
    foiministryreqresponse = client.get('/api/foirequests/'+str(foijsondata["id"])+'/ministryrequest/'+str(foijsondata["ministryRequests"][0]["id"])+'/ministry',headers=factory_ministry_auth_header(app, client), content_type='application/json')
    
    addfoidivisionrequest = FOI_DIVISION_BASE_PAYLOAD
    addfoidivisionrequest["requeststatusid"] = 2
    addfoidivisionrequest["divisions"] = [{"divisionid":1,"stageid":1},{"divisionid":2,"stageid":1}]
    addfoicfrdivisionresponse = client.post('/api/foirequests/'+str(foijsondata["id"])+'/ministryrequest/'+str(foijsondata["ministryRequests"][0]["id"])+'/ministry',data=json.dumps(addfoidivisionrequest), headers=factory_ministry_auth_header(app, client), content_type='application/json')
    modfoidivisionrequest = FOI_DIVISION_BASE_PAYLOAD
    modfoidivisionrequest["requeststatusid"] = 2
    modfoidivisionrequest["divisions"] = [{"divisionid":1,"stageid":2},{"divisionid":2,"stageid":1}]
    modfoicfrdivisionresponse = client.post('/api/foirequests/'+str(foijsondata["id"])+'/ministryrequest/'+str(foijsondata["ministryRequests"][0]["id"])+'/ministry',data=json.dumps(modfoidivisionrequest), headers=factory_ministry_auth_header(app, client), content_type='application/json')
    delfoidivisionrequest = FOI_DIVISION_BASE_PAYLOAD
    delfoidivisionrequest["requeststatusid"] = 2
    delfoidivisionrequest["divisions"] = [{"divisionid":2,"stageid":1}]
    delfoicfrdivisionresponse = client.post('/api/foirequests/'+str(foijsondata["id"])+'/ministryrequest/'+str(foijsondata["ministryRequests"][0]["id"])+'/ministry',data=json.dumps(delfoidivisionrequest), headers=factory_ministry_auth_header(app, client), content_type='application/json')
    getcommentresponse = client.get('/api/foicomment/ministryrequest/'+str(foijsondata["ministryRequests"][0]["id"]), headers=factory_ministry_auth_header(app, client), content_type='application/json')
    assert foiministryreqresponse.status_code == 200 and foiresponse.status_code == 200 and getrawresponse.status_code == 200 and wfupdateresponse.status_code == 200 and foiassignresponse.status_code == 200 and addfoicfrdivisionresponse.status_code == 200  and modfoicfrdivisionresponse.status_code == 200 and delfoicfrdivisionresponse.status_code == 200 and getcommentresponse.status_code == 200  and len(getcommentresponse.data) >=1 
 