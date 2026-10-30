"""Caller boundaries must supply integers while lookup helpers keep returning Rows."""

from unittest.mock import Mock

import pytest
from sqlalchemy import text

from request_api.exceptions import BusinessException
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIRestrictedMinistryRequests import FOIRestrictedMinistryRequest


@pytest.fixture
def version_row(session):
    return session.execute(text('SELECT 3 AS version')).first()


def assert_missing(call):
    with pytest.raises(BusinessException) as caught:
        call()
    assert caught.value.status_code == 404
    assert caught.value.code == 'REQUEST_VERSION_NOT_FOUND'
    assert caught.value.message == 'Request version not found'


@pytest.mark.parametrize('multiple', [False, True])
@pytest.mark.parametrize('restricted', [False, True])
@pytest.mark.parametrize('ids', [[], [101], [101, 102]])
def test_restrictions_use_scalar_versions(monkeypatch, version_row, multiple, restricted, ids):
    from request_api.services.requestservice import requestservice
    monkeypatch.setattr(FOIMinistryRequest, 'getversionforrequest', lambda requestid: version_row)
    effects = []
    monkeypatch.setattr(FOIRestrictedMinistryRequest, 'disablerestrictedrequests',
                        lambda *args: effects.append(('disable', args)))
    def save(requestid, kind, restricted_value, version, user):
        assert type(version) is int
        assert version == 3
        effects.append(('save', (requestid, kind, restricted_value, version, user)))
        return 'saved'
    monkeypatch.setattr(FOIRestrictedMinistryRequest, 'saverestrictedrequest', save)
    service = requestservice()
    if multiple:
        service.createrestrictedrequests([{'id': i} for i in ids], 'ministry', restricted, 'tester')
    else:
        for i in ids:
            assert service.saverestrictedrequest(i, 'ministry', restricted, 'tester') == 'saved'
    assert effects == [effect for i in ids for effect in [
        ('disable', (i, 'ministry', 'tester')), ('save', (i, 'ministry', restricted, 3, 'tester'))]]


@pytest.mark.parametrize('multiple', [False, True])
def test_missing_restriction_version_preflights_all_ministries(monkeypatch, version_row, multiple):
    from request_api.services.requestservice import requestservice
    monkeypatch.setattr(FOIMinistryRequest, 'getversionforrequest',
                        lambda requestid: version_row if requestid == 101 else None)
    disable = Mock()
    save = Mock()
    monkeypatch.setattr(FOIRestrictedMinistryRequest, 'disablerestrictedrequests', disable)
    monkeypatch.setattr(FOIRestrictedMinistryRequest, 'saverestrictedrequest', save)
    service = requestservice()
    if multiple:
        call = lambda: service.createrestrictedrequests([{'id': 101}, {'id': 102}], 'ministry', True, 'tester')
    else:
        call = lambda: service.saverestrictedrequest(102, 'ministry', True, 'tester')
    assert_missing(call)
    disable.assert_not_called()
    save.assert_not_called()


@pytest.fixture
def ministry(session):
    from datetime import datetime
    ministry = FOIMinistryRequest(version=3, filenumber='TEST-4901', description='Synthetic',
        duedate=datetime(2026, 12, 1), requeststatuslabel='Open', isconsultflag=False)
    session.add(ministry)
    session.commit()
    return ministry


@pytest.mark.parametrize('existing', [False, True])
@pytest.mark.parametrize('restricted', [False, True])
def test_restrictions_persist_integer_version(session, ministry, existing, restricted):
    from request_api.services.requestservice import requestservice
    requestid = ministry.foiministryrequestid
    if existing:
        FOIRestrictedMinistryRequest.saverestrictedrequest(requestid, 'iao', True, 3, 'tester')
    assert requestservice().saverestrictedrequest(requestid, 'iao', restricted, 'tester').success
    session.expire_all()
    rows = session.query(FOIRestrictedMinistryRequest).filter_by(ministryrequestid=requestid).all()
    assert len(rows) == (2 if existing else 1)
    active = [r for r in rows if r.isactive]
    assert len(active) == 1
    assert active[0].version == 3
    assert type(active[0].version) is int
    assert active[0].isrestricted is restricted


