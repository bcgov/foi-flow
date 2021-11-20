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
"""API endpoints for managing a FOI Requests resource."""


from flask import g, request
from flask_restx import Namespace, Resource, cors
from flask_expects_json import expects_json
from flask_cors import cross_origin
from request_api.auth import auth
from request_api.tracer import Tracer
from request_api.utils.util import  cors_preflight, allowedOrigins
from request_api.exceptions import BusinessException, Error
from request_api.services.actionservice import actionservice
import json


API = Namespace('FOIAction', description='Endpoints for FOI state management')
TRACER = Tracer.get_instance()

@cors_preflight('GET,OPTIONS')
@API.route('/foiaction/<requestype>/<status>')
class FOIActionByTypeAndStatus(Resource):
    """Resource for managing FOI requests."""

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedOrigins())
    #@auth.require
    def get(requestype, status):
        """ GET Method for capturing FOI request possible states"""
        if requestype is None or status is None:
                return {'status': False, 'message':'Bad Request'}, 400
        if requestype is not None:
            if requestype != "personal" and requestype != "general":
                return {'status': False, 'message':'Bad Request'}, 400  
         
        try:
            result = actionservice().getActionByTypeAndStatus(requestype, status)
            if result is not None:
                return json.loads(result), 200
            else:
                return {'status': False, 'message':'Not Found'}, 404   
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500    
        
        
