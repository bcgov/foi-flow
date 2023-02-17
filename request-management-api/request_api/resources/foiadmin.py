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
"""API endpoints for managing a FOI admin portal."""

from flask import g, request
from flask_restx import Namespace, Resource, cors
from flask_expects_json import expects_json
from request_api.auth import auth
from request_api.tracer import Tracer
from request_api.utils.util import  cors_preflight, allowedorigins
from request_api.exceptions import BusinessException, Error
from request_api.services.programareaservice import programareaservice
# from request_api.services.programareadivisionservice import programareadivisionservice
import json
from flask_cors import cross_origin
import request_api
from request_api.utils.cache import cache_filter, response_filter

API = Namespace('FOIAdmin', description='Endpoints for FOI admin management')
TRACER = Tracer.get_instance()

"""Custom exception messages
"""
EXCEPTION_MESSAGE_BAD_REQUEST='Bad Request'
EXCEPTION_MESSAGE_NOT_FOUND='Not Found'

@cors_preflight('GET,OPTIONS')
@API.route('/foiadmin/divisions/<requesttype>')
class FOIProgramAreaDivisions(Resource):
    """Retrieves all FOI program area divisions"""

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    #@auth.require
    def get(requesttype):
        return {'status': True, 'message': 'test get divisions'}, 200    

@cors_preflight('POST,OPTIONS')
@API.route('/foiadmin/division/<requesttype>')
class CreateFOIProgramAreaDivision(Resource):
    """Creates FOI program area division"""

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    #@auth.require
    def post(requesttype):
        return {'status': True, 'message': 'test create division'}, 200    


@cors_preflight('PUT,OPTIONS')
@API.route('/foiadmin/division/<requesttype>/<divisionid>')
class UpdateFOIProgramAreaDivision(Resource):
    """Updates FOI program area division"""

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    #@auth.require
    def put(requesttype, divisionid):
        return {'status': True, 'message': 'test update division'}, 200    


@cors_preflight('PUT,OPTIONS')
@API.route('/foiadmin/division/<requesttype>/<divisionid>/disable')
class DisableFOIProgramAreaDivision(Resource):
    """Disables FOI program area division"""
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    #@auth.require
    def put(requesttype, divisionid):
        return {'status': True, 'message': 'test disable division'}, 200    