def test_replacement_failure_keeps_committed_disable_and_session_reusable(app, db):
    """Use actual commits, without the session fixture's outer rollback."""
    from request_api.services.requestservice import requestservice
    from datetime import datetime
    from sqlalchemy.exc import IntegrityError
    with app.app_context():
        ministry = FOIMinistryRequest(version=3, filenumber='TEST-4901-commits', description='Synthetic',
            duedate=datetime(2026, 12, 1), requeststatuslabel='Open', isconsultflag=False)
        db.session.add(ministry)
        db.session.commit()
        requestid = ministry.foiministryrequestid
        try:
            FOIRestrictedMinistryRequest.saverestrictedrequest(requestid, 'iao', True, 3, 'tester')
            # NULL createdby forces the replacement INSERT to fail after disable commits.
            with pytest.raises(IntegrityError):
                requestservice().saverestrictedrequest(requestid, 'iao', False, None)
            db.session.rollback()
            assert db.session.execute(text('SELECT 1')).scalar_one() == 1
            rows = db.session.query(FOIRestrictedMinistryRequest).filter_by(ministryrequestid=requestid).all()
            assert len(rows) == 1
            assert rows[0].isactive is False
        finally:
            db.session.rollback()
            db.session.query(FOIRestrictedMinistryRequest).filter_by(ministryrequestid=requestid).delete()
            db.session.query(FOIMinistryRequest).filter_by(foiministryrequestid=requestid).delete()
            db.session.commit()


FEE_CASES = ['payment-create', 'payment-version', 'payment-cancel', 'cfr-create', 'cfr-sanction', 'cfr-pay']


@pytest.mark.parametrize('case', FEE_CASES)
@pytest.mark.parametrize('missing', [False, True])
def test_fee_save_boundaries(monkeypatch, version_row, case, missing):
    from request_api.models.FOIRequestPayments import FOIRequestPayment
    from request_api.models.FOIRequestCFRFees import FOIRequestCFRFee
    from request_api.services.paymentservice import paymentservice
    from request_api.services.cfrfeeservice import cfrfeeservice
    monkeypatch.setattr(FOIMinistryRequest, 'getversionforrequest', lambda *a, **kw: None if missing else version_row)
    monkeypatch.setattr(FOIRequestPayment, 'getpayment', lambda *a: {
        'version': 7, 'paymentid': 11, 'paymenturl': 'https://example.invalid/pay',
        'paymentexpirydate': '2026-12-01'})
    monkeypatch.setattr(cfrfeeservice, 'getcfrfee', lambda *a: {
        'version': 7, 'cfrfeeid': 12, 'feedata': {'amountpaid': '0.00', 'balanceremaining': 20}})
    saved = []
    def save(obj, *args):
        assert type(obj.ministryrequestversion) is int
        assert obj.ministryrequestversion == 3
        assert obj.version == (1 if case == 'cfr-create' else 8)
        saved.append(obj)
        return 'saved'
    monkeypatch.setattr(FOIRequestPayment, 'savepayment', save)
    monkeypatch.setattr(FOIRequestCFRFee, 'createcfrfee', save)
    operations = {
        'payment-create': lambda: paymentservice().createpayment(201, 101, {'paymentExpiryDate': '2026-12-01'}),
        'payment-version': lambda: paymentservice().createpaymentversion(201, 101, 10),
        'payment-cancel': lambda: paymentservice().cancelpayment(201, 101, {'paymenturl': None}),
        'cfr-create': lambda: cfrfeeservice().createcfrfee(101, {'feedata': {}}, 'tester'),
        'cfr-sanction': lambda: cfrfeeservice().sanctioncfrfee(101, {'feedata': {}}, 'tester'),
        'cfr-pay': lambda: cfrfeeservice().paycfrfee(101, 5),
    }
    if missing:
        assert_missing(operations[case])
        assert saved == []
    else:
        assert operations[case]() == 'saved'
        assert len(saved) == 1
        if case == 'payment-version':
            assert saved[0].paidamount == 10
        if case == 'payment-cancel':
            assert saved[0].createdby == 'System_Cancel'
        if case == 'cfr-pay':
            assert saved[0].feedata['amountpaid'] == '5.00'


COMMENT_CASES = ['createministryrequestcomment', 'createrawrequestcomment',
                 'createRequestHistorycomments', 'createMinistryRequestHistorycomments']


