"""Background tasks must never share the request's db.session (FOIMOD-4901 deadlock)."""
import contextvars
import logging

import eventlet
from flask import current_app, request

from request_api.models.db import db
from request_api.utils.backgroundtask import runinbackground


def test_background_task_gets_its_own_session_and_keeps_request_headers(app):
    seen = {}

    def task(value):
        seen['session'] = db.session()
        seen['app'] = current_app._get_current_object()
        seen['authorization'] = request.headers.get('Authorization')
        seen['value'] = value

    with app.test_request_context(headers={'Authorization': 'Bearer upgrade-token'}):
        requestsession = db.session()
        runinbackground(task, 'payload').wait()

    assert seen['session'] is not requestsession
    assert seen['app'] is app
    assert seen['authorization'] == 'Bearer upgrade-token'
    assert seen['value'] == 'payload'


def test_background_task_runs_without_request_context(app):
    seen = {}

    def task():
        seen['session'] = db.session()

    with app.app_context():
        callersession = db.session()
        runinbackground(task).wait()

    assert seen['session'] is not callersession


def test_background_task_failure_is_logged_not_raised(app, caplog):
    def task():
        raise RuntimeError('event failed')

    with app.test_request_context(), caplog.at_level(logging.ERROR, logger='request_api.utils.backgroundtask'):
        assert runinbackground(task).wait() is None

    assert 'Background task' in caplog.text
    assert 'event failed' in caplog.text


def test_greenlets_in_one_app_context_get_separate_sessions(app):
    # Mirrors the incident: a second greenlet running inside a copy of the request's app context.
    with app.app_context():
        requestsession = db.session()
        othersession = eventlet.spawn(contextvars.copy_context().run, db.session).wait()

    assert othersession is not requestsession
