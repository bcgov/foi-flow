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
from request_api.services.applicantcorrespondence.correspondenceemail import correspondenceemailservice

import json
from flask_cors import cross_origin
import request_api
from request_api.utils.cache import cache_filter, response_filter
from request_api.schemas.foiapplicantcorrespondencelog import  FOIApplicantCorrespondenceLogSchema, FOIApplicantCorrespondenceLogUpdateSchema, FOIApplicantCorrespondenceEmailSchema, FOIApplicantCorrespondenceResponseSchema 
from request_api.auth import auth, AuthHelper
from request_api.services.requestservice import requestservice
from request_api.services.cfrfeeservice import cfrfeeservice
from request_api.services.paymentservice import paymentservice
from request_api.services.communicationwrapperservice import communicationwrapperservice

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
@API.route('/foiflow/applicantcorrespondence/<requestid>/<ministryrequestid>/sendpreview')
class FOIFlowApplicantCorrespondence(Resource):
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @auth.hasusertype('iao')
    def post(requestid, ministryrequestid):
        try:
            requestjson = request.get_json()
            applicantcorrespondencelog = FOIApplicantCorrespondenceLogSchema().load(data=requestjson)
            if ministryrequestid == 'None':
                rawrequestid = requestid
            else:
                rawrequestid = requestservice().getrawrequestidbyfoirequestid(requestid)
            result = communicationwrapperservice().send_preview_email(requestid, rawrequestid, ministryrequestid, applicantcorrespondencelog)
            return {'status': result['success'], 'message': result['message']}, 200
        except BusinessException:
            return "Error happened while saving applicant correspondence log", 500

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
            if ministryrequestid == 'None':
                if requestid == 'undefined':
                    return json.dumps([]) , 200
                rawrequestid = requestid
            else:
                rawrequestid = requestservice().getrawrequestidbyfoirequestid(requestid)
            correspondencelogs = applicantcorrespondenceservice().getapplicantcorrespondencelogs(ministryrequestid, rawrequestid)
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
            applicantcorrespondencelog = FOIApplicantCorrespondenceLogSchema().load(data=requestjson)
            if ministryrequestid == 'None':
                rawrequestid = requestid
            else:
                rawrequestid = requestservice().getrawrequestidbyfoirequestid(requestid)
            result = communicationwrapperservice().send_email(requestid, rawrequestid, ministryrequestid, applicantcorrespondencelog)
            return {'status': result['success'], 'message': result['message'], 'id': result['identifier']}, 200
        except BusinessException:
            return "Error happened while saving applicant correspondence log", 500

@cors_preflight('POST,OPTIONS')
@API.route('/foiflow/applicantcorrespondence/update/<requestid>/<ministryrequestid>')
class FOIFlowApplicantCorrespondence(Resource):
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @auth.hasusertype('iao')
    def post(requestid, ministryrequestid): # This endpoint updates associated attachments and emails as well
        try:
            requestjson = request.get_json()
            applicantcorrespondencelogupdate = FOIApplicantCorrespondenceLogUpdateSchema().load(data=requestjson)
            if ministryrequestid == 'None':
                rawrequestid = requestid
            else:
                rawrequestid = requestservice().getrawrequestidbyfoirequestid(requestid)
            if ministryrequestid == 'None' or ministryrequestid is None or ("israwrequest" in applicantcorrespondencelogupdate and applicantcorrespondencelogupdate["israwrequest"]) is True:
                result = applicantcorrespondenceservice().editapplicantcorrespondencelogforrawrequest(rawrequestid, applicantcorrespondencelogupdate, AuthHelper.getuserid())
            else:
                result = applicantcorrespondenceservice().editapplicantcorrespondencelogforministry(ministryrequestid, applicantcorrespondencelogupdate, AuthHelper.getuserid())
            return {'status': result.success, 'message': result.message, 'id': result.identifier}, 200
        except BusinessException:
            return "Error happened while saving applicant correspondence log", 500

