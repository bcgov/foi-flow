"""Synthetic signed identity fixtures; no shared Keycloak accounts are used."""

import json
import time
from urllib.parse import parse_qs

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat
import jwt


class SyntheticIdentity:
    issuer = 'http://oidc:8080/realms/test'
    audience = 'foi-upgrade-test'
    kid = 'synthetic-test-key'

    def __init__(self):
        self.key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        public = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(self.key.public_key()))
        public.update(kid=self.kid, use='sig', alg='RS256')
        self.jwks = {'keys': [public]}
        self.private_pem = self.key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption())

    def token(self, username='upgrade-intake', **overrides):
        now = int(time.time())
        groups = ['Intake Team'] if username != 'upgrade-ministry' else ['AEST Ministry Team']
        claims = {
            'iss': self.issuer, 'aud': self.audience, 'sub': username,
            'iat': now, 'exp': now + 300, 'preferred_username': username,
            'name': username, 'groups': groups, 'role': 'intake', 'realm_access': {'roles': []},
        }
        claims.update(overrides)
        return jwt.encode(claims, self.key, algorithm='RS256', headers={'kid': self.kid})

    def token_response(self, request, context):
        username = parse_qs(request.text).get('username', ['upgrade-intake'])[0]
        return {'access_token': self.token(username)}

    def configure(self, app):
        app.config.update(
            JWT_OIDC_TEST_MODE=True,
            JWT_OIDC_TEST_ISSUER=self.issuer,
            JWT_OIDC_TEST_AUDIENCE=self.audience,
            JWT_OIDC_TEST_KEYS=self.jwks,
            JWT_OIDC_TEST_PRIVATE_KEY_PEM=self.private_pem,
        )