@pytest.mark.parametrize('method', COMMENT_CASES)
@pytest.mark.parametrize('missing', [False, True])
def test_comment_save_boundaries(monkeypatch, version_row, method, missing):
    from request_api.models.FOIRawRequests import FOIRawRequest
    from request_api.models.FOIRequestComments import FOIRequestComment
    from request_api.models.FOIRawRequestComments import FOIRawRequestComment
    from request_api.services.commentservice import commentservice
    expected_lookup = FOIRawRequest if method in (
        'createrawrequestcomment', 'createRequestHistorycomments') else FOIMinistryRequest
    other_lookup = FOIMinistryRequest if expected_lookup is FOIRawRequest else FOIRawRequest
    monkeypatch.setattr(expected_lookup, 'getversionforrequest', lambda *a: None if missing else version_row)
    monkeypatch.setattr(other_lookup, 'getversionforrequest', lambda *a: pytest.fail('Changed lookup choice'))
    saved = []
    def save(kind, data, version, user):
        assert type(version) is int
        assert version == 3
        assert data['comment'] == 'Synthetic comment'
        assert kind == 9
        saved.append(data)
        return 'saved'
    monkeypatch.setattr(FOIRequestComment, 'savecomment', save)
    monkeypatch.setattr(FOIRawRequestComment, 'savecomment', save)
    call = lambda: getattr(commentservice(), method)(
        {'requestid': 101, 'ministryrequestid': 102, 'comment': 'Synthetic comment'}, 'tester', 9)
    if missing:
        assert_missing(call)
        assert saved == []
    else:
        assert call() == 'saved'
        assert len(saved) == 1


@pytest.mark.parametrize('raw', [False, True])
@pytest.mark.parametrize('grouped', [False, True])
@pytest.mark.parametrize('missing', [False, True])
def test_watcher_save_boundaries(monkeypatch, version_row, raw, grouped, missing):
    from request_api.models.FOIRawRequests import FOIRawRequest
    from request_api.models.FOIRequestWatchers import FOIRequestWatcher
    from request_api.models.FOIRawRequestWatchers import FOIRawRequestWatcher
    from request_api.services.watcherservice import watcherservice
    model = FOIRawRequestWatcher if raw else FOIRequestWatcher
    lookup = FOIRawRequest if raw else FOIMinistryRequest
    monkeypatch.setattr(lookup, 'getversionforrequest', lambda *a: None if missing else version_row)
    saved = []
    def save(data, version, user, *groups):
        assert type(version) is int
        assert version == 3
        assert groups == ((['Intake Team'],) if grouped else ())
        saved.append(data.copy())
        return 'saved'
    monkeypatch.setattr(model, 'savewatcher', save)
    monkeypatch.setattr(model, 'savewatcherbygroups', save)
    data = {'requestid': 101, 'ministryrequestid': 102, 'watchedby': 'tester', 'isactive': True}
    if not grouped:
        data['watchedbygroup'] = 'Intake Team'
    method = 'createrawrequestwatcher' if raw else 'createministryrequestwatcher'
    call = lambda: getattr(watcherservice(), method)(data, 'tester', ['Intake Team', 'formsflow-user'])
    if missing:
        assert_missing(call)
        assert saved == []
        assert 'watchedbygroup' not in data if grouped else data['watchedbygroup'] == 'Intake Team'
    else:
        assert call() == 'saved'
        assert len(saved) == 1


@pytest.mark.parametrize('raw', [False, True])
@pytest.mark.parametrize('missing', [False, True])
def test_correspondence_email_save_boundaries(monkeypatch, version_row, raw, missing):
    from request_api.models.FOIRawRequests import FOIRawRequest
    from request_api.models.FOICorrespondenceEmails import FOICorrespondenceEmail
    from request_api.models.FOICorrespondenceEmailsRawRequests import FOICorrespondenceEmailRawRequest
    from request_api.services.applicantcorrespondence.correspondenceemail import correspondenceemailservice
    lookup = FOIRawRequest if raw else FOIMinistryRequest
    model = FOICorrespondenceEmailRawRequest if raw else FOICorrespondenceEmail
    monkeypatch.setattr(lookup, 'getversionforrequest', lambda **kw: None if missing else version_row)
    saved = []
    def save(obj):
        version = obj.foirawrequestversion_id if raw else obj.foiministryrequestversion_id
        assert type(version) is int
        assert version == 3
        assert obj.email == 'history@example.invalid'
        saved.append(obj)
        return 'saved'
    monkeypatch.setattr(model, 'savecorrespondenceemail', save)
    call = lambda: correspondenceemailservice().savecorrespondenceemail(
        101, 102 if raw else 'None', {'email': 'history@example.invalid'}, 'tester')
    if missing:
        assert_missing(call)
        assert saved == []
    else:
        assert call() == 'saved'
        assert len(saved) == 1