@cors_preflight('POST,OPTIONS')
@API.route('/foiflow/applicantcorrespondence/draft/<requestid>/<ministryrequestid>')
class FOIFlowApplicantCorrespondenceDraft(Resource):

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def post(requestid, ministryrequestid):
        try:
            requestjson = request.get_json()
            correspondenceschemaobj = FOIApplicantCorrespondenceLogSchema().load(data=requestjson)
            if ministryrequestid == 'None':
                rawrequestid = requestid
            else:
                rawrequestid = requestservice().getrawrequestidbyfoirequestid(requestid)
            if ministryrequestid != 'None' or "israwrequest" in correspondenceschemaobj and correspondenceschemaobj["israwrequest"] == False:
                result = applicantcorrespondenceservice().saveapplicantcorrespondencelog(rawrequestid, ministryrequestid, correspondenceschemaobj, AuthHelper.getuserid(), True)
            elif ministryrequestid == 'None' or "israwrequest" in correspondenceschemaobj and correspondenceschemaobj["israwrequest"] == True:
                result = applicantcorrespondenceservice().saveapplicantcorrespondencelogforrawrequest(rawrequestid, correspondenceschemaobj, AuthHelper.getuserid(), True)
            if result.success == True:
               return {'status': result.success, 'message':result.message,'id':result.identifier} , 200      
        except BusinessException:
            return "Error happened while saving applicant correspondence log" , 500
        
@cors_preflight('POST,OPTIONS')
@API.route('/foiflow/applicantcorrespondence/draft/edit/<requestid>/<ministryrequestid>')
class FOIFlowApplicantCorrespondenceDraft(Resource):

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def post(requestid, ministryrequestid):
        try:
            requestjson = request.get_json()
            if ministryrequestid == 'None':
                rawrequestid = requestid
            else:
                rawrequestid = requestservice().getrawrequestidbyfoirequestid(requestid)
            applicantcorrespondencelog = FOIApplicantCorrespondenceLogSchema().load(data=requestjson)
            if ministryrequestid == 'None' or "israwrequest" in applicantcorrespondencelog and applicantcorrespondencelog["israwrequest"] == True:
                result = applicantcorrespondenceservice().saveapplicantcorrespondencelogforrawrequest(rawrequestid, applicantcorrespondencelog, AuthHelper.getuserid(), True)
            else:
                result = applicantcorrespondenceservice().saveapplicantcorrespondencelog(rawrequestid, ministryrequestid, applicantcorrespondencelog, AuthHelper.getuserid(), True)
            if result.success == True:
               return {'status': result.success, 'message':result.message,'id':result.identifier} , 200      
        except BusinessException:
            return "Error happened while saving applicant correspondence log" , 500

@cors_preflight('POST,OPTIONS')
@API.route('/foiflow/applicantcorrespondence/draft/delete/<ministryrequestid>/<rawrequestid>/<correspondenceid>')
class FOIFlowApplicantCorrespondenceDraft(Resource):

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def post(ministryrequestid, rawrequestid, correspondenceid):
        try:
            requestjson = request.get_json()
            if ministryrequestid == 'None':
                rawrequestidforrequest = rawrequestid
            else:
                rawrequestidforrequest = requestservice().getrawrequestidbyfoirequestid(rawrequestid)
            if ministryrequestid == 'None' or "israwrequest" in requestjson and requestjson["israwrequest"] == True:
                rawresult = applicantcorrespondenceservice().deleteapplicantcorrespondencelograwrequest(rawrequestidforrequest, correspondenceid, AuthHelper.getuserid())
                return {'status': rawresult.success, 'message':rawresult.message,'id':rawresult.identifier} , 200
            else:
                rawresult = applicantcorrespondenceservice().deleteapplicantcorrespondencelograwrequest(rawrequestidforrequest, correspondenceid, AuthHelper.getuserid())
                ministryresult = applicantcorrespondenceservice().deleteapplicantcorrespondencelogministry(ministryrequestid, correspondenceid, AuthHelper.getuserid())
            if rawresult.success == True and ministryresult.success == True:
               return {'status': ministryresult.success, 'message':ministryresult.message,'id':ministryresult.identifier} , 200      
        except BusinessException:
            return "Error happened while deleting applicant correspondence log" , 500


