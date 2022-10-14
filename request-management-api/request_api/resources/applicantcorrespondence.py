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
"""API endpoints for managing a FOI Requests Applicant Correpondence logs resource."""


from flask import g, request
from flask_restx import Namespace, Resource, cors
from flask_expects_json import expects_json
from request_api.auth import auth
from request_api.tracer import Tracer
from request_api.utils.util import  cors_preflight, allowedorigins
from request_api.exceptions import BusinessException, Error
from request_api.services.applicantcorrespondence.applicantcorrespondencelog import applicantcorrespondenceservice 
import json
from flask_cors import cross_origin
import request_api
from request_api.utils.cache import cache_filter, response_filter
from request_api.schemas.foiapplicantcorrespondencelog import  FOIApplicantCorrespondenceSchema
from request_api.auth import auth, AuthHelper
from request_api.services.requestservice import requestservice
from request_api.services.cfrfeeservice import cfrfeeservice

API = Namespace('FOIApplicantCorrespondenceLog', description='Endpoints for FOI Applicant Correspondence Log')
TRACER = Tracer.get_instance()

"""Custom exception messages
"""
EXCEPTION_MESSAGE_BAD_REQUEST='Bad Request'
EXCEPTION_MESSAGE_NOT_FOUND='Not Found'


@cors_preflight('GET,OPTIONS')
@API.route('/foiflow/applicantcorrespondence/templates')
class FOIFlowApplicantCorrespondenceTemplates(Resource):

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())      
    @auth.require
    @auth.hasusertype('iao')
    @request_api.cache.cached(
        key_prefix="applicantcorrespondencetemplates",
        unless=cache_filter,
        response_filter=response_filter
        )
    def get():
        try:
            data = applicantcorrespondenceservice().getapplicantcorrespondencetemplates()
            jsondata = json.dumps(data)
            return jsondata , 200
        except BusinessException:
            return "Error happened while accessing  applicant correspondence templates" , 500  

@cors_preflight('POST,OPTIONS')
@API.route('/foiflow/applicantcorrespondence/<requestid>/<ministryrequestid>')
class FOIFlowApplicantCorrespondence(Resource):

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @auth.hasusertype('iao')
    def get(requestid, ministryrequestid):
        try:
            correspondencelogs = applicantcorrespondenceservice().getapplicantcorrespondencelogs(ministryrequestid)
            return json.dumps(correspondencelogs) , 200
        except BusinessException:
            return "Error happened while fetching  applicant correspondence logs" , 500 



    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @auth.hasusertype('iao')
    def post(requestid, ministryrequestid):
        try:
            requestjson = request.get_json()
            applicantcorrespondencelog = FOIApplicantCorrespondenceSchema().load(data=requestjson)           
            result = applicantcorrespondenceservice().saveapplicantcorrespondencelog(applicantcorrespondencelog, ministryrequestid, AuthHelper.getuserid())
            if cfrfeeservice().getactivepayment(requestid, ministryrequestid) != None:
                requestservice().postfeeeventtoworkflow(requestid, ministryrequestid, "CANCELLED")
            requestservice().postcorrespondenceeventtoworkflow(ministryrequestid,  requestid, result.identifier, applicantcorrespondencelog['attributes'], applicantcorrespondencelog['templateid'])
           
            return {'status': result.success, 'message':result.message,'id':result.identifier} , 200      
        except BusinessException:
            return "Error happened while saving  applicant correspondence log" , 500 
   