@pytest.mark.parametrize('raw', [False, True])
@pytest.mark.parametrize('edit', [False, True])
@pytest.mark.parametrize('draft', [False, True])
@pytest.mark.parametrize('missing', [False, True])
def test_correspondence_log_save_boundaries(monkeypatch, version_row, raw, edit, draft, missing):
    from request_api.models.FOIRawRequests import FOIRawRequest
    from request_api.models.FOIApplicantCorrespondences import FOIApplicantCorrespondence
    from request_api.models.FOIApplicantCorrespondencesRawRequests import FOIApplicantCorrespondenceRawRequest
    from request_api.models.default_method_result import DefaultMethodResult
    from request_api.services.applicantcorrespondence.applicantcorrespondencelog import applicantcorrespondenceservice
    lookup = FOIRawRequest if raw else FOIMinistryRequest
    model = FOIApplicantCorrespondenceRawRequest if raw else FOIApplicantCorrespondence
    monkeypatch.setattr(lookup, 'getversionforrequest', lambda **kw: None if missing else version_row)
    monkeypatch.setattr(model, 'getapplicantcorrespondencebyid', lambda *a: {
        'applicantcorrespondenceid': 11, 'version': 7, 'isdraft': True,
        'correspondencemessagejson': '{}', 'sentcorrespondencemessage': None})
    updates = []
    suffix = 'rawrequest' if raw else 'ministryrequest'
    for part in ['attachments', 'emails']:
        monkeypatch.setattr(applicantcorrespondenceservice,
            '_applicantcorrespondenceservice__update' + part + 'version' + suffix,
            lambda self, *a: updates.append(a))
    data = {'correspondenceid': 11, 'correspondencemessagejson': '{"subject":"Synthetic"}',
            'attachments': [], 'emails': [] if draft else ['history@example.invalid'],
            'ccemails': [], 'isdraft': draft}
    saved = []
    def save(obj, *args):
        version = obj.foirawrequestversion_id if raw else obj.foiministryrequestversion_id
        assert type(version) is int
        assert version == 3
        assert obj.version == 8
        assert obj.isdraft is draft
        assert obj.correspondencemessagejson == '{"subject":"Synthetic"}'
        if not edit:
            assert args == ([], data['emails'], [])
        if not draft:
            assert obj.sentby == 'tester'
        saved.append(obj)
        return DefaultMethodResult(True, 'saved', 11)
    monkeypatch.setattr(model, 'saveapplicantcorrespondence', save)
    service = applicantcorrespondenceservice()
    if edit:
        method = service.editapplicantcorrespondencelogforrawrequest if raw else service.editapplicantcorrespondencelogforministry
        call = lambda: method(101, data, 'tester')
    elif raw:
        call = lambda: service.saveapplicantcorrespondencelogforrawrequest(101, data, 'tester', draft)
    else:
        call = lambda: service.saveapplicantcorrespondencelog(201, 101, data, 'tester', draft)
    if missing:
        assert_missing(call)
        assert saved == []
        assert updates == []
    else:
        assert call().success
        assert len(saved) == 1
        assert len(updates) == (2 if edit else 0)
        if edit:
            assert all(args[0] == 101 for args in updates)


@pytest.fixture
def raw_request(session):
    from request_api.models.FOIRawRequests import FOIRawRequest
    result = FOIRawRequest.saverawrequest({'requestType': 'general', 'description': 'Synthetic'},
        'online', False, 'tester', None, False, None, None, [])
    return result.identifier


@pytest.mark.parametrize('matching_ministry', [False, True])
def test_raw_history_comment_uses_raw_version(session, raw_request, matching_ministry):
    from datetime import datetime
    from request_api.models.FOIRawRequestComments import FOIRawRequestComment
    from request_api.services.commentservice import commentservice

    assert FOIMinistryRequest.getversionforrequest(raw_request) is None
    if matching_ministry:
        session.add(FOIMinistryRequest(
            foiministryrequestid=raw_request, version=7, filenumber='TEST-HISTORY',
            description='Unrelated ministry request', duedate=datetime(2026, 12, 1),
            requeststatuslabel='Open', isconsultflag=False))
        session.flush()

    result = commentservice().createRequestHistorycomments(
        {'requestid': raw_request, 'comment': 'Synthetic history export'}, 'tester')

    assert result.success
    session.expire_all()
    comment = session.query(FOIRawRequestComment).filter_by(commentid=result.identifier).one()
    assert comment.requestid == raw_request
    assert comment.version == 1
    assert comment.commenttypeid == 2
    assert comment.comment == 'Synthetic history export'


