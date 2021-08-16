import json
import uuid

def test_ping(app, client):
    response = client.get('/api/healthz')
    assert response.status_code == 200

with open('tests/samplerequestjson/foirequest-general.json') as f:
  generalrequestjson = json.load(f)
def test_post_foirequest_general(app, client):    
    response = client.post('/api/foirequests',data=json.dumps(generalrequestjson), content_type='application/json') 
    jsondata = json.loads(response.data)
    print(str(jsondata["id"]))
    assert response.status_code == 200

with open('tests/samplerequestjson/foirequest-personal.json') as f:
  personalrequestjson = json.load(f)
def test_post_foirequest_personal(app, client):    
    response = client.post('/api/foirequests',data=json.dumps(personalrequestjson), content_type='application/json') 
    jsondata = json.loads(response.data)
    print(str(jsondata["id"]))
    assert response.status_code == 200


def test_get_foirequestqueue(app, client):
   response = client.get('/api/dashboard') 
   jsondata = json.loads(response.data)
   assert response.status_code == 200    