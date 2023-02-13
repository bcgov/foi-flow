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

NEW_EXTENSION_SCHEMA = {
        "extensionreasonid": 5,
        "extendedduedays": 30,
        "extendedduedate": "2022-03-04" 
    }

RAW_REQUEST_JSON = 'tests/samplerequestjson/rawrequest.json'
FOI_REQUEST_GENERAL_JSON = 'tests/samplerequestjson/foirequest-general.json'
FOI_REQUEST_GENERAL_UPDATE_JSON = 'tests/samplerequestjson/foirequest-general-update.json'
FOI_REQUEST_GENERAL_MINISTRY_UPDATE_JSON = 'tests/samplerequestjson/foirequest-ministry-general-update.json'
RAW_REQUEST_POST_URL = '/api/foirawrequests'
REQUEST_POST_URL = '/api/foirequests'
WF_URL_BASE = '/api/foirawrequestbpm/addwfinstanceid/'
CREATE_EXTN_BASE_URL = '/api/foiextension/foirequest/'
GET_EXTN_BASE_URL = '/api/foiextension/ministryrequest/'

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

with open(RAW_REQUEST_JSON) as x, open(FOI_REQUEST_GENERAL_JSON) as y, open(FOI_REQUEST_GENERAL_UPDATE_JSON) as z, open(FOI_REQUEST_GENERAL_MINISTRY_UPDATE_JSON) as v:
  generalministryrequestjson = json.load(v)
  generalupdaterequestjson = json.load(z)
  generalrequestjson = json.load(y)
  rawrequestjson = json.load(x)

def test_foiministryextension_list(app, client):
    rawresponse = client.post(RAW_REQUEST_POST_URL,data=json.dumps(rawrequestjson), headers=factory_intake_auth_header(app, client), content_type=CONTENT_TYPE)
    jsondata = json.loads(rawresponse.data)    
    foirequest = generalrequestjson
    foirequest["id"] = str(jsondata["id"])
    foirequest["requeststatusid"] = 1
    foiresponse = client.post(REQUEST_POST_URL,data=json.dumps(foirequest), headers=factory_intake_auth_header(app, client), content_type=CONTENT_TYPE)
    foijsondata = json.loads(foiresponse.data)    
    wfinstanceid={"wfinstanceid":str(uuid.uuid4())}
    wfupdateresponse = client.put(WF_URL_BASE + str(jsondata["id"]),data=json.dumps(wfinstanceid), headers=factory_intake_auth_header(app, client), content_type=CONTENT_TYPE)
    foiministryrequest = generalministryrequestjson
    foiministryrequest["id"] = str(foijsondata["id"])
    foiministryrequest["idNumber"] = str(foijsondata["ministryRequests"][0]["filenumber"])
    foiministryrequest["requeststatusid"] = 2
    requestposturl = REQUEST_POST_URL+'/'+str(foijsondata["id"])+'/ministryrequest/'+str(foijsondata["ministryRequests"][0]["id"])+'/ministry'
    foiministryresponse = client.post(requestposturl,data=json.dumps(foiministryrequest), headers=factory_intake_auth_header(app, client), content_type=CONTENT_TYPE)
    foiministryrequest2 = generalministryrequestjson
    foiministryrequest2["id"] = str(foijsondata["id"])
    foiministryrequest2["idNumber"] = str(foijsondata["ministryRequests"][0]["filenumber"])
    foiministryrequest2["documents"] = [
        {
            "category": "cfr-feeassessed",
            "documentpath":"/EDU/"+str(foijsondata["ministryRequests"][0]["filenumber"])+"/cfr-review/test.docx",
            "filename":"test.docx"
        }
        ]
    foiministryrequest2["requeststatusid"] = 7
    foiministryresponse2 = client.post(requestposturl,data=json.dumps(foiministryrequest2), headers=factory_intake_auth_header(app, client), content_type=CONTENT_TYPE)
    ministryid = str(foijsondata["ministryRequests"][0]["id"])
    createextnresponse = client.post(CREATE_EXTN_BASE_URL+str(foijsondata["id"])+'/ministryrequest/'+ministryid,data=json.dumps(NEW_EXTENSION_SCHEMA), headers=factory_intake_auth_header(app, client), content_type=CONTENT_TYPE)   
    getextensionssresponse = client.get(GET_EXTN_BASE_URL+ministryid, headers=factory_ministry_auth_header(app, client), content_type=CONTENT_TYPE)
    assert rawresponse.status_code == 200 and foiresponse.status_code == 200 and wfupdateresponse.status_code == 200 and foiministryresponse.status_code == 200 and foiministryresponse2.status_code == 200 and createextnresponse.status_code == 200 and getextensionssresponse.status_code == 200

def test_foiministryextension_create(app, client):  
    rawresponse = client.post(RAW_REQUEST_POST_URL,data=json.dumps(rawrequestjson), headers=factory_intake_auth_header(app, client), content_type=CONTENT_TYPE)
    jsondata = json.loads(rawresponse.data)    
    foirequest = generalrequestjson
    foirequest["id"] = str(jsondata["id"])
    foirequest["requeststatusid"] = 1
    foiresponse = client.post(REQUEST_POST_URL,data=json.dumps(foirequest), headers=factory_intake_auth_header(app, client), content_type=CONTENT_TYPE)
    foijsondata = json.loads(foiresponse.data)    
    wfinstanceid={"wfinstanceid":str(uuid.uuid4())}
    wfupdateresponse = client.put(WF_URL_BASE+str(jsondata["id"]),data=json.dumps(wfinstanceid), headers=factory_intake_auth_header(app, client), content_type=CONTENT_TYPE)
 
    foiministryextnresponse = client.post(CREATE_EXTN_BASE_URL+str(foijsondata["id"])+'/ministryrequest/'+str(foijsondata["ministryRequests"][0]["id"]),data=json.dumps(NEW_EXTENSION_SCHEMA), headers=factory_intake_auth_header(app, client), content_type=CONTENT_TYPE)
    assert rawresponse.status_code == 200 and foiresponse.status_code == 200 and wfupdateresponse.status_code == 200 and foiministryextnresponse.status_code == 200