def test_payment_cfr_comment_watcher_postgres_saves(session, ministry, raw_request):
    from request_api.models.FOIRequestPayments import FOIRequestPayment
    from request_api.models.FOIRequestCFRFees import FOIRequestCFRFee
    from request_api.models.FOIRequestComments import FOIRequestComment
    from request_api.models.FOIRawRequestComments import FOIRawRequestComment
    from request_api.models.FOIRequestWatchers import FOIRequestWatcher
    from request_api.models.FOIRawRequestWatchers import FOIRawRequestWatcher
    from request_api.services.paymentservice import paymentservice
    from request_api.services.cfrfeeservice import cfrfeeservice
    from request_api.services.commentservice import commentservice
    from request_api.services.watcherservice import watcherservice
    requestid = ministry.foiministryrequestid
    assert paymentservice().createpayment(201, requestid, {'paymentExpiryDate': '2026-12-01'}).success
    assert cfrfeeservice().createcfrfee(requestid, {'feedata': {}}, 'tester').success
    data = {'ministryrequestid': requestid, 'requestid': raw_request, 'comment': 'Synthetic',
            'watchedby': 'tester', 'isactive': True, 'watchedbygroup': 'Intake Team'}
    assert commentservice().createministryrequestcomment(data, 'tester').success
    assert commentservice().createrawrequestcomment(data, 'tester').success
    assert watcherservice().createministryrequestwatcher(data, 'tester', []).success
    assert watcherservice().createrawrequestwatcher(data, 'tester', []).success
    session.expire_all()
    for model in [FOIRequestPayment, FOIRequestCFRFee]:
        obj = session.query(model).filter_by(ministryrequestid=requestid).one()
        assert type(obj.ministryrequestversion) is int
        assert obj.ministryrequestversion == 3
        assert obj.version == 1
    for model in [FOIRequestWatcher, FOIRequestComment]:
        obj = session.query(model).filter_by(ministryrequestid=requestid).one()
        assert obj.version == 3
    for model in [FOIRawRequestWatcher, FOIRawRequestComment]:
        obj = session.query(model).filter_by(requestid=raw_request).one()
        assert obj.version == 1
    assert session.query(FOIRequestComment).filter_by(ministryrequestid=requestid).one().commentsversion == 1


@pytest.mark.parametrize('replace', [False, True])
@pytest.mark.parametrize('missing', [False, True])
def test_record_save_boundaries(monkeypatch, version_row, replace, missing):
    from request_api.models.FOIRequestRecords import FOIRequestRecord
    from request_api.models.default_method_result import DefaultMethodResult
    from request_api.services.recordservice import recordservice
    monkeypatch.setattr(FOIMinistryRequest, 'getversionforrequest', lambda *a: None if missing else version_row)
    monkeypatch.setattr(FOIMinistryRequest, 'getrequestbyministryrequestid', lambda *a: {'foirequest_id': 201})
    monkeypatch.setattr(FOIRequestRecord, 'getrecordbyid', lambda *a: {
        's3uripath': 'test/old.pdf', 'attributes': '{"lastmodified":"2026-10-27"}'})
    external = Mock(return_value=({}, None))
    monkeypatch.setattr(recordservice, 'makedocreviewerrequest', external)
    saved = []
    def save(*args):
        records = args[-1]
        assert len(records) == 1
        assert type(records[0].ministryrequestversion) is int
        assert records[0].ministryrequestversion == 3
        assert records[0].version == 1
        assert records[0].foirequestid == 201
        saved.extend(records)
        # Stop before job/queue work; persistence and preflight are the boundary under test.
        return DefaultMethodResult(False, 'synthetic stop')
    monkeypatch.setattr(FOIRequestRecord, 'replace', save)
    monkeypatch.setattr(FOIRequestRecord, 'bulk_create', save)
    data = {'records': [{'filename': 'test.pdf', 's3uripath': 'test/new.pdf',
                         'attributes': {}, 'replacementof': None}]}
    call = (lambda: recordservice().replace(201, 101, 11, data, 'tester')) if replace else (
        lambda: recordservice().create(201, 101, data, 'tester'))
    if missing:
        assert_missing(call)
        assert saved == []
        external.assert_not_called()
    else:
        call()
        assert len(saved) == 1


