import json
import uuid

def test_ping(app, client):
    response = client.get('/api/healthz')
    assert response.status_code == 200

with open('tests/samplerequestjson/rawrequest.json') as f:
  requestjson = json.load(f)
def test_post_foirawrequests(app, client):    
    response = client.post('/api/foirawrequests',data=json.dumps(requestjson), content_type='application/json') 
    jsondata = json.loads(response.data)
    print(str(jsondata["id"]))
    wfinstanceid={"wfinstanceid":str(uuid.uuid4())}
    wfupdateresponse = client.put('/api/foirawrequestbpm/addwfinstanceid/'+str(jsondata["id"]),data=json.dumps(wfinstanceid), content_type='application/json')   
    assert response.status_code == 200 and wfupdateresponse.status_code == 200  and len(jsondata) >=1

def test_get_foirawrequests(app, client):
    response = client.get('/api/foirawrequests')
    jsondata = json.loads(response.data)    
    assert response.status_code == 200 and len(jsondata) >=1

def test_get_programareas(client):    
    response = client.get('api/foiflow/programareas')    
    jsondata = json.loads(response.data)    
    assert response.status_code == 200  and len(jsondata) >=1

def test_get_applicantcategories(client):    
    response = client.get('api/foiflow/applicantcategories')    
    jsondata = json.loads(response.data)    
    assert response.status_code == 200 and len(jsondata) >=1        



