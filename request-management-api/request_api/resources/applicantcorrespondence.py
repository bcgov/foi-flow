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
from request_api.schemas.foiapplicantcorrespondencelog import  FOIApplicantCorrespondenceSchema, FOIApplicantCorrespondenceEmailSchema, FOIApplicantCorrespondenceResponseSchema, FOIApplicantCorrespondenceEditResponseSchema 
from request_api.auth import auth, AuthHelper
from request_api.services.requestservice import requestservice
from request_api.services.cfrfeeservice import cfrfeeservice
from request_api.services.paymentservice import paymentservice
from request_api.services.communicationwrapperservice import communicationwrapperservice
from request_api.services.communicationemailservice import communicationemailservice

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
            applicantcorrespondencelog = FOIApplicantCorrespondenceSchema().load(data=requestjson) 
            rawrequestid = requestservice().getrawrequestidbyfoirequestid(requestid)
            result = communicationwrapperservice().send_email(rawrequestid, ministryrequestid, applicantcorrespondencelog)
            return {'status': result.success, 'message':result.message,'id':result.identifier} , 200
        except BusinessException:
            return "Error happened while saving  applicant correspondence log" , 500 

    # @staticmethod
    # @TRACER.trace()
    # @cross_origin(origins=allowedorigins())
    # @auth.require
    # @auth.hasusertype('iao')
    # def post(requestid, ministryrequestid):
    #     try:
    #         requestjson = request.get_json()
    #         applicantcorrespondencelog = FOIApplicantCorrespondenceSchema().load(data=requestjson)
    #         rawrequestid = requestservice().getrawrequestidbyfoirequestid(requestid)

    #         # Save correspondence log based on request type
    #         if ministryrequestid == 'None' or ministryrequestid is None or ("israwrequest" in applicantcorrespondencelog and applicantcorrespondencelog["israwrequest"]) is True:
    #             result = applicantcorrespondenceservice().saveapplicantcorrespondencelogforrawrequest(rawrequestid, applicantcorrespondencelog, AuthHelper.getuserid())
    #         else:
    #             result = applicantcorrespondenceservice().saveapplicantcorrespondencelog(requestid, ministryrequestid, applicantcorrespondencelog, AuthHelper.getuserid())

    #         # if cfrfeeservice().getactivepayment(requestid, ministryrequestid) != None:
    #         #     requestservice().postfeeeventtoworkflow(requestid, ministryrequestid, "CANCELLED")

    #         if result.success == True:
    #             # Fee processing logic
    #             isFee = communicationwrapperservice._is_fee_processing(applicantcorrespondencelog["templateid"])
    #             print("isFee", isFee)
    #             if communicationwrapperservice._is_fee_processing(applicantcorrespondencelog["templateid"]) == True:
    #                 if cfrfeeservice().getactivepayment(requestid, ministryrequestid) != None:
    #                     requestservice().postfeeeventtoworkflow(requestid, ministryrequestid, "CANCELLED")
                    
    #                 # Handle payment attributes
    #                 print("_attributes")
    #                 _attributes = applicantcorrespondencelog["attributes"][0] if "attributes" in applicantcorrespondencelog else None
    #                 _paymentexpirydate =  _attributes["paymentExpiryDate"] if _attributes is not None and "paymentExpiryDate" in _attributes else None
    #                 if _paymentexpirydate not in (None, ""):
    #                     paymentservice().createpayment(requestid, ministryrequestid, _attributes, AuthHelper.getuserid())  

    #                 print("success1")
    #                 # Post correspondence event to workflow
    #                 requestservice().postcorrespondenceeventtoworkflow(requestid, ministryrequestid, result.identifier, applicantcorrespondencelog['attributes'], applicantcorrespondencelog['templateid'])
    #                 print("success2")
                
    #             # Send email for non-fee templates with email recipients
    #             else:
    #                 if "emails" in applicantcorrespondencelog and len(applicantcorrespondencelog["emails"]) > 0:
    #                     template = applicantcorrespondenceservice().gettemplatebyid(applicantcorrespondencelog["templateid"])
    #                     return communicationemailservice().send(template, applicantcorrespondencelog)

    #         print("success3")
    #         return {'status': result.success, 'message': result.message, 'id': result.identifier}, 200
    #     except BusinessException:
    #         return "Error happened while saving applicant correspondence log", 500
        
        
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
            correspondenceschemaobj = FOIApplicantCorrespondenceSchema().load(data=requestjson)
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
            rawrequestid = requestservice().getrawrequestidbyfoirequestid(requestid)
            applicantcorrespondencelog = FOIApplicantCorrespondenceSchema().load(data=requestjson) 
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
            rawrequestidfromfoirequest = requestservice().getrawrequestidbyfoirequestid(rawrequestid)
            if ministryrequestid == 'None' or "israwrequest" in requestjson and requestjson["israwrequest"] == True:
                rawresult = applicantcorrespondenceservice().deleteapplicantcorrespondencelograwrequest(rawrequestidfromfoirequest, correspondenceid, AuthHelper.getuserid())
                return {'status': rawresult.success, 'message':rawresult.message,'id':rawresult.identifier} , 200
            else:
                rawresult = applicantcorrespondenceservice().deleteapplicantcorrespondencelograwrequest(rawrequestidfromfoirequest, correspondenceid, AuthHelper.getuserid())
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
            rawrequestidfromfoirequest = requestservice().getrawrequestidbyfoirequestid(rawrequestid)
            correspondenceemail = FOIApplicantCorrespondenceEmailSchema().load(data=requestjson) 
            result = correspondenceemailservice().savecorrespondenceemail(ministryrequestid, rawrequestidfromfoirequest, correspondenceemail, AuthHelper.getuserid())
            
            return {'status': result.success, 'message':result.message,'id':result.identifier} , 200      
        except BusinessException:
            return "Error happened while saving  applicant correspondence log" , 500 
    
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def get(ministryrequestid, rawrequestid):
        try:
            rawrequestidfromfoirequest = requestservice().getrawrequestidbyfoirequestid(rawrequestid)
            correspondenceemails = correspondenceemailservice().getcorrespondenceemails(ministryrequestid, rawrequestidfromfoirequest)
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
            rawrequestidfromfoirequest = requestservice().getrawrequestidbyfoirequestid(rawrequestid)
            correspondenceemail = FOIApplicantCorrespondenceResponseSchema().load(data=requestjson) 
            if ministryrequestid == 'None' or 'israwrequest' in requestjson and requestjson['israwrequest'] == True:
                result = applicantcorrespondenceservice().saveapplicantcorrespondencelogforrawrequest(rawrequestidfromfoirequest, correspondenceemail, AuthHelper.getuserid())
            else:
                result = applicantcorrespondenceservice().saveapplicantcorrespondencelog(rawrequestidfromfoirequest, ministryrequestid, correspondenceemail, AuthHelper.getuserid())
            
            return {'status': result.success, 'message':result.message,'id':result.identifier} , 200      
        except BusinessException:
            return "Error happened while saving  applicant correspondence log" , 500 
        