@pytest.mark.parametrize('operation', ['oi-create', 'oi-create-unpublished', 'oi-update', 'pd-update'])
@pytest.mark.parametrize('missing', [False, True])
def test_publication_metadata_save_boundaries(monkeypatch, version_row, operation, missing):
    from datetime import datetime
    from types import SimpleNamespace
    from request_api.models.FOIOpenInformationRequests import FOIOpenInformationRequests
    from request_api.models.FOIProactiveDisclosureRequests import FOIProactiveDisclosureRequests
    from request_api.models.default_method_result import DefaultMethodResult
    from request_api.services.openinfoservice import openinfoservice
    from request_api.services.proactivedisclosureservice import proactivedisclosureservice
    monkeypatch.setattr(FOIMinistryRequest, 'getversionforrequest', lambda *a: None if missing else version_row)
    assignment = Mock()
    monkeypatch.setattr(openinfoservice, 'updateopeninfoassignee', assignment)
    monkeypatch.setattr(openinfoservice, 'getcurrentfoiopeninforequest', lambda *a: {'oiassignedto': None})
    saved = []
    def save(self, data, user):
        assert type(data['foiministryrequestversion_id']) is int
        assert data['foiministryrequestversion_id'] == 3
        assert data['foiministryrequest_id'] == 101
        saved.append(data.copy())
        return DefaultMethodResult(False, 'synthetic stop')
    monkeypatch.setattr(FOIOpenInformationRequests, 'createopeninfo', save)
    monkeypatch.setattr(FOIOpenInformationRequests, 'saveopeninfo', save)
    monkeypatch.setattr(FOIProactiveDisclosureRequests, 'savefoiproactiverequest', save)
    if operation.startswith('oi-create'):
        call = lambda: openinfoservice().createopeninforequest(
            {'requestType': 'general', 'selectedMinistries': [{'code': 'AEST'}],
             'closedate': datetime(2026, 10, 27)}, 'tester', SimpleNamespace(foiministryrequestid=101),
            publish=operation == 'oi-create')
    elif operation == 'oi-update':
        call = lambda: openinfoservice().updateopeninforequest({'oiassignedto': 'tester'}, 'tester', 101, {})
    else:
        call = lambda: proactivedisclosureservice().updateproactivedisclosure({}, 'tester', 101)
    if missing:
        assert_missing(call)
        assert saved == []
        assignment.assert_not_called()
    else:
        call()
        assert len(saved) == 1


@pytest.mark.parametrize('changed', [False, True])
@pytest.mark.parametrize('missing', [False, True])
def test_division_event_queries_current_and_previous_scalar_versions(monkeypatch, version_row, changed, missing):
    from request_api.models.FOIMinistryRequestDivisions import FOIMinistryRequestDivision
    from request_api.services.events.division import divisionevent
    monkeypatch.setattr(FOIMinistryRequest, 'getversionforrequest', lambda *a: None if missing else version_row)
    queries = []
    division = {'division.name': 'Synthetic', 'stage.name': 'CFR', 'divisionduedate': None,
                'divisionreceiveddate': None, 'eapproval': None}
    def getdivisions(requestid, version):
        assert type(version) is int
        queries.append(version)
        return [division] if version == 3 and changed else []
    monkeypatch.setattr(FOIMinistryRequestDivision, 'getdivisions', getdivisions)
    comments = Mock()
    monkeypatch.setattr(divisionevent, 'createcomment', comments)
    call = lambda: divisionevent().createdivisionevent(101, 'ministryrequest', 'tester')
    if missing:
        assert_missing(call)
        assert queries == []
        comments.assert_not_called()
    else:
        assert call().success
        assert queries == [3, 2]
        assert comments.call_count == int(changed)


