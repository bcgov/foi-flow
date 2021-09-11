import json
import uuid

def test_ping(app, client):
    response = client.get('/api/healthz')
    assert response.status_code == 200


def test_get_foiactionforgeneralcase1(app, client):
    response = client.get('/api/foiaction/general/unopened')
    jsondata = json.loads(response.data)    
    assert response.status_code == 200 and len(jsondata) >=1

def test_get_foiactionforgeneralcase2(app, client):
    response = client.get('/api/foiaction/general/intakeinprogress')
    jsondata = json.loads(response.data)    
    assert response.status_code == 200 and len(jsondata) >=1
    
def test_get_foiactionforgeneralinvalid(app, client):
    response = client.get('/api/foiaction/invalid/invalid')
    jsondata = json.loads(response.data)    
    assert response.status_code == 400 and len(jsondata) >=1
