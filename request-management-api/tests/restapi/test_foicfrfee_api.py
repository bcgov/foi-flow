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

TEST_CFR_FEE_SCHEMA = {
    "feedata":{ 
        "amountpaid":11.00, 
        "totalamountdue":2.00, 
        "estimatedlocatinghrs": 11.00, 
        "actuallocatinghrs": 11.00, 
        "estimatedproducinghrs": 11.00, 
        "actualproducinghrs": 11.00, 
        "estimatediaopreparinghrs": 11.44444433330440,
        "estimatedministrypreparinghrs": 11.44444433330440,
        "actualiaopreparinghrs": 11.00,
        "actualministrypreparinghrs": 11.00,
        "estimatedelectronicpages": 11.00, 
        "actualelectronicpages": 11.00, 
        "estimatedhardcopypages": 11.00, 
        "actualhardcopypages": 9 
    }, 
    "overallsuggestions":"test"
}

TEST_CFR_FEE_SANCTION_SCHEMA = {
    "feedata":{
        "amountpaid":5.00 
    }, 
    "status":"approved" 
}


RAW_REQUEST_POST_URL = '/api/foirawrequests'
REQUEST_POST_URL = '/api/foirequests'
RAW_REQUEST_JSON = 'tests/samplerequestjson/rawrequest.json'
FOI_REQUEST_GENERAL_JSON = 'tests/samplerequestjson/foirequest-general.json'
FOI_REQUEST_GENERAL_UPDATE_JSON = 'tests/samplerequestjson/foirequest-general-update.json'
FOI_REQUEST_GENERAL_CFR_JSON = 'tests/samplerequestjson/foirequest-general-CFR.json'
WF_URL_BASE = '/api/foirawrequestbpm/addwfinstanceid/'
CREATE_CFR_FEE_URL = '/api/foicfrfee/ministryrequest/'
GET_CFR_FEE_URL = '/api/foicfrfee/ministryrequest/'

CONTENT_TYPE = 'application/json'

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

with open(RAW_REQUEST_JSON) as x, open(FOI_REQUEST_GENERAL_JSON) as y, open(FOI_REQUEST_GENERAL_UPDATE_JSON) as z, open(FOI_REQUEST_GENERAL_CFR_JSON) as v:
  generalcfrrequestjson = json.load(v)
  generalupdaterequestjson = json.load(z)
  generalrequestjson = json.load(y)
  rawrequestjson = json.load(x)


def test_foicfrfees_create(app, client):  
    rawresponse = client.post(RAW_REQUEST_POST_URL,data=json.dumps(rawrequestjson), headers=factory_intake_auth_header(app, client), content_type=CONTENT_TYPE)
    jsondata = json.loads(rawresponse.data)    
    foirequest = generalrequestjson
    foirequest["id"] = str(jsondata["id"])
    foirequest["requeststatusid"] = 1
    foiresponse = client.post(REQUEST_POST_URL,data=json.dumps(foirequest), headers=factory_intake_auth_header(app, client), content_type=CONTENT_TYPE)
    foijsondata = json.loads(foiresponse.data)    
    wfinstanceid={"wfinstanceid":str(uuid.uuid4())}
    wfupdateresponse = client.put(WF_URL_BASE+str(jsondata["id"]),data=json.dumps(wfinstanceid), headers=factory_intake_auth_header(app, client), content_type=CONTENT_TYPE)
    cfrrequestposturl = REQUEST_POST_URL+'/'+str(foijsondata["id"])+'/ministryrequest/'+str(foijsondata["ministryRequests"][0]["id"])
    cfrrequest = generalcfrrequestjson
    cfrrequest["requeststatusid"] = 2
    foicfrrequestresponse = client.post(cfrrequestposturl,data=json.dumps(cfrrequest), headers=factory_intake_auth_header(app, client), content_type=CONTENT_TYPE)
    foicfrrequestjsondata = json.loads(foicfrrequestresponse.data)  
    createfoicfrfeesresponse = client.post(CREATE_CFR_FEE_URL+str(foicfrrequestjsondata["ministryRequests"][0]["id"]),data=json.dumps(TEST_CFR_FEE_SCHEMA), headers=factory_ministry_auth_header(app, client), content_type=CONTENT_TYPE)
    assert rawresponse.status_code == 200 and foiresponse.status_code == 200 and wfupdateresponse.status_code == 200


