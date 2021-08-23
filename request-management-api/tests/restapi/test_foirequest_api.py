import json
import uuid

def test_ping(app, client):
    response = client.get('/api/healthz')
    assert response.status_code == 200

with open('tests/samplerequestjson/rawrequest.json') as f:
  requestjson = json.load(f)

with open('tests/samplerequestjson/foirequest-general.json') as f:
  generalrequestjson = json.load(f)
def test_post_foirequest_general(app, client):    
    response = client.post('/api/foirequests',data=json.dumps(generalrequestjson), content_type='application/json') 
    jsondata = json.loads(response.data)
    print(str(jsondata["id"]))
    foiRequestId = str(jsondata["id"])
    # Update Workflow ID
    wkIdJsonData = {"wfinstanceId":"328a8914-f166-11eb-99bc-0a580a6161f7"}
    wkUpdateResponse = client.post('/api/foirequests/'+foiRequestId,data=json.dumps(wkIdJsonData), content_type='application/json')
    wkUpdateJsondata = json.loads(wkUpdateResponse.data)
    print(str(wkUpdateJsondata["id"]))
    # Update Ministry Status
    fileNumber = str(jsondata["ministryRequests"][0]["filenumber"])
    statusJsonData = {"selectedMinistries":[{"filenumber":fileNumber, "status":"CFR"}]}
    statusUpdateResponse = client.post('/api/foirequests/'+foiRequestId,data=json.dumps(statusJsonData), content_type='application/json')
    statusUpdateJsondata = json.loads(statusUpdateResponse.data)
    print(str(statusUpdateJsondata["id"]))
    assert response.status_code == 200

with open('tests/samplerequestjson/foirequest-personal.json') as f:
  personalrequestjson = json.load(f)
def test_post_foirequest_personal(app, client):

    response = client.post('/api/foirawrequests',data=json.dumps(requestjson), content_type='application/json') 
    jsondata = json.loads(response.data)
    
    wfinstanceid={"wfinstanceid":str(uuid.uuid4())}
    wfupdateresponse = client.put('/api/foirawrequestbpm/addwfinstanceid/'+str(jsondata["id"]),data=json.dumps(wfinstanceid), content_type='application/json')
    assert response.status_code == 200 and wfupdateresponse.status_code == 200  and len(jsondata) >=1

    personalrequestjson["id"] = str(jsondata["id"])
    openrequestdata = json.dumps(personalrequestjson)

    response = client.post('/api/foirequests',data=openrequestdata, content_type='application/json') 
    jsondata = json.loads(response.data)    
    assert response.status_code == 200


def test_get_foirequestqueue(app, client):
   response = client.get('/api/dashboard') 
   jsondata = json.loads(response.data)
   assert response.status_code == 200    