@pytest.mark.parametrize('raw', [False, True])
def test_correspondence_postgres_versions(session, ministry, raw_request, raw):
    from request_api.models.FOIApplicantCorrespondences import FOIApplicantCorrespondence
    from request_api.models.FOIApplicantCorrespondencesRawRequests import FOIApplicantCorrespondenceRawRequest
    from request_api.models.FOICorrespondenceEmails import FOICorrespondenceEmail
    from request_api.models.FOICorrespondenceEmailsRawRequests import FOICorrespondenceEmailRawRequest
    from request_api.services.applicantcorrespondence.applicantcorrespondencelog import applicantcorrespondenceservice
    from request_api.services.applicantcorrespondence.correspondenceemail import correspondenceemailservice
    ministryid = ministry.foiministryrequestid
    requestid = raw_request if raw else ministryid
    service = applicantcorrespondenceservice()
    data = {'attachments': [], 'emails': [], 'correspondencemessagejson': '{}'}
    if raw:
        result = service.saveapplicantcorrespondencelogforrawrequest(requestid, data, 'tester', True)
    else:
        result = service.saveapplicantcorrespondencelog(201, requestid, data, 'tester', True)
    assert result.success
    assert correspondenceemailservice().savecorrespondenceemail(
        ministryid, raw_request if raw else 'None', {'email': 'test@example.invalid'}, 'tester').success
    update = {'correspondenceid': result.identifier, 'isdraft': False, 'attachments': []}
    if raw:
        edited = service.editapplicantcorrespondencelogforrawrequest(requestid, update, 'tester')
    else:
        edited = service.editapplicantcorrespondencelogforministry(requestid, update, 'tester')
    assert edited.success
    session.expire_all()
    model = FOIApplicantCorrespondenceRawRequest if raw else FOIApplicantCorrespondence
    email_model = FOICorrespondenceEmailRawRequest if raw else FOICorrespondenceEmail
    key = 'foirawrequest_id' if raw else 'foiministryrequest_id'
    version_key = 'foirawrequestversion_id' if raw else 'foiministryrequestversion_id'
    logs = session.query(model).filter_by(**{key: requestid}).order_by(model.version).all()
    assert [log.version for log in logs] == [1, 2]
    assert [getattr(log, version_key) for log in logs] == ([1, 1] if raw else [3, 3])
    assert logs[-1].isdraft is False
    email = session.query(email_model).filter_by(**{key: requestid}).one()
    assert getattr(email, version_key) == (1 if raw else 3)


@pytest.mark.parametrize('replace', [False, True])
def test_record_postgres_versions(session, ministry, monkeypatch, replace):
    from request_api.models.FOIRequestRecords import FOIRequestRecord
    from request_api.services.recordservice import recordservice
    requestid = ministry.foiministryrequestid
    monkeypatch.setattr(FOIMinistryRequest, 'getrequestbyministryrequestid', lambda *a: {'foirequest_id': 201})
    monkeypatch.setattr(recordservice, 'makedocreviewerrequest',
        lambda self, method, url, data: ({}, None) if url == '/api/document/delete' else (None, 'synthetic stop after persistence'))
    records = {'records': [{'filename': 'new.pdf', 's3uripath': 'test/new.pdf',
        'attributes': {'lastmodified': '2026-10-27'}, 'replacementof': -1}]}
    service = recordservice()
    if replace:
        old = FOIRequestRecord(version=1, foirequestid=201, ministryrequestid=requestid,
            ministryrequestversion=3, filename='old.pdf', s3uripath='test/old.pdf',
            attributes={'lastmodified': '2026-10-27'}, replacementof=-1, isactive=True)
        session.add(old)
        session.commit()
        records['records'][0]['replacementof'] = None
        service.replace(201, requestid, old.recordid, records, 'tester')
    else:
        service.create(201, requestid, records, 'tester')
    session.expire_all()
    record = session.query(FOIRequestRecord).filter_by(ministryrequestid=requestid, s3uripath='test/new.pdf').one()
    assert record.ministryrequestversion == 3
    assert type(record.ministryrequestversion) is int
    assert record.version == 1


def test_publication_metadata_postgres_versions(session, ministry):
    from datetime import datetime
    from request_api.models.FOIOpenInformationRequests import FOIOpenInformationRequests
    from request_api.models.FOIProactiveDisclosureRequests import FOIProactiveDisclosureRequests
    from request_api.services.openinfoservice import openinfoservice
    from request_api.services.proactivedisclosureservice import proactivedisclosureservice
    requestid = ministry.foiministryrequestid
    oi = openinfoservice()
    assert oi.createopeninforequest({'requestType': 'general', 'selectedMinistries': [{'code': 'AEST'}],
        'closedate': datetime(2026, 10, 27)}, 'tester', ministry).success
    # Include oiassignedto to exercise the established assignment branch.
    assert oi.updateopeninforequest(oi.getcurrentfoiopeninforequest(requestid), 'tester', requestid, {}).success
    from request_api.models.ProactiveDisclosureCategories import ProactiveDisclosureCategory
    category = session.query(ProactiveDisclosureCategory).first()
    assert category is not None
    assert proactivedisclosureservice().updateproactivedisclosure(
        {'proactivedisclosurecategoryid': category.proactivedisclosurecategoryid,
         'earliesteligiblepublicationdate': '2026-12-01', 'publicationdate': '2026-12-01'}, 'tester', requestid).success
    session.expire_all()
    for model in [FOIOpenInformationRequests, FOIProactiveDisclosureRequests]:
        rows = session.query(model).filter_by(foiministryrequest_id=requestid).all()
        assert len(rows) == (2 if model is FOIOpenInformationRequests else 1)
        assert all(type(row.foiministryrequestversion_id) is int and row.foiministryrequestversion_id == 3 for row in rows)


