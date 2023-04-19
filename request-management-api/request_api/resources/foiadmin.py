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
from request_api.auth import auth, AuthHelper
from request_api.tracer import Tracer
from request_api.utils.util import  cors_preflight, allowedorigins
from request_api.exceptions import BusinessException, Error
from request_api.services.programareadivisionservice import programareadivisionservice
from request_api.schemas.foiprogramareadivision import FOIProgramAreaDivisionSchema
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
@API.route('/foiadmin/divisions')
class FOIProgramAreaDivisions(Resource):
    """Retrieves all FOI program area divisions"""

    @staticmethod
    @TRACER.trace()
    @auth.require
    @cross_origin(origins=allowedorigins())
    @auth.isfoiadmin()
    def get():
        try:
            result = programareadivisionservice().getallprogramareadivisions()
            return json.dumps(result), 200
        except KeyError as err:
            return {'status': False, 'message':err.messages}, 400        
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500     

@cors_preflight('POST,OPTIONS')
@API.route('/foiadmin/division')
class CreateFOIProgramAreaDivision(Resource):
    """Creates FOI program area division"""

    @staticmethod
    @TRACER.trace()
    @auth.require
    @cross_origin(origins=allowedorigins())
    @auth.isfoiadmin()
    def post():
        try:
            requestjson = request.get_json()
            programareadivisionschema = FOIProgramAreaDivisionSchema().load(requestjson)
            result = programareadivisionservice().createprogramareadivision(programareadivisionschema)
            # if result.success == True:
            #   asyncio.ensure_future();
            return {'status': result.success, 'message':result.message, 'id':result.identifier}, 200 
        except KeyError as err:
            return {'status': False, 'message':err.messages}, 400        
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500             


@cors_preflight('PUT,OPTIONS')
@API.route('/foiadmin/division/<divisionid>')
class UpdateFOIProgramAreaDivision(Resource):
    """Updates FOI program area division"""

    @staticmethod
    @TRACER.trace()
    @auth.require
    @cross_origin(origins=allowedorigins())
    @auth.isfoiadmin()
    def put(divisionid):
        try:
            requestjson = request.get_json()
            programareadivisionschema = FOIProgramAreaDivisionSchema().load(requestjson)
            result = programareadivisionservice().updateprogramareadivision(divisionid, programareadivisionschema, AuthHelper.getuserid())
            # if result.success == True:
            #   asyncio.ensure_future();
            return {'status': result.success, 'message':result.message, 'id':result.identifier}, 200 
        except KeyError as err:
            return {'status': False, 'message':err.messages}, 400        
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500  


@cors_preflight('PUT,OPTIONS')
@API.route('/foiadmin/division/<divisionid>/disable')
class DisableFOIProgramAreaDivision(Resource):
    """Disables FOI program area division"""
    @staticmethod
    @TRACER.trace()
    @auth.require
    @cross_origin(origins=allowedorigins())
    @auth.isfoiadmin()
    def put(divisionid):
        try:
            result = programareadivisionservice().disableprogramareadivision(divisionid, AuthHelper.getuserid())
            # if result.success == True:
            #   asyncio.ensure_future();
            return {'status': result.success, 'message':result.message, 'id':result.identifier}, 200 
        except KeyError as err:
            return {'status': False, 'message':err.messages}, 400        
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500   