@cors_preflight('POST,GET, OPTIONS')
@API.route('/foiflow/applicantcorrespondence/email/<ministryrequestid>/<rawrequestid>')
class FOIFlowApplicantCorrespondenceEmail(Resource):

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def post(ministryrequestid, rawrequestid):
        try:
            requestjson = request.get_json()
            if ministryrequestid == 'None':
                rawrequestidforrequest = rawrequestid
            else:
                rawrequestidforrequest = requestservice().getrawrequestidbyfoirequestid(rawrequestid)
            correspondenceemail = FOIApplicantCorrespondenceEmailSchema().load(data=requestjson) 
            result = correspondenceemailservice().savecorrespondenceemail(ministryrequestid, rawrequestidforrequest, correspondenceemail, AuthHelper.getuserid())
            
            return {'status': result.success, 'message':result.message,'id':result.identifier} , 200      
        except BusinessException:
            return "Error happened while saving  applicant correspondence log" , 500 
    
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def get(ministryrequestid, rawrequestid):
        try:
            if ministryrequestid == 'None':
                rawrequestidforrequest = rawrequestid
            else:
                rawrequestidforrequest = requestservice().getrawrequestidbyfoirequestid(rawrequestid)
            correspondenceemails = correspondenceemailservice().getcorrespondenceemails(ministryrequestid, rawrequestidforrequest)
            return json.dumps(correspondenceemails) , 200
        except BusinessException:
            return "Unable to retrieve correspondence emails" , 500    
        
@cors_preflight('POST,OPTIONS')
@API.route('/foiflow/applicantcorrespondence/response/<ministryrequestid>/<rawrequestid>')
class FOIFlowApplicantCorrespondenceResponse(Resource):

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def post(ministryrequestid, rawrequestid):
        try:
            requestjson = request.get_json()
            if ministryrequestid == 'None':
                rawrequestidforrequest = rawrequestid
            else:
                rawrequestidforrequest = requestservice().getrawrequestidbyfoirequestid(rawrequestid)
            correspondenceemail = FOIApplicantCorrespondenceResponseSchema().load(data=requestjson) 
            if ministryrequestid == 'None' or 'israwrequest' in requestjson and requestjson['israwrequest'] == True:
                result = applicantcorrespondenceservice().saveapplicantcorrespondencelogforrawrequest(rawrequestidforrequest, correspondenceemail, AuthHelper.getuserid())
            else:
                result = applicantcorrespondenceservice().saveapplicantcorrespondencelog(rawrequestidforrequest, ministryrequestid, correspondenceemail, AuthHelper.getuserid())
            
            return {'status': result.success, 'message':result.message,'id':result.identifier} , 200      
        except BusinessException:
            return "Error happened while saving  applicant correspondence log" , 500 
        
@cors_preflight('POST,OPTIONS')
@API.route('/foiflow/applicantcorrespondence/response/delete/<ministryrequestid>/<rawrequestid>/<correspondenceid>')
class FOIFlowApplicantCorrespondenceResponse(Resource):

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def post(ministryrequestid, rawrequestid, correspondenceid):
        try:
            requestjson = request.get_json()
            if ministryrequestid == 'None':
                rawrequestidforrequest = rawrequestid
            else:
                rawrequestidforrequest = requestservice().getrawrequestidbyfoirequestid(rawrequestid)
            if ministryrequestid == 'None' or 'israwrequest' in requestjson and requestjson['israwrequest'] == True:
                rawresult = applicantcorrespondenceservice().deleteapplicantcorrespondencelograwrequest(rawrequestidforrequest, correspondenceid, AuthHelper.getuserid())
                return {'status': rawresult.success, 'message':rawresult.message,'id':rawresult.identifier} , 200
            else:
                rawresult = applicantcorrespondenceservice().deleteapplicantcorrespondencelograwrequest(rawrequestidforrequest, correspondenceid, AuthHelper.getuserid())
                ministryresult = applicantcorrespondenceservice().deleteapplicantcorrespondencelogministry(ministryrequestid, correspondenceid, AuthHelper.getuserid())
            if rawresult.success == True and ministryresult.success == True:
               return {'status': ministryresult.success, 'message':ministryresult.message,'id':ministryresult.identifier} , 200   
        except BusinessException:
            return "Error happened while deleting applicant correspondence log" , 500