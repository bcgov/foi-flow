from request_api.services.programareaservice import programareaservice
from request_api.services.applicantcategoryservice import applicantcategoryservice

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