def test_foicfrfees_sanction(app, client):  
    rawresponse = client.post(RAW_REQUEST_POST_URL,data=json.dumps(rawrequestjson), headers=factory_intake_auth_header(app, client), content_type=CONTENT_TYPE)
    jsondata = json.loads(rawresponse.data)    
    foirequest = generalrequestjson
    foirequest["id"] = str(jsondata["id"])
    foirequest["requeststatusid"] = 1
    foiresponse = client.post(REQUEST_POST_URL,data=json.dumps(foirequest), headers=factory_intake_auth_header(app, client), content_type=CONTENT_TYPE)
    foijsondata = json.loads(foiresponse.data)    
    wfinstanceid={"wfinstanceid":str(uuid.uuid4())}
    wfupdateresponse = client.put(WF_URL_BASE+str(jsondata["id"]),data=json.dumps(wfinstanceid), headers=factory_intake_auth_header(app, client), content_type=CONTENT_TYPE)
    cfrrequestposturl = REQUEST_POST_URL+'/'+str(foijsondata["id"])+'/ministryrequest/'+str(foijsondata["ministryRequests"][0]["id"])
    cfrrequest = generalcfrrequestjson
    cfrrequest["requeststatusid"] = 2
    foicfrrequestresponse = client.post(cfrrequestposturl,data=json.dumps(cfrrequest), headers=factory_intake_auth_header(app, client), content_type=CONTENT_TYPE)
    foicfrrequestjsondata = json.loads(foicfrrequestresponse.data)  
    createfoicfrfeesresponse = client.post(CREATE_CFR_FEE_URL+str(foicfrrequestjsondata["ministryRequests"][0]["id"]),data=json.dumps(TEST_CFR_FEE_SCHEMA), headers=factory_ministry_auth_header(app, client), content_type=CONTENT_TYPE)
    sanctionfoicfrfeesresponse = client.post(CREATE_CFR_FEE_URL+str(foicfrrequestjsondata["ministryRequests"][0]["id"])+"/sanction",data=json.dumps(TEST_CFR_FEE_SANCTION_SCHEMA), headers=factory_intake_auth_header(app, client), content_type=CONTENT_TYPE)
    assert rawresponse.status_code == 200 and foiresponse.status_code == 200 and wfupdateresponse.status_code == 200


def test_foicfrfees_get(app, client):  
    rawresponse = client.post(RAW_REQUEST_POST_URL,data=json.dumps(rawrequestjson), headers=factory_intake_auth_header(app, client), content_type=CONTENT_TYPE)
    jsondata = json.loads(rawresponse.data)    
    foirequest = generalrequestjson
    foirequest["id"] = str(jsondata["id"])
    foirequest["requeststatusid"] = 1
    foiresponse = client.post(REQUEST_POST_URL,data=json.dumps(foirequest), headers=factory_intake_auth_header(app, client), content_type=CONTENT_TYPE)
    foijsondata = json.loads(foiresponse.data)    
    wfinstanceid={"wfinstanceid":str(uuid.uuid4())}
    wfupdateresponse = client.put(WF_URL_BASE+str(jsondata["id"]),data=json.dumps(wfinstanceid), headers=factory_intake_auth_header(app, client), content_type=CONTENT_TYPE)
    cfrrequestposturl = REQUEST_POST_URL+'/'+str(foijsondata["id"])+'/ministryrequest/'+str(foijsondata["ministryRequests"][0]["id"])
    cfrrequest = generalcfrrequestjson
    cfrrequest["requeststatusid"] = 2
    foicfrrequestresponse = client.post(cfrrequestposturl,data=json.dumps(cfrrequest), headers=factory_intake_auth_header(app, client), content_type=CONTENT_TYPE)
    foicfrrequestjsondata = json.loads(foicfrrequestresponse.data)  
    createfoicfrfeesresponse = client.post(CREATE_CFR_FEE_URL+str(foicfrrequestjsondata["ministryRequests"][0]["id"]),data=json.dumps(TEST_CFR_FEE_SCHEMA), headers=factory_ministry_auth_header(app, client), content_type=CONTENT_TYPE)
    getfoicfrfeeresponse = client.get(CREATE_CFR_FEE_URL+str(foicfrrequestjsondata["ministryRequests"][0]["id"]), headers=factory_intake_auth_header(app, client), content_type=CONTENT_TYPE)
    assert rawresponse.status_code == 200 and foiresponse.status_code == 200 and wfupdateresponse.status_code == 200