@cors_preflight('POST,OPTIONS')
@API.route('/foiflow/applicantcorrespondence/response/edit/<ministryrequestid>/<rawrequestid>')
class FOIFlowApplicantCorrespondenceEditResponse(Resource):

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def post(ministryrequestid, rawrequestid):
        try:
            rawrequestidfromfoirequest = requestservice().getrawrequestidbyfoirequestid(rawrequestid)
            requestjson = request.get_json()
            correspondenceemail = FOIApplicantCorrespondenceEditResponseSchema().load(data=requestjson) 
            if ministryrequestid == 'None' or 'israwrequest' in requestjson and requestjson['israwrequest'] == True:
                result = applicantcorrespondenceservice().editapplicantcorrespondencelogforrawrequest(rawrequestidfromfoirequest, correspondenceemail, AuthHelper.getuserid())
            elif ministryrequestid != 'None' or 'israwrequest' in requestjson and requestjson['israwrequest'] == False:
                result = applicantcorrespondenceservice().editapplicantcorrespondencelogforministry(ministryrequestid, correspondenceemail, AuthHelper.getuserid())
            
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
            rawrequestidfromfoirequest = requestservice().getrawrequestidbyfoirequestid(rawrequestid)
            if ministryrequestid == 'None' or 'israwrequest' in requestjson and requestjson['israwrequest'] == True:
                rawresult = applicantcorrespondenceservice().deleteapplicantcorrespondencelograwrequest(rawrequestidfromfoirequest, correspondenceid, AuthHelper.getuserid())
                return {'status': rawresult.success, 'message':rawresult.message,'id':rawresult.identifier} , 200
            else:
                rawresult = applicantcorrespondenceservice().deleteapplicantcorrespondencelograwrequest(rawrequestidfromfoirequest, correspondenceid, AuthHelper.getuserid())
                ministryresult = applicantcorrespondenceservice().deleteapplicantcorrespondencelogministry(ministryrequestid, correspondenceid, AuthHelper.getuserid())
            if rawresult.success == True and ministryresult.success == True:
               return {'status': ministryresult.success, 'message':ministryresult.message,'id':ministryresult.identifier} , 200   
        except BusinessException:
            return "Error happened while deleting applicant correspondence log" , 500