def test_lookup_contracts_and_unchanged_scalar_extractors(session, ministry, raw_request):
    from datetime import datetime
    from sqlalchemy.engine import Row
    from request_api.models.FOIRawRequests import FOIRawRequest
    from request_api.services.documentservice import documentservice
    from request_api.services.extensionservice import extensionservice
    from request_api.services.subjectcodeservice import subjectcodeservice
    from request_api.services.events.attachment import attachmentevent
    requestid = ministry.foiministryrequestid
    for version in [1, 2]:
        session.add(FOIMinistryRequest(foiministryrequestid=requestid, version=version,
            filenumber='TEST-4901-old', description='Synthetic', duedate=datetime(2026, 12, 1),
            requeststatuslabel='Open', isconsultflag=False))
        FOIRawRequest.saverawrequestversion({'requestType': 'general'}, raw_request,
            None, None, 'Unopened', False, 'tester', 'Unopened')
    session.commit()
    for model, identifier in [(FOIMinistryRequest, requestid), (FOIRawRequest, raw_request)]:
        row = model.getversionforrequest(identifier)
        assert isinstance(row, Row)
        assert type(row[0]) is int
        assert row[0] == 3
        assert model.getversionforrequest(-4901) is None
    for requesttype, identifier in [('ministryrequest', requestid), ('rawrequest', raw_request)]:
        assert documentservice()._documentservice__getversionforrequest(identifier, requesttype) == 3
        assert attachmentevent()._attachmentevent__getversionforrequest(identifier, requesttype) == 3
    assert extensionservice()._extensionservice__getversionforrequest(requestid) == 3
    assert subjectcodeservice()._subjectcodeservice__getministryversionforrequest(requestid) == 3


def test_extension_event_reads_saved_extension_version_as_scalar(session, ministry, monkeypatch):
    from request_api.models.FOIRequestExtensions import FOIRequestExtension
    from request_api.models.default_method_result import DefaultMethodResult
    from request_api.services.events.extension import extensionevent

    extension = FOIRequestExtension(
        version=1, foiministryrequest_id=ministry.foiministryrequestid,
        foiministryrequestversion_id=3, extensionreasonid=1,
        extensionstatusid=1, extendedduedays=10, createdby='tester',
    )
    session.add(extension)
    session.commit()
    event = extensionevent()
    monkeypatch.setattr(event, '_extensionevent__maintained', lambda *args: None)
    monkeypatch.setattr(event, 'createnotification',
                        lambda *args: DefaultMethodResult(True, 'No notification'))

    result = event.createextensionevent(
        ministry.foiministryrequestid, extension.foirequestextensionid,
        'tester', 'Tester', 'add',
    )

    assert result.success is True
    assert result.identifier == extension.foirequestextensionid


def test_request_builder_keeps_row_extraction(session, ministry, monkeypatch):
    from request_api.services.foirequest.requestservicebuilder import requestservicebuilder
    from request_api.services.foirequest.requestserviceministrybuilder import requestserviceministrybuilder
    monkeypatch.setattr(FOIMinistryRequest, 'getrequest', lambda *a: {'axisrequestid': 'TEST-4901', 'recordspagecount': 0})
    monkeypatch.setattr(requestservicebuilder, 'getvalueof', lambda *a: 1)
    monkeypatch.setattr(requestservicebuilder, 'getprogramareaiaocodebyid', lambda *a: 'AEST')
    # Child builders can write extension comments; keep this compatibility check local.
    for method in ['createfoirequestdocuments', 'createfoirequestextensions', 'createfoirequestdivisionfromobject']:
        monkeypatch.setattr(requestserviceministrybuilder, method, lambda *a: [])
    result = requestservicebuilder().createministry(
        {'requestType': 'general', 'description': 'Synthetic', 'requeststatuslabel': 'Open',
         'axisRequestId': 'TEST-4901', 'dueDate': '2026-12-01', 'isconsultflag': False},
        {'code': 'AEST'}, 1, 'tester', ministryid=ministry.foiministryrequestid)
    assert type(result.version) is int
    assert result.version == 4
