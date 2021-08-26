import json
import uuid

def test_ping(app, client):
    response = client.get('/api/healthz')
    assert response.status_code == 200


def test_get_foiassigneesforgeneral(app, client):
    response = client.get('/api/foiassignees/general')
    jsondata = json.loads(response.data)    
    assert response.status_code == 200 and len(jsondata) >=1

def test_get_foiassigneesforpersonal(app, client):
    response = client.get('/api/foiassignees/personal')
    jsondata = json.loads(response.data)    
    assert response.status_code == 200 and len(jsondata) >=1
    
def test_get_foiassigneesforinvalid(app, client):
    response = client.get('/api/foiassignees/test')
    jsondata = json.loads(response.data)    
    assert response.status_code == 400 and len(jsondata) >=1


def test_get_foiassigneesforgeneralopen(app, client):
    response = client.get('/api/foiassignees/general/open')
    jsondata = json.loads(response.data)    
    assert response.status_code == 200 and len(jsondata) >=1

def test_get_foiassigneesforpersonalopen(app, client):
    response = client.get('/api/foiassignees/personal/open')
    jsondata = json.loads(response.data)    
    assert response.status_code == 200 and len(jsondata) >=1
    
def test_get_foiassigneesforpersonalinvalidstatus(app, client):
    response = client.get('/api/foiassignees/personal/test')
    jsondata = json.loads(response.data)    
    assert response.status_code == 404

def test_get_foiassigneesforgroup(app, client):
    response = client.get('/api/foiassignees/intaketeam')
    jsondata = json.loads(response.data)    
    assert response.status_code == 200 and len(jsondata) >=1
    
def test_get_foiassigneesforinvalidgroup(app, client):
    response = client.get('/api/foiassignees/test')
    jsondata = json.loads(response.data)    
    assert response.status_code == 404