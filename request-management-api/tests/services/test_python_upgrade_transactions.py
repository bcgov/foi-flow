"""Use real application models to verify ORM transactions and version history."""

from request_api.models.FOIRawRequests import FOIRawRequest
from sqlalchemy import text


def create_request(session):
    result = FOIRawRequest.saverawrequest(
        {'requestType': 'general', 'description': None, 'receivedDate': '2026-10-23'},
        'online', False, 'upgrade-intake', 'synthetic upgrade test', False,
        None, None, [],
    )
    assert result.success
    return result.identifier


def test_request_commit_preserves_json_and_nulls(session):
    requestid = create_request(session)
    record = session.query(FOIRawRequest).filter_by(requestid=requestid, version=1).one()
    assert record.requestrawdata['description'] is None
    assert record.requestrawdata['receivedDate'] == '2026-10-23'
    assert record.updated_at is None
    assert record.createdby == 'upgrade-intake'


def test_nested_rollback_keeps_outer_transaction_usable(session):
    requestid = create_request(session)
    nested = session.begin_nested()
    session.execute(text('UPDATE "FOIRawRequests" SET notes=:note WHERE requestid=:id'),
                    {'note': 'rolled back', 'id': requestid})
    nested.rollback()
    assert session.query(FOIRawRequest).filter_by(requestid=requestid).one().notes == 'synthetic upgrade test'
    assert session.execute(text('SELECT 1')).scalar_one() == 1


def test_request_update_preserves_version_history(session):
    requestid = create_request(session)
    result = FOIRawRequest.saverawrequestversion(
        {'requestType': 'general', 'description': 'second version'},
        requestid, None, None, 'Unopened', False, 'upgrade-intake', 'Unopened',
    )
    assert result.success
    versions = session.query(FOIRawRequest).filter_by(requestid=requestid).order_by(FOIRawRequest.version).all()
    assert [record.version for record in versions] == [1, 2]
    assert versions[0].requestrawdata['description'] is None
    assert versions[1].requestrawdata['description'] == 'second version'


def test_commit_is_rolled_back_between_tests(session):
    # Every prior case committed through production code. Its fixture's outer
    # transaction must still remove those records before the next case.
    assert session.query(FOIRawRequest).filter_by(notes='synthetic upgrade test').count() == 0
