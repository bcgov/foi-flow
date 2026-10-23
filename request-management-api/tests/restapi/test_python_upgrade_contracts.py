"""Pin representative existing responses without external workflow writes."""

import json
from pathlib import Path

from request_api.models.FOIRawRequests import FOIRawRequest


def test_request_read_preserves_fields_and_nulls(session, client, identity):
    payload = json.loads((Path('tests/samplerequestjson/rawrequest.json')).read_text())['requestData']
    created = FOIRawRequest.saverawrequest(payload, 'online', False, 'upgrade-intake', None,
                                         False, None, None, [])
    response = client.get('/api/foirawrequest/' + str(created.identifier),
                          headers={'Authorization': 'Bearer ' + identity.token()})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['firstName'] == 'UT - UserFirstName'
    assert data['lastName'] == 'UT - UserLastName'
    assert data['requestType'] == 'general'
    assert data['middleName'] is None


def test_invalid_request_id_preserves_validation_response(client, identity):
    response = client.get('/api/foirawrequest/not-an-integer',
                          headers={'Authorization': 'Bearer ' + identity.token()})
    assert response.status_code == 500
    assert response.get_json() == {'status': 500, 'message': 'Invalid Request Id'}
