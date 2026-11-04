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
"""API endpoints for managing a FOI Email Communication"""


from flask import g, request
from flask_restx import Namespace, Resource, cors
from flask_expects_json import expects_json
from request_api.auth import auth
from request_api.auth import auth, AuthHelper
from request_api.tracer import Tracer
from request_api.utils.util import  cors_preflight, allowedorigins
from request_api.exceptions import BusinessException, Error
from request_api.services.userservice import userservice
from request_api.services.userpreferenceservice import userpreferenceservice


import json
from flask_cors import cross_origin

API = Namespace('FOIUser', description='Endpoints for FOI User management')
TRACER = Tracer.get_instance()

@cors_preflight('GET,OPTIONS')
@API.route('/foiuser')
class FOIUser(Resource):
    """Get users"""

       
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def get():      
        try:
            result = userservice().getusers()
            return json.dumps(result), 200
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500


@cors_preflight('GET,PUT,OPTIONS')
@API.route('/foiuser/preferences')
class FOIUserPreferences(Resource):
    """Get or update preferences for the authenticated FOI MOD user."""

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def get():
        try:
            result = userpreferenceservice().getpreferences(
                AuthHelper.getuserid()
            )
            return result, 200
        except ValueError as exception:
            return {
                'status': False,
                'message': str(exception)
            }, 400
        except BusinessException as exception:
            return {
                'status': exception.status_code,
                'message': exception.message
            }, 500

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def put():
        try:
            payload = request.get_json(silent=True)

            if payload is None:
                raise ValueError(
                    "JSON preference payload is required"
                )

            result = userpreferenceservice().savepreferences(
                AuthHelper.getuserid(),
                payload
            )

            return result, 200

        except ValueError as exception:
            return {
                'status': False,
                'message': str(exception)
            }, 400
        except BusinessException as exception:
            return {
                'status': exception.status_code,
                'message': exception.message
            }, 500
@cors_preflight('POST,OPTIONS')
@API.route('/foiuser/refresh')
class FOIUserRefresh(Resource):
    """Refresh users from KC"""

       
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def post():      
        try:
            result = userservice().syncusers()
            responsecode = 200 if result.success == True else 500
            return {'status': result.success, 'message':result.message} , responsecode
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500
        
