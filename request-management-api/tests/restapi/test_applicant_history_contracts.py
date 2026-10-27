"""Synthetic applicant histories through ORM, service and HTTP boundaries."""

import json
import uuid

import pytest

from request_api.models.FOIRequestApplicants import FOIRequestApplicant


@pytest.fixture
def profiles(session):
    histories = [None, [], [{'axisrequestid': 'TEST-01', 'requeststatus': 'Closed'}],
                 [{'axisrequestid': 'TEST-02', 'requeststatus': 'Closed', 'description': 'Synthetic'}]]
    applicants = []
    for history in histories:
        applicant = FOIRequestApplicant(firstname='HistoryContract', lastname='Synthetic',
            email='history-contract@example.invalid', applicantprofileid=str(uuid.uuid4()),
            request_history=history, is_active=True)
        session.add(applicant)
        applicants.append(applicant)
    session.commit()
    return applicants, histories


@pytest.mark.parametrize('route', ['search', 'email'])
def test_history_search_and_email_preserve_mixed_results(session, client, identity, profiles, route):
    applicants, histories = profiles
    headers = {'Authorization': 'Bearer ' + identity.token()}
    if route == 'search':
        response = client.post('/api/foiapplicants/search',
            json={'keywords': {'email': 'history-contract@example.invalid'}}, headers=headers)
    else:
        response = client.get('/api/foiapplicants/history-contract@example.invalid', headers=headers)
    assert response.status_code == 200
    # These routes return a JSON-encoded list with their existing text content type.
    payload = json.loads(response.data)
    if isinstance(payload, str):
        payload = json.loads(payload)
    assert isinstance(payload, list)
    actual = {int(item['foiRequestApplicantID']): item['requestHistory'] for item in payload}
    assert actual == {a.foirequestapplicantid: h for a, h in zip(applicants, histories)}


def test_profile_retrieval_and_new_version_retain_history(session, profiles):
    applicants, histories = profiles
    for applicant, history in zip(applicants, histories):
        applicant_id = applicant.foirequestapplicantid
        assert FOIRequestApplicant.get_applicant_profile_by_id(applicant_id)['requestHistory'] == history
        assert FOIRequestApplicant.get_latest_applicant_profile_by_id(applicant_id)['requestHistory'] == history
        updated = FOIRequestApplicant(firstname='HistoryContract', lastname='Updated',
            email=applicant.email, applicantprofileid=applicant.applicantprofileid, is_active=True)
        result = FOIRequestApplicant.update_applicant_profile(updated, applicant_id, 'synthetic-user')
        assert result.success
        latest = FOIRequestApplicant.get_latest_applicant_profile_by_id(applicant_id)
        assert latest['requestHistory'] == history
        assert latest['foirequestapplicantid'] == updated.foirequestapplicantid
        found = FOIRequestApplicant.search_applicant_profiles({'email': applicant.email})
        matching = [p for p in found if p['applicantprofileid'] == applicant.applicantprofileid]
        assert len(matching) == 1
        assert matching[0]['foirequestapplicantid'] == updated.foirequestapplicantid


def test_service_builds_supported_historical_arrays(session, profiles):
    from request_api.services.applicantservice import applicantservice
    applicants, histories = profiles
    for applicant, history in zip(applicants, histories):
        requests = applicantservice().getapplicantrequests(applicant.foirequestapplicantid)
        expected = [{'foirequestapplicantid': applicant.foirequestapplicantid,
                     'axisrequestid': h['axisrequestid'], 'requeststatus': h['requeststatus'],
                     'receiveddate': 'Historical Request', 'description': h.get('description')}
                    for h in history or []]
        assert requests == expected


@pytest.mark.parametrize('missing', [False, True])
def test_request_creation_restriction_boundary(session, client, identity, monkeypatch, missing):
    """Keep unrelated request/workflow creation outside this restriction contract."""
    from datetime import datetime
    from request_api.models.FOIMinistryRequests import FOIMinistryRequest
    from request_api.models.FOIRestrictedMinistryRequests import FOIRestrictedMinistryRequest
    from request_api.models.default_method_result import DefaultMethodResult
    from request_api.services.requestservice import requestservice
    from request_api.services.rawrequestservice import rawrequestservice
    from request_api.services.eventservice import eventservice
    ministry = FOIMinistryRequest(version=3, filenumber='TEST-4901-route', description='Synthetic',
        duedate=datetime(2026, 12, 1), requeststatuslabel='Open', isconsultflag=False)
    session.add(ministry)
    session.commit()
    requestid = -4901 if missing else ministry.foiministryrequestid
    monkeypatch.setattr(rawrequestservice, 'saverawrequestversion', lambda *a: DefaultMethodResult(True, 'saved', 201))
    monkeypatch.setattr(requestservice, 'saverequest', lambda *a, **kw:
        DefaultMethodResult(True, 'saved', 201, [{'id': requestid}]))
    for method in ['copywatchers', 'copycomments', 'copydocuments', 'copyapplicationfee', 'postopeneventtoworkflow']:
        monkeypatch.setattr(requestservice, method, lambda *a: None)
    monkeypatch.setattr(eventservice, 'posteventsync', lambda *a: None)
    payload = {'id': 201, 'requestType': 'general', 'description': 'Synthetic', 'category': 'Business',
               'dueDate': '2026-12-01', 'receivedMode': 'Online', 'receivedDateUF': '2026-10-27',
               'requestProcessStart': '2026-10-27', 'isiaorestricted': True}
    response = client.post('/api/foirequests', json=payload,
                           headers={'Authorization': 'Bearer ' + identity.token()})
    if missing:
        assert response.status_code == 500
        assert response.get_json() == {'status': 404, 'message': 'Request version not found'}
        assert session.query(FOIRestrictedMinistryRequest).filter_by(ministryrequestid=ministry.foiministryrequestid).count() == 0
    else:
        assert response.status_code == 200, response.data
        assert response.get_json()['status'] is True
        restriction = session.query(FOIRestrictedMinistryRequest).filter_by(ministryrequestid=requestid).one()
        assert restriction.version == 3
        assert restriction.isrestricted is True
