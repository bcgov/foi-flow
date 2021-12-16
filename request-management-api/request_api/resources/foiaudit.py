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
"""API endpoints for managing a FOI Audits."""


from flask import g, request
from flask_restx import Namespace, Resource, cors
from flask_expects_json import expects_json
from flask_cors import cross_origin
from request_api.auth import auth
from request_api.tracer import Tracer
from request_api.utils.util import  cors_preflight, getgroupsfromtoken, allowedorigins
from request_api.exceptions import BusinessException, Error
from request_api.services.auditservice import auditservice
import json


API = Namespace('FOIAudit', description='Endpoints for FOI audit management')
TRACER = Tracer.get_instance()

@cors_preflight('GET,OPTIONS')
@API.route('/foiaudit/<type>/<id>/<field>')
@API.route('/foiaudit/<type>/<id>/<field>/summary')
class FOIAuditByField(Resource):
    """Resource for managing audit of FOI data."""

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def get(type, id, field):
        """ GET Method for auditing of FOI request field"""
        
        if (type is None or id is None or field is None) or ((type is not None and type != "rawrequest" and type != "ministryrequest") or (field is not None and field != "description")):
            return {'status': False, 'message':'Bad Request'}, 400

        try:
            isall = False if request.url.endswith('summary') else True      
            result = auditservice().getauditforfield(type, id, field, getgroupsfromtoken(),isall)
            if result is not None:
                return {"audit": result}, 200
            else:
                return {'status': False, 'message':'Not Found'}, 404   
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500    
        

        