def test_foiministryextension_edit(app, client):
    rawresponse = client.post(RAW_REQUEST_POST_URL,data=json.dumps(rawrequestjson), headers=factory_intake_auth_header(app, client), content_type=CONTENT_TYPE)
    jsondata = json.loads(rawresponse.data)    
    foirequest = generalrequestjson
    foirequest["id"] = str(jsondata["id"])
    foirequest["requeststatusid"] = 1
    foiresponse = client.post(REQUEST_POST_URL,data=json.dumps(foirequest), headers=factory_intake_auth_header(app, client), content_type=CONTENT_TYPE)
    foijsondata = json.loads(foiresponse.data)    
    wfinstanceid={"wfinstanceid":str(uuid.uuid4())}
    wfupdateresponse = client.put(WF_URL_BASE+str(jsondata["id"]),data=json.dumps(wfinstanceid), headers=factory_intake_auth_header(app, client), content_type=CONTENT_TYPE)
   
    createextnresponse = client.post(CREATE_EXTN_BASE_URL+str(foijsondata["id"])+'/ministryrequest/'+str(foijsondata["ministryRequests"][0]["id"]),data=json.dumps(NEW_EXTENSION_SCHEMA), headers=factory_intake_auth_header(app, client), content_type=CONTENT_TYPE)   
    getextensionssresponse = client.get(GET_EXTN_BASE_URL+str(foijsondata["ministryRequests"][0]["id"]), headers=factory_ministry_auth_header(app, client), content_type=CONTENT_TYPE)
    getextensionssresponsejsondata = json.loads(getextensionssresponse.data) 
    extensionschema = {
        "extensionreasonid": 7,
        "extensionstatusid": 1,
        "extendedduedays": 2,
        "extendedduedate": "2022-03-07" ,
        "decisiondate": "2022-01-20",
        "approvednoofdays": 3,
        "documents": [{
            "documentpath": "https://citz-foi-prod.objectstore.gov.bc.ca/dev-forms-foirequests/CITZ/CITZ-2022-236861/extension/12e4dad1-71b7-4c2d-a770-c16937ecc052.docx",
            "filename": "CITZExtensionDenied.docx", 
            "category": "extension"
        }] 
    }
    foirequestid = str(foijsondata["id"])
    ministryid = str(foijsondata["ministryRequests"][0]["id"])
    extensionid = str(getextensionssresponsejsondata[0]['foirequestextensionid'])    
    foiministryextnresponse = client.post(CREATE_EXTN_BASE_URL+foirequestid+'/ministryrequest/'+ministryid+'/extension/'+extensionid+'/edit',data=json.dumps(extensionschema), headers=factory_intake_auth_header(app, client), content_type=CONTENT_TYPE)
    assert rawresponse.status_code == 200 and foiresponse.status_code == 200 and wfupdateresponse.status_code == 200 and createextnresponse.status_code == 200 and foiministryextnresponse.status_code == 200


def test_foiministryextension_delete(app, client):
    rawresponse = client.post(RAW_REQUEST_POST_URL,data=json.dumps(rawrequestjson), headers=factory_intake_auth_header(app, client), content_type=CONTENT_TYPE)
    jsondata = json.loads(rawresponse.data)    
    foirequest = generalrequestjson
    foirequest["id"] = str(jsondata["id"])
    foirequest["requeststatusid"] = 1
    foiresponse = client.post(REQUEST_POST_URL,data=json.dumps(foirequest), headers=factory_intake_auth_header(app, client), content_type=CONTENT_TYPE)
    foijsondata = json.loads(foiresponse.data)    
    wfinstanceid={"wfinstanceid":str(uuid.uuid4())}
    wfupdateresponse = client.put(WF_URL_BASE+str(jsondata["id"]),data=json.dumps(wfinstanceid), headers=factory_intake_auth_header(app, client), content_type=CONTENT_TYPE)
    
    createextnresponse = client.post(CREATE_EXTN_BASE_URL+str(foijsondata["id"])+'/ministryrequest/'+str(foijsondata["ministryRequests"][0]["id"]),data=json.dumps(NEW_EXTENSION_SCHEMA), headers=factory_intake_auth_header(app, client), content_type=CONTENT_TYPE)   
    getextensionssresponse = client.get(GET_EXTN_BASE_URL+str(foijsondata["ministryRequests"][0]["id"]), headers=factory_ministry_auth_header(app, client), content_type=CONTENT_TYPE)
    getextensionssresponsejsondata = json.loads(getextensionssresponse.data)    
    foirequestid = str(foijsondata["id"])
    ministryid = str(foijsondata["ministryRequests"][0]["id"])
    extensionid = str(getextensionssresponsejsondata[0]['foirequestextensionid'])
    foiministryextnresponse = client.post(CREATE_EXTN_BASE_URL+foirequestid+'/ministryrequest/'+ministryid+'/extension/'+extensionid+'/delete', headers=factory_intake_auth_header(app, client), content_type=CONTENT_TYPE)
    assert rawresponse.status_code == 200 and foiresponse.status_code == 200 and wfupdateresponse.status_code == 200 and createextnresponse.status_code == 200 and foiministryextnresponse.status_code == 200

