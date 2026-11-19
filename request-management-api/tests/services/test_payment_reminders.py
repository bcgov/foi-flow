"""Payment reminders must receive named values from real SQLAlchemy results."""

from datetime import datetime
from unittest.mock import Mock

import pytest

from request_api.models.FOIRawRequests import FOIRawRequest
from request_api.models.NotificationTypes import NotificationType
from request_api.models.default_method_result import DefaultMethodResult
from request_api.services.commentservice import commentservice
from request_api.services.commons.duecalculator import duecalculator
from request_api.services.events.payment import paymentevent
from request_api.services.notificationservice import notificationservice
from request_api.utils.commons.datetimehandler import datetimehandler
from request_api.utils.enums import StateName


REMINDER = (
    '20 business days has passed awaiting payment, '
    'you can consider closing the request as abandoned'
)
STATE_CHANGED_AT = datetime(2026, 10, 20, 14, 30)


def add_request(session, state, updated_at, requestid=None, version=1):
    request = FOIRawRequest(
        version=version, status=state.value, requeststatuslabel=state.name,
        updated_at=updated_at, requestrawdata={},
    )
    if requestid is not None:
        request.requestid = requestid
    session.add(request)
    session.flush()
    return request.requestid


def test_app_fee_owing_requests_return_latest_rows_as_dicts(session):
    first_date = datetime(2026, 10, 1)
    last_date = datetime(2026, 10, 15)
    owing_id = add_request(session, StateName.appfeeowing, last_date)
    reopened_id = add_request(session, StateName.unopened, first_date)
    add_request(session, StateName.appfeeowing, first_date, reopened_id, version=2)
    paid_id = add_request(session, StateName.appfeeowing, first_date)
    add_request(session, StateName.unopened, last_date, paid_id, version=2)
    session.commit()

    requests = FOIRawRequest.getappfeeowingrequests()

    assert isinstance(requests, list)
    assert all(isinstance(request, dict) for request in requests)
    assert requests == [
        {'requestid': reopened_id, 'updated_at': first_date,
         'status': StateName.appfeeowing.value},
        {'requestid': owing_id, 'updated_at': last_date,
         'status': StateName.appfeeowing.value},
    ]


def test_app_fee_owing_requests_return_empty_list(session):
    assert FOIRawRequest.getappfeeowingrequests() == []


@pytest.fixture
def payment_reminder(session, monkeypatch):
    requestid = add_request(session, StateName.appfeeowing, STATE_CHANGED_AT)
    session.commit()
    monkeypatch.setattr(datetimehandler, 'gettoday', lambda self: '2026-11-19')
    elapsed = Mock(return_value=20)
    businessday = Mock(return_value=True)
    monkeypatch.setattr(duecalculator, 'getbusinessdaysbetween', elapsed)
    monkeypatch.setattr(duecalculator, 'isbusinessday', businessday)
    monkeypatch.setattr(NotificationType, 'getnotificationtypeid', Mock(return_value=7))
    comments = Mock(return_value=[])
    create_comment = Mock()
    create_notification = Mock()
    dismiss = Mock()
    monkeypatch.setattr(commentservice, 'getrawrequestcomments', comments)
    monkeypatch.setattr(commentservice, 'createrawrequestcomment', create_comment)
    monkeypatch.setattr(notificationservice, 'createnotification', create_notification)
    monkeypatch.setattr(notificationservice, 'dismissremindernotification', dismiss)
    return requestid, elapsed, businessday, comments, create_comment, create_notification, dismiss


@pytest.mark.parametrize(
    'elapsed_days,is_business_day,existing_comment,expected_reminder',
    [(19, True, False, False), (20, True, False, True),
     (21, True, False, True), (20, False, False, False),
     (20, True, True, True)],
)
def test_payment_reminder_preserves_eligibility_and_comment_deduplication(
    payment_reminder, elapsed_days, is_business_day, existing_comment, expected_reminder,
):
    requestid, elapsed, businessday, comments, create_comment, notify, dismiss = payment_reminder
    elapsed.return_value = elapsed_days
    businessday.return_value = is_business_day
    comments.return_value = [{'text': REMINDER}] if existing_comment else []

    result = paymentevent().createpaymentreminderevent()

    assert result.success is True
    assert result.identifier == '2026-11-19'
    elapsed.assert_called_once_with('2026-10-20')
    dismiss.assert_called_once_with('rawrequest', 'Payment')
    if expected_reminder:
        comments.assert_called_once_with(requestid)
        notify.assert_called_once_with(
            {'message': REMINDER}, requestid, 'rawrequest', 7, 'system',
        )
    else:
        comments.assert_not_called()
        notify.assert_not_called()
    if expected_reminder and not existing_comment:
        create_comment.assert_called_once_with(
            {'comment': REMINDER, 'requestid': requestid}, 'system', 2,
        )
    else:
        create_comment.assert_not_called()


def test_reminder_endpoint_handles_payment_query_rows(payment_reminder, client, identity, monkeypatch):
    from request_api.services import eventservice as events

    # Isolate other reminder types while keeping the real payment query/service path.
    for event in (events.cfrdateevent, events.legislativedateevent, events.divisiondateevent,
                  events.oipcduedateevent, events.section5pendingevent, events.pdpublishdateevent):
        monkeypatch.setattr(
            event, 'createdueevent',
            lambda self: DefaultMethodResult(True, 'No reminders due', '2026-11-19'),
        )

    response = client.post(
        '/api/foinotifications/reminder',
        headers={'Authorization': 'Bearer ' + identity.token()},
    )

    assert response.status_code == 200
    assert response.get_json() == {
        'status': True, 'message': 'Due reminder notifications created', 'id': '2026-11-19',
    }
    requestid, _, _, _, create_comment, notify, _ = payment_reminder
    create_comment.assert_called_once_with(
        {'comment': REMINDER, 'requestid': requestid}, 'system', 2,
    )
    notify.assert_called_once_with(
        {'message': REMINDER}, requestid, 'rawrequest', 7, 'system',
    )
