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

from request_api.tracer import Tracer
from request_api.utils.util import  cors_preflight
from request_api.exceptions import BusinessException, Error
from request_api.services.assigneeservice import assigneeservice
import json


API = Namespace('FOIAssignee', description='Endpoints for FOI assignee management')
TRACER = Tracer.get_instance()

@cors_preflight('GET,OPTIONS')
@API.route('/foiassignees', defaults={'requestype':None, 'status': None})
@API.route('/foiassignees/<requestype>', defaults={'status': None})
@API.route('/foiassignees/<requestype>/<status>')
class FOIAssigneesByTypeAndStatus(Resource):
    """Resource for managing FOI requests."""

    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')  ##todo: This will get replaced with Allowed Origins
    def get(requestype=None, status=None):
        """ POST Method for capturing FOI requests before processing"""
        if requestype is not None:
            if requestype != "personal" and requestype != "general":
                return {'status': False, 'message':'Bad Request'}, 400   
        try:
            result = assigneeservice().getGroupsAndMembersByTypeAndStatus(requestype, status)
            if result is not None:
                return json.dumps(result), 200
            else:
                return {'status': False, 'message':'Not Found'}, 404   
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500    
        
        
@cors_preflight('GET,OPTIONS')
@API.route('/foiassignees/group/<groupName>')
class FOIAssigneesByTypeAndStatus(Resource):
    """Resource for managing FOI requests."""

    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')  ##todo: This will get replaced with Allowed Origins
    def get(groupName):
        """ POST Method for capturing FOI requests before processing"""
        try:
            result = assigneeservice().getMembersByGroupName(groupName)
            if result is not None:
                return json.dumps(result), 200
            else:
                return {'status': False, 'message':'Not Found'}, 404 
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500    