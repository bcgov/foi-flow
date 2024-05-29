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

import request_api.config as config
from request_api.config import _Config

from request_api.models import db, ma
from request_api.utils.util_logging import configure_logging
from request_api.auth import jwt
from flask_cors import CORS
import re
#from flask_caching import Cache

import secure

app = Flask(__name__)
#Cache Initialization
#app.config.from_object('request_api.utils.cache.Config') 
#cache = Cache(app) 



#Setup log
configure_logging()

# Security Response headers
csp = (
    secure.ContentSecurityPolicy()
    .default_src("'self'")
    .script_src("'self'","'unsafe-inline'")
    .style_src("'self'","'unsafe-inline'")
    .object_src('self')
    .connect_src("'self'","'unsafe-inline'")
)
hsts = secure.StrictTransportSecurity().include_subdomains().preload().max_age(31536000)
referrer = secure.ReferrerPolicy().no_referrer()
cache_value = secure.CacheControl().no_store().max_age(0)
xfo_value = secure.XFrameOptions().deny()
secure_headers = secure.Secure(
    csp=csp,
    hsts=hsts,
    referrer=referrer,
    cache=cache_value,
    xfo=xfo_value
)

@app.after_request
def set_secure_headers(response):
    secure_headers.framework.flask(response)
    response.headers.add('Cross-Origin-Resource-Policy','same-origin')
    response.headers['Cross-Origin-Opener-Policy'] = 'same-origin'
    response.headers['Cross-Origin-Embedder-Policy'] = 'unsafe-none'
    return response

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

    #ExceptionHandler(app)


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



