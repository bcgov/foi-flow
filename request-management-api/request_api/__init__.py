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
from flask import Flask
from sbc_common_components.exception_handling.exception_handler import ExceptionHandler  # noqa: I001

import request_api.config as config
from request_api.config import _Config

from request_api.models import db, ma
from request_api.utils.util_logging import setup_logging, setup_filelogging
from request_api.auth import jwt
from flask_cors import CORS
import re
from flask_caching import Cache
from flask_socketio import SocketIO

app = Flask(__name__)
#Cache Initialization
app.config.from_object('request_api.utils.cache.Config') 
cache = Cache(app) 

SOCKETIO_PING_TIMEOUT = int(os.getenv('SOCKETIO_PING_TIMEOUT', 5))
SOCKETIO_PING_INTERVAL = int(os.getenv('SOCKETIO_PING_INTERVAL', 25))
SOCKETIO_LOG_LEVEL = bool(os.getenv('SOCKETIO_LOG_LEVEL', False))
ENGINEIO_LOG_LEVEL = bool(os.getenv('ENGINEIO_LOG_LEVEL', False))
SOCKETIO_CORS_ORIGIN= os.getenv('CORS_ORIGIN').split(",")

socketio = SocketIO(logger=SOCKETIO_LOG_LEVEL, engineio_logger=ENGINEIO_LOG_LEVEL,ping_timeout=SOCKETIO_PING_TIMEOUT,ping_interval=SOCKETIO_PING_INTERVAL,cors_allowed_origins=SOCKETIO_CORS_ORIGIN)

def create_app(run_mode=os.getenv('FLASK_ENV', 'development')):
    """Return a configured Flask App using the Factory method."""   
 
    app.config.from_object(config.CONFIGURATION[run_mode])

    from request_api.resources import API_BLUEPRINT #, DEFAULT_API_BLUEPRINT #, OPS_BLUEPRINT  # pylint: disable=import-outside-toplevel

    print("environment :" + run_mode)
    
    CORS(app, supports_credentials=True)
    db.init_app(app)
    ma.init_app(app)

    app.register_blueprint(API_BLUEPRINT)

    if os.getenv('FLASK_ENV', 'production') != 'testing':
        print("JWTSET DONE!!!!!!!!!!!!!!!!")
        setup_jwt_manager(app, jwt)

    ExceptionHandler(app)


    register_shellcontext(app)
    
    return app


def setup_jwt_manager(app, jwt_manager):
    """Use flask app to configure the JWTManager to work for a particular Realm."""

    def get_roles(a_dict):
        return a_dict['groups']  # pragma: no cover

    app.config['JWT_ROLE_CALLBACK'] = get_roles
    
    jwt_manager.init_app(app)



def register_shellcontext(app):
    """Register shell context objects."""

    def shell_context():
        """Shell context objects."""
        return {'app': app, 'jwt': jwt, 'db': db, 'models': models}  # pragma: no cover

    app.shell_context_processor(shell_context)



