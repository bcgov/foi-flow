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
import flask
from flask_restx import Namespace, Resource, cors
from flask_expects_json import expects_json
from request_api.auth import auth, AuthHelper
from request_api.tracer import Tracer
from request_api.utils.util import  cors_preflight, allowedorigins
from request_api.exceptions import BusinessException, Error
from request_api.services.applicantservice import applicantservice
import json
from flask_cors import cross_origin
import request_api
from request_api.utils.cache import cache_filter, response_filter
from request_api.schemas.foiapplicant import FOIRequestApplicantSchema

API = Namespace('FOIAssignee', description='Endpoints for FOI assignee management')
TRACER = Tracer.get_instance()

"""Custom exception messages
"""
EXCEPTION_MESSAGE_BAD_REQUEST='Bad Request'
EXCEPTION_MESSAGE_NOT_FOUND='Not Found'


@cors_preflight('GET,OPTIONS')
@API.route('/foiapplicants/<email>')
class FOIApplicants(Resource):
    """Resource for retriving all FOI assignees."""

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @auth.isiao
    @cors_preflight('GET,OPTIONS')
    def get(email=None):
        if email is None or email == "":
            return {'status': False, 'message':EXCEPTION_MESSAGE_BAD_REQUEST}, 400
        try:
            result = applicantservice().getapplicantbyemail(email)
            if result is not None:
                return json.dumps(result), 200
            else:
                return {'status': False, 'message':EXCEPTION_MESSAGE_NOT_FOUND}, 404   
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500 


@cors_preflight('POST,OPTIONS')
@API.route('/foiapplicants/search')
class EventPagination(Resource):
    """ Retrives the foi request based on the queue type.
    """
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @auth.isiao
    @cors_preflight('POST,OPTIONS')
    def post():
        try:
            requestjson = request.get_json()
            _keywords = requestjson['keywords']

            if _keywords is None or _keywords == "":
                return {'status': False, 'message':EXCEPTION_MESSAGE_BAD_REQUEST}, 400
            else:
                result = applicantservice().searchapplicant(_keywords)                
                if result is not None:
                    return json.dumps(result), 200
                else:
                    return {'status': False, 'message':EXCEPTION_MESSAGE_NOT_FOUND}, 404  
        except BusinessException as exception:
            return {'status': exception.status_code, 'message':exception.message}, 500 


@cors_preflight('POST,OPTIONS')
@API.route('/foiapplicants/save')
class EventPagination(Resource):
    """ Saves applicant info and request specific contact info for all open requests associated to an applicant
    """
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @auth.isiao
    @cors_preflight('POST,OPTIONS')
    def post():
        try:
            applicant = FOIRequestApplicantSchema().load(request.get_json())
            result = applicantservice().saveapplicantinfo(applicant, AuthHelper.getuserid())                
            if result.success:
                return {'status': result.success, 'message':result.message,'id':result.identifier} , 200
            else:
                return {'status': False, 'message':EXCEPTION_MESSAGE_NOT_FOUND}, 404  
        except BusinessException as exception:
            return {'status': exception.status_code, 'message':exception.message}, 500 


@cors_preflight('GET,OPTIONS')
@API.route('/foiapplicants/history/<applicantid>')
class FOIApplicants(Resource):
    """Resource for retriving all FOI assignees."""

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @auth.isiao
    @cors_preflight('GET,OPTIONS')
    def get(applicantid=None):
        if applicantid is None or applicantid == 0:
            return {'status': False, 'message':EXCEPTION_MESSAGE_BAD_REQUEST}, 400
        try:
            result = applicantservice().getapplicanthistory(applicantid)
            if result is not None:
                return json.dumps(result), 200
            else:
                return {'status': False, 'message':EXCEPTION_MESSAGE_NOT_FOUND}, 404
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500


@cors_preflight('GET,OPTIONS')
@API.route('/foiapplicants/requests/<applicantid>')
class FOIApplicants(Resource):
    """Resource for retriving all FOI assignees."""

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @auth.isiao
    @cors_preflight('GET,OPTIONS')
    def get(applicantid=None):
        if applicantid is None or applicantid == 0:
            return {'status': False, 'message':EXCEPTION_MESSAGE_BAD_REQUEST}, 400
        try:
            result = applicantservice().getapplicantrequests(applicantid)
            if result is not None:
                return json.dumps(result), 200
            else:
                return {'status': False, 'message':EXCEPTION_MESSAGE_NOT_FOUND}, 404
        except BusinessException as exception:
            return {'status': exception.status_code, 'message':exception.message}, 500

@cors_preflight('GET,OPTIONS')
@API.route('/foiapplicants/applicantid/<applicantid>')
class FOIApplicants(Resource):
    """Resource for retriving applicant by id"""

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @auth.isiao
    @cors_preflight('GET,OPTIONS')
    def get(applicantid=None):
        if applicantid is None or applicantid == 0:
            return {'status': False, 'message':EXCEPTION_MESSAGE_BAD_REQUEST}, 400
        try:
            result = applicantservice().getapplicantbyid(applicantid)
            if result is not None:
                return json.dumps(result), 200
            else:
                return {'status': False, 'message':EXCEPTION_MESSAGE_NOT_FOUND}, 404
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500