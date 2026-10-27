"""Exercise production auth decorators with signed tokens and local JWKS transport."""

from importlib import import_module
from io import BytesIO
import base64
import hashlib
import hmac
import json

from flask import Flask
from flask_jwt_oidc import JwtManager
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
import jwt
import pytest

from request_api import register_auth_error_handler, setup_jwt_manager


@pytest.fixture
def auth_client(identity, monkeypatch):
    auth_module = import_module('request_api.auth')
    manager_module = import_module('flask_jwt_oidc.jwt_manager')
    manager = JwtManager()
    app = Flask(__name__)
    app.config.update(
        JWT_OIDC_TEST_MODE=False,
        JWT_OIDC_WELL_KNOWN_CONFIG=None,
        JWT_OIDC_JWKS_URI=identity.issuer + '/certs',
        JWT_OIDC_ISSUER=identity.issuer,
        JWT_OIDC_AUDIENCE=identity.audience,
        JWT_OIDC_ALGORITHMS='RS256',
        JWT_OIDC_CACHING_ENABLED=False,
    )

    def fetch_jwks(url, **kwargs):
        assert url == identity.issuer + '/certs'
        return BytesIO(json.dumps(identity.jwks).encode())

    monkeypatch.setattr(manager_module, 'urlopen', fetch_jwks)
    monkeypatch.setattr(auth_module, 'jwt', manager)
    setup_jwt_manager(app, manager)
    register_auth_error_handler(app)

    @app.get('/protected')
    @auth_module.Auth.require
    @auth_module.Auth.ismemberofgroups('Intake Team')
    def protected():
        return {'userid': auth_module.AuthHelper.getuserid()}

    return app.test_client()


def test_valid_signed_token_and_permitted_role(auth_client, identity):
    response = auth_client.get('/protected', headers={'Authorization': 'Bearer ' + identity.token()})
    assert response.status_code == 200
    assert response.get_json() == {'userid': 'upgrade-intake'}


@pytest.mark.parametrize('claims', [
    {'exp': 1}, {'iss': 'http://wrong-issuer'}, {'aud': 'wrong-audience'},
])
def test_expired_wrong_issuer_or_wrong_audience_is_rejected(auth_client, identity, claims):
    response = auth_client.get('/protected', headers={'Authorization': 'Bearer ' + identity.token(**claims)})
    assert response.status_code == 401


def test_wrong_signature_is_rejected(auth_client, identity):
    other = type(identity)()
    response = auth_client.get('/protected', headers={'Authorization': 'Bearer ' + other.token()})
    assert response.status_code == 401


def test_valid_token_without_permitted_role_is_denied(auth_client, identity):
    response = auth_client.get('/protected', headers={'Authorization': 'Bearer ' + identity.token(groups=[])})
    assert response.status_code == 401
    assert response.get_data(as_text=True) == 'Unauthorized'


def test_missing_token_is_rejected(auth_client):
    assert auth_client.get('/protected').status_code == 401


def test_hmac_token_signed_with_public_key_is_rejected(auth_client, identity):
    # Exercise the asymmetric/HMAC confusion advisory against the actual
    # validator. The configured RS256 algorithm must reject HS256 outright.
    public_der = identity.key.public_key().public_bytes(Encoding.DER, PublicFormat.SubjectPublicKeyInfo)
    claims = jwt.decode(identity.token(), options={'verify_signature': False})
    parts = [{'alg': 'HS256', 'typ': 'JWT', 'kid': identity.kid}, claims]
    unsigned = b'.'.join(base64.urlsafe_b64encode(json.dumps(part).encode()).rstrip(b'=') for part in parts)
    signature = hmac.new(public_der, unsigned, hashlib.sha256).digest()
    forged = (unsigned + b'.' + base64.urlsafe_b64encode(signature).rstrip(b'=')).decode()
    response = auth_client.get('/protected', headers={'Authorization': 'Bearer ' + forged})
    assert response.status_code == 401
