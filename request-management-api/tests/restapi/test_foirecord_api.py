import json
import uuid
import os
import requests
import ast

TEST_INTAKE_USER_PAYLOAD = {
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

def factory_intake_auth_header(app, client):
    url = '{0}/auth/realms/{1}/protocol/openid-connect/token'.format(os.getenv('KEYCLOAK_ADMIN_HOST'),os.getenv('KEYCLOAK_ADMIN_REALM'))        
    x = requests.post(url, TEST_INTAKE_USER_PAYLOAD, verify=True).content.decode('utf-8')       
    return {'Authorization': 'Bearer ' + str(ast.literal_eval(x)['access_token'])}  

def factory_ministry_auth_header(app, client):
    url = '{0}/auth/realms/{1}/protocol/openid-connect/token'.format(os.getenv('KEYCLOAK_ADMIN_HOST'),os.getenv('KEYCLOAK_ADMIN_REALM'))        
    x = requests.post(url, TEST_MINISTRY_USER_PAYLOAD, verify=True).content.decode('utf-8')       
    return {'Authorization': 'Bearer ' + str(ast.literal_eval(x)['access_token'])}  

def test_ping(app, client):
    response = client.get('/api/healthz')
    assert response.status_code == 200

with open('tests/samplerequestjson/rawrequest.json') as x, open('tests/samplerequestjson/foirequest-general.json') as y, open('tests/samplerequestjson/foirequest-general-update.json') as z, open('tests/samplerequestjson/foirequest-ministry-general-update.json') as v:
  generalministryrequestjson = json.load(v)
  generalupdaterequestjson = json.load(z)
  generalrequestjson = json.load(y)
  rawrequestjson = json.load(x)
def test_foiministrydocument_list(app, client):
    rawresponse = client.post('/api/foirawrequests',data=json.dumps(rawrequestjson), headers=factory_intake_auth_header(app, client), content_type='application/json')
    jsondata = json.loads(rawresponse.data)    
    foirequest = generalrequestjson
    foirequest["id"] = str(jsondata["id"])
    foirequest["requeststatusid"] = 1
    foiresponse = client.post('/api/foirequests',data=json.dumps(foirequest), headers=factory_intake_auth_header(app, client), content_type='application/json')
    foijsondata = json.loads(foiresponse.data)    
    wfinstanceid={"wfinstanceid":str(uuid.uuid4())}
    wfupdateresponse = client.put('/api/foirawrequestbpm/addwfinstanceid/'+str(jsondata["id"]),data=json.dumps(wfinstanceid), headers=factory_intake_auth_header(app, client), content_type='application/json')
    foiministryrequest = generalministryrequestjson
    foiministryrequest["id"] = str(foijsondata["id"])
    foiministryrequest["idNumber"] = str(foijsondata["ministryRequests"][0]["filenumber"])
    foiministryrequest["requeststatusid"] = 2
    foiministryresponse = client.post('/api/foirequests/'+str(foijsondata["id"])+'/ministryrequest/'+str(foijsondata["ministryRequests"][0]["id"])+'/ministry',data=json.dumps(foiministryrequest), headers=factory_intake_auth_header(app, client), content_type='application/json')
    foiministryrequest2 = generalministryrequestjson
    foiministryrequest2["id"] = str(foijsondata["id"])
    foiministryrequest2["idNumber"] = str(foijsondata["ministryRequests"][0]["filenumber"])
    foiministryrequest2["documents"] = [
        {
            "category": "cfr-feeassessed",
            "documentpath":"/EDUC/"+str(foijsondata["ministryRequests"][0]["filenumber"])+"/cfr-review/test.docx",
            "filename":"test.docx"
        }
        ]
    foiministryrequest2["requeststatusid"] = 7
    foiministryresponse2 = client.post('/api/foirequests/'+str(foijsondata["id"])+'/ministryrequest/'+str(foijsondata["ministryRequests"][0]["id"])+'/ministry',data=json.dumps(foiministryrequest2), headers=factory_intake_auth_header(app, client), content_type='application/json')
    getdocumentsresponse = client.get('/api/foidocument/ministryrequest/'+str(foijsondata["id"]), headers=factory_ministry_auth_header(app, client), content_type='application/json')
    foirecordrequest = { "records": [{
    "divisionid":1,
    "s3uripath":"/s3/test/3434",
    "filename": "test.pdf"
    },
    {
    "divisionid":1,
    "s3uripath":"/s3/test/3434",
    "filename": "test2.pdf"
    }]
    }
    foirecordresponse1 = client.post('/api/foirecord/'+str(foijsondata["id"])+'/ministryrequest/'+str(foijsondata["ministryRequests"][0]["id"]),data=json.dumps(foirecordrequest), headers=factory_ministry_auth_header(app, client), content_type='application/json')
    getrecordresponse = client.get('/api/foirecord/'+str(foijsondata["id"])+'/ministryrequest/'+str(foijsondata["id"]), headers=factory_ministry_auth_header(app, client), content_type='application/json')
    assert rawresponse.status_code == 200 and foiresponse.status_code == 200 and wfupdateresponse.status_code == 200 and foiministryresponse.status_code == 200 and foiministryresponse2.status_code == 200 and getdocumentsresponse.status_code == 200 and foirecordresponse1.status_code == 200 and getrecordresponse.status_code == 200 

