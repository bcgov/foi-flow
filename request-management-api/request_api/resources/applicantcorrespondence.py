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
from request_api.services.applicantcorrespondencelog import applicantcorrespondenceservice 
import json
from flask_cors import cross_origin
import request_api
from request_api.utils.cache import cache_filter, response_filter
from request_api.schemas.foiapplicantcorrespondencelog import  FOIApplicantCorrespondenceSchema
from request_api.auth import auth, AuthHelper

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
@API.route('/foiflow/applicantcorrespondence/<ministryrequestid>')
class FOIFlowApplicantCorrespondence(Resource):

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def get(ministryrequestid):
        try:
          
            _correpondencelogs = applicantcorrespondenceservice().getapplicantcorrespondencelogs(ministryrequestid)           
            correpondencelogs =[]
            for _correpondencelog in _correpondencelogs:
                attachments = []
                for _attachment in _correpondencelog['attachments']: 
                    attachment = {
                        "applicantcorrespondenceattachmentid" : _attachment.applicantcorrespondenceattachmentid,
                        "attachmentdocumenturipath" : _attachment.attachmentdocumenturipath,
                        "attachmentfilename" : _attachment.attachmentfilename,
                    } 
                    attachments.append(attachment)                     

                correpondencelog ={
                    "applicantcorrespondenceid":_correpondencelog['applicantcorrespondenceid'],
                    "parentapplicantcorrespondenceid":_correpondencelog['parentapplicantcorrespondenceid'],
                    "templateid":_correpondencelog['templateid'],
                    "correspondencemessagejson":_correpondencelog['correspondencemessagejson'],
                    "created_at":_correpondencelog['created_at'],
                    "createdby":_correpondencelog['createdby'],
                    "attachments" : attachments
                } 
                correpondencelogs.append(correpondencelog)                  
            return json.dumps(correpondencelogs) , 200      
        except BusinessException:
            return "Error happened while fetching  applicant correspondence logs" , 500 



    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def post(ministryrequestid):
        try:
           requestjson = request.get_json()
           applicantcorrespondencelog = FOIApplicantCorrespondenceSchema().load(data=requestjson)           
           userid = AuthHelper.getuserid()          
           result = applicantcorrespondenceservice().saveapplicantcorrespondencelog(templateid=applicantcorrespondencelog['templateid'],
           ministryrequestid=ministryrequestid,createdby=userid,messagehtml=applicantcorrespondencelog['correspondencemessagejson'],attachments=applicantcorrespondencelog['attachments']) 
           return {'status': result.success, 'message':result.message,'id':result.identifier} , 200      
        except BusinessException:
            return "Error happened while saving  applicant correspondence log" , 500 
   