from request_api.services.programareaservice import programareaservice
from request_api.services.applicantcategoryservice import applicantcategoryservice
from request_api.services.deliverymodeservice import deliverymodeservice
from request_api.services.receivedmodeservice import receivedmodeservice
from request_api.services.keycloakadminservice import KeycloakAdminService

def test_get_programareas(session):
    response = programareaservice.getprogramareas()
    assert response
    # assert the structure is correct by checking for name, description properties in each element
    for item in response:
        assert item['name'] and item['iaocode']


def test_get_applicantcategories(session):
    response = applicantcategoryservice.getapplicantcategories()
    assert response
    # assert the structure is correct by checking for name, description properties in each element
    for item in response:
        assert item['name'] and item['description']

def test_get_receivedmodes(session):
    response = receivedmodeservice.getreceivedmodes()
    assert response
    # assert the structure is correct by checking for name, description properties in each element
    for item in response:
        assert item['name'] and item['description']        

def test_get_deliverymodes(session):
    response = deliverymodeservice.getdeliverymodes()
    assert response
    # assert the structure is correct by checking for name, description properties in each element
    for item in response:
        assert item['name'] and item['description'] 

def test_get_intaketeam(session):
    keycloakadminservice = KeycloakAdminService()
    response = keycloakadminservice.getusers()    
    assert len(response) > 0     
    for item in response:
        assert item['id'] and item['username']
