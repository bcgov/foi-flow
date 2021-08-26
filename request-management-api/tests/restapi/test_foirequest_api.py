import json
import uuid

def test_ping(app, client):
    response = client.get('/api/healthz')
    assert response.status_code == 200

with open('tests/samplerequestjson/rawrequest.json') as x, open('tests/samplerequestjson/foirequest-general.json') as y:
  generalrequestjson = json.load(y)
  rawrequestjson = json.load(x)
def test_post_foirequest_general(app, client):
    rawresponse = client.post('/api/foirawrequests',data=json.dumps(rawrequestjson), content_type='application/json')
    jsondata = json.loads(rawresponse.data)
    getrawresponse = client.get('/api/foirawrequest/'+str(jsondata["id"]), content_type='application/json')
    getrawjsondata = json.loads(getrawresponse.data)
    #assert rawresponse.status_code == 200
    foirequest = generalrequestjson
    foirequest["id"] = str(jsondata["id"])
    foiresponse = client.post('/api/foirequests',data=json.dumps(foirequest), content_type='application/json')
    foijsondata = json.loads(foiresponse.data)
    wfinstanceid={"wfinstanceid":str(uuid.uuid4())}
    wfupdateresponse = client.put('/api/foirawrequestbpm/addwfinstanceid/'+str(foijsondata["id"]),data=json.dumps(wfinstanceid), content_type='application/json')
    assert foiresponse.status_code == 200 and wfupdateresponse.status_code == 200

with open('tests/samplerequestjson/rawrequest.json') as x, open('tests/samplerequestjson/foirequest-personal.json') as y:
  personalrequestjson = json.load(y)
  rawrequestjson = json.load(x)
def test_post_foirequest_personal(app, client):
    rawresponse = client.post('/api/foirawrequests',data=json.dumps(rawrequestjson), content_type='application/json')
    jsondata = json.loads(rawresponse.data)
    getrawresponse = client.get('/api/foirawrequest/'+str(jsondata["id"]), content_type='application/json')
    getrawjsondata = json.loads(getrawresponse.data)
    #assert rawresponse.status_code == 200
    foirequest = personalrequestjson
    foirequest["id"] = str(jsondata["id"])
    foiresponse = client.post('/api/foirequests',data=json.dumps(foirequest), content_type='application/json')
    foijsondata = json.loads(foiresponse.data)
    wfinstanceid={"wfinstanceid":str(uuid.uuid4())}
    wfupdateresponse = client.put('/api/foirawrequestbpm/addwfinstanceid/'+str(foijsondata["id"]),data=json.dumps(wfinstanceid), content_type='application/json')
    assert foiresponse.status_code == 200 and wfupdateresponse.status_code == 200



def test_get_foirequestqueue(app, client):
   response = client.get('/api/dashboard') 
   jsondata = json.loads(response.data)
   assert response.status_code == 401    