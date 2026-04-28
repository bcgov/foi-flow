import logging

from flask import Flask, current_app
from flask_jwt_oidc.exceptions import AuthError
from flask_restx import Api, Namespace, Resource

from request_api import register_auth_error_handler
from request_api.utils.auth_error_handler import auth_error_restx_response


def test_token_expired_auth_error_logs_warning(caplog):
    app = Flask(__name__)
    register_auth_error_handler(app)

    @app.route("/api/test-expired-token")
    def expired_token():
        raise AuthError(
            {"code": "token_expired", "description": "Signature has expired."},
            401,
        )

    with caplog.at_level(logging.WARNING, logger=app.logger.name):
        response = app.test_client().get("/api/test-expired-token")

    assert response.status_code == 401
    assert response.get_json()["code"] == "token_expired"
    assert "JWT token expired for GET /api/test-expired-token" in caplog.text
    assert not [
        record
        for record in caplog.records
        if record.name == app.logger.name and record.levelno >= logging.ERROR
    ]


def test_token_expired_auth_error_logs_warning_from_restx_resource(caplog):
    app = Flask(__name__)
    api = Api(app)
    namespace = Namespace("test")

    @api.errorhandler(AuthError)
    def handle_auth_error(error):
        return auth_error_restx_response(error, current_app.logger)

    @namespace.route("/expired-token")
    class ExpiredToken(Resource):
        def get(self):
            raise AuthError(
                {"code": "token_expired", "description": "Signature has expired."},
                401,
            )

    api.add_namespace(namespace, path="/api")

    with caplog.at_level(logging.WARNING, logger=app.logger.name):
        response = app.test_client().get("/api/expired-token")

    assert response.status_code == 401
    assert response.get_json()["code"] == "token_expired"
    assert "JWT token expired for GET /api/expired-token" in caplog.text
    assert not [
        record
        for record in caplog.records
        if record.name == app.logger.name and record.levelno >= logging.ERROR
    ]
