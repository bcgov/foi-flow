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
from request_api.auth import auth
from request_api.tracer import Tracer
from request_api.utils.util import  cors_preflight, allowedorigins
from request_api.exceptions import BusinessException, Error
from request_api.services.assigneeservice import assigneeservice
import json
from flask_cors import cross_origin
import request_api
from request_api.utils.cache import cache_filter, response_filter, keycloak_cache_filter, clear_keycloak_cache

API = Namespace('FOIAssignee', description='Endpoints for FOI assignee management')
TRACER = Tracer.get_instance()

"""Custom exception messages
"""
EXCEPTION_MESSAGE_BAD_REQUEST='Bad Request'
EXCEPTION_MESSAGE_NOT_FOUND='Not Found'


@cors_preflight('GET,OPTIONS')
@API.route('/foiassignees')
class FOIAssignees(Resource):
    """Resource for retriving all FOI assignees."""

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @request_api.cache.cached(
        key_prefix="foiassignees",
        unless=keycloak_cache_filter,
        response_filter=response_filter
        )
    def get(requestype=None, status=None, bcgovcode=None):
        if requestype is not None and (requestype != "personal" and requestype != "general"):
            return {'status': False, 'message':EXCEPTION_MESSAGE_BAD_REQUEST}, 400   
        try:
            result = assigneeservice().getgroupsandmembersbytypeandstatus(requestype, status, bcgovcode)
            if result is not None:
                return json.dumps(result), 200
            else:
                return {'status': False, 'message':EXCEPTION_MESSAGE_NOT_FOUND}, 404   
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500 


@cors_preflight('GET,OPTIONS')
#@API.route('/foiassignees')
@API.route('/foiassignees/<requestype>/<status>')
@API.route('/foiassignees/<requestype>/<status>/<bcgovcode>')
class FOIAssigneesByTypeAndStatus(Resource):
    """Resource for retriving FOI assignees based on status."""

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @request_api.cache.cached(
        unless=cache_filter,
        response_filter=response_filter
        )
    def get(requestype=None, status=None, bcgovcode=None):
        if requestype is not None and (requestype != "personal" and requestype != "general"):
            return {'status': False, 'message':EXCEPTION_MESSAGE_BAD_REQUEST}, 400   
        try:
            result = assigneeservice().getgroupsandmembersbytypeandstatus(requestype, status, bcgovcode)
            if result is not None:
                return json.dumps(result), 200
            else:
                return {'status': False, 'message':EXCEPTION_MESSAGE_NOT_FOUND}, 404   
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500    
        
@cors_preflight('GET,OPTIONS')
@API.route('/foiassignees/group/<groupname>')
class FOIAssigneesByTypeAndStatus(Resource):
    """esource for retriving FOI assignees based on group."""

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @request_api.cache.cached(
        unless=cache_filter,
        response_filter=response_filter
        )
    def get(groupname):
        """ POST Method for capturing FOI requests before processing"""
        try:
            result = assigneeservice().getmembersbygroupname(groupname)
            if result is not None:
                return json.dumps(result), 200
            else:
                return {'status': False, 'message':EXCEPTION_MESSAGE_NOT_FOUND}, 404 
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500    
        

@cors_preflight('GET,OPTIONS')
@API.route('/foiassignees/processingteams/<requestype>')
class FOIAssigneesTeams(Resource):
    """Resource for retriving FOI assignees based on group.
        Response is sent with value defaulting to Fee Estimate state"""

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @request_api.cache.cached(
        unless=cache_filter,
        response_filter=response_filter
        )
    def get(requestype):
        """ POST Method for capturing FOI requests before processing"""
        try:
            if requestype is None:
                return {'status': False, 'message':EXCEPTION_MESSAGE_BAD_REQUEST}, 400   
            if requestype is not None and (requestype != "personal" and requestype != "general"):
                return {'status': False, 'message':EXCEPTION_MESSAGE_BAD_REQUEST}, 400   
            result = assigneeservice().getprocessingteamsbyrequesttype(requestype)
            if result is not None:
                return json.dumps(result), 200
            else:
                return {'status': False, 'message':EXCEPTION_MESSAGE_NOT_FOUND}, 404 
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500    
        
