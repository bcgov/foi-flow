"""Common setup and fixtures for the pytest suite used by this service."""

import os
import re
import sys
from pathlib import Path

# Validate before importing request_api: its configuration is evaluated on import.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from check_test_environment import validate_test_environment

validate_test_environment(os.environ)

import pytest
import requests_mock

from flask_migrate import Migrate, upgrade
from request_api import db as _db

from request_api import create_app, setup_jwt_manager
from sqlalchemy import text
from sqlalchemy.orm import scoped_session, sessionmaker
from request_api.auth import jwt as _jwt
sys.path.insert(0, str(Path(__file__).resolve().parent))
from identity import SyntheticIdentity


@pytest.fixture(scope='session')
def identity():
    return SyntheticIdentity()


@pytest.fixture(scope='session', autouse=True)
def external_http(identity):
    # Unregistered HTTP calls fail locally instead of escaping to real services.
    with requests_mock.Mocker() as transport:
        transport.post(
            'http://oidc:8080/auth/realms/test/protocol/openid-connect/token',
            json=identity.token_response,
        )
        transport.get('http://oidc:8080/auth/admin/realms/test/groups', json=[
            {'id': 'upgrade-intake-group', 'name': 'Intake Team', 'path': '/Intake Team', 'subGroups': []},
            {'id': 'upgrade-ministry-group', 'name': 'AEST Ministry Team', 'path': '/AEST Ministry Team', 'subGroups': []},
        ])
        transport.post(
            re.compile(r'^http://workflow:8080/engine-rest/process-definition/key/[^/]+/start$'),
            json={'id': '00000000-0000-0000-0000-000000000007'},
        )
        transport.post('http://workflow:8080/engine-rest/message', status_code=204)
        transport.get(
            re.compile(r'^http://workflow:8080/engine-rest/process-instance/[^/]+$'),
            json={'id': '00000000-0000-0000-0000-000000000007'},
        )
        yield transport

@pytest.fixture(scope='session')
def app(identity, external_http):
    """Return a session-wide application configured in TEST mode."""
    _app = create_app('testing')
    identity.configure(_app)
    setup_jwt_manager(_app, _jwt)
    return _app


@pytest.fixture(scope='function')
def app_request(app, db):
    """Return a session-wide application configured in TEST mode."""
    return app


@pytest.fixture(scope='session')
def client(app, db):  # pylint: disable=redefined-outer-name
    """Return a session-wide Flask test client."""
    return app.test_client()

@pytest.fixture(scope='session')
def jwt(app):
    """Return a session-wide jwt manager."""
    return _jwt

@pytest.fixture(scope='session')
def client_ctx(app, db):  # pylint: disable=redefined-outer-name
    """Return session-wide Flask test client."""
    with app.test_client() as _client:
        yield _client


@pytest.fixture(scope='session')
def db(app):  # pylint: disable=redefined-outer-name, invalid-name
    """Return a session-wide initialised database.

    Drops schema, and recreate.
    """
    with app.app_context():
        drop_schema_sql = """DROP SCHEMA public CASCADE;
                             CREATE SCHEMA public;
                             GRANT ALL ON SCHEMA public TO postgres;
                             GRANT ALL ON SCHEMA public TO public;
                          """

        sess = _db.session()
        #sess.execute(drop_schema_sql)
        #sess.commit()

        # ############################################
        # There are 2 approaches, an empty database, or the same one that the app will use
        #     create the tables
        #     _db.create_all()
        # or
        # Use Alembic to load all of the DB revisions including supporting lookup data
        # This is the path we'll use in auth_api!!

        # even though this isn't referenced directly, it sets up the internal configs that upgrade needs

        Migrate(app, _db)
        upgrade()

    return _db


@pytest.fixture(scope='function')
def session(app, db):  # pylint: disable=redefined-outer-name, invalid-name
    """Return a function-scoped session."""
    with app.app_context():
        conn = db.engine.connect()
        txn = conn.begin()

        original_session = db.session
        sess = scoped_session(sessionmaker(bind=conn, join_transaction_mode='create_savepoint'))
        db.session = sess

        sql = text('select 1')
        sess.execute(sql)

        try:
            yield sess
        finally:
            sess.remove()
            db.session = original_session
            if txn.is_active:
                txn.rollback()
            conn.close()
