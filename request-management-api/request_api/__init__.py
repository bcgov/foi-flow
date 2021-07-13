# Copyright © 2021 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""The Authroization API service.

This module is the API for the Authroization system.
"""

import json
import os
import logging
#import sentry_sdk  # noqa: I001; pylint: disable=ungrouped-imports,wrong-import-order; conflicts with Flake8
from flask import Flask
#from humps.main import camelize
#from sbc_common_components.exception_handling.exception_handler import ExceptionHandler  # noqa: I001
#from sentry_sdk.integrations.flask import FlaskIntegration  # noqa: I001

import request_api.config as config
#from request_api import models
#from request_api.auth import jwt
from request_api.config import _Config
#from request_api.extensions import mail
from request_api.models import db, ma
#from request_api.utils.cache import cache
# from request_api.utils.run_version import get_run_version
#from request_api.utils.util_logging import setup_logging, setup_filelogging

#setup_logging(os.path.join(_Config.PROJECT_ROOT, 'logging.conf'))  # important to do this first


def create_app(run_mode=os.getenv('FLASK_ENV', 'development')):
    """Return a configured Flask App using the Factory method."""   
    app = Flask(__name__)
    app.config.from_object(config.CONFIGURATION[run_mode])
    #app.config['DEBUG'] = True

    # Configure Sentry
    # if app.config.get('SENTRY_DSN', None):
    #     sentry_sdk.init(
    #         dsn=app.config.get('SENTRY_DSN'),
    #         integrations=[FlaskIntegration()]
    #     )

    #from request_api.resources import TEST_BLUEPRINT  # pylint: disable=import-outside-toplevel
    from request_api.resources import API_BLUEPRINT #, DEFAULT_API_BLUEPRINT #, OPS_BLUEPRINT  # pylint: disable=import-outside-toplevel

    print(run_mode)
    db.init_app(app)
    ma.init_app(app)
    #mail.init_app(app)

    app.register_blueprint(API_BLUEPRINT)
    #app.register_blueprint(DEFAULT_API_BLUEPRINT)

    #app.register_blueprint(OPS_BLUEPRINT)

    # if os.getenv('FLASK_ENV', 'production') in ['development', 'testing']:
    #     app.register_blueprint(TEST_BLUEPRINT)

    # if os.getenv('FLASK_ENV', 'production') != 'testing':
    #     setup_jwt_manager(app, jwt)

    #ExceptionHandler(app)

    # @app.after_request
    # def handle_after_request(response):  # pylint: disable=unused-variable
    #     add_version(response)
    #     camelize_json(response)
    #     return response

    # def add_version(response):
    #     version = get_run_version()
    #     response.headers['API'] = f'request_api/{version}'

    # def camelize_json(response):
    #     if response.headers['Content-Type'] == 'application/json':
    #         response.set_data(json.dumps(camelize(json.loads(response.get_data()))))

    register_shellcontext(app)
    
    ###### Added handler to log to a file ######

    #setup_filelogging(app)

    return app


# def setup_jwt_manager(app, jwt_manager):
#     """Use flask app to configure the JWTManager to work for a particular Realm."""

#     def get_roles(a_dict):
#         return a_dict['realm_access']['roles']  # pragma: no cover

#     app.config['JWT_ROLE_CALLBACK'] = get_roles

#     jwt_manager.init_app(app)


def register_shellcontext(app):
    """Register shell context objects."""

    def shell_context():
        """Shell context objects."""
        return {'app': app, 'jwt': jwt, 'db': db, 'models': models}  # pragma: no cover

    app.shell_context_processor(shell_context)



