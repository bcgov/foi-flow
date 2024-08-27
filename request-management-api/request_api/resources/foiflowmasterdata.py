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

from flask import request
from flask_restx import Namespace, Resource
from flask_cors import cross_origin
from request_api.auth import auth
from request_api.services.external.storageservice import storageservice


from request_api.tracer import Tracer
from request_api.utils.util import  cors_preflight, allowedorigins, getrequiredmemberships
from request_api.exceptions import BusinessException
from request_api.services.applicantcategoryservice import applicantcategoryservice
from request_api.services.programareaservice import programareaservice
from request_api.services.deliverymodeservice import deliverymodeservice
from request_api.services.receivedmodeservice import receivedmodeservice
from request_api.services.divisionstageservice import divisionstageservice
from request_api.services.closereasonservice import closereasonservice
from request_api.schemas.foirequestsformslist import  FOIRequestsFormsList
from request_api.services.extensionreasonservice import extensionreasonservice
from request_api.services.cacheservice import cacheservice
from request_api.services.subjectcodeservice import subjectcodeservice
from request_api.services.oipcservice import oipcservice
from request_api.services.openinfoservice import openinfoservice
import json
import request_api
import requests
from aws_requests_auth.aws_auth import AWSRequestsAuth
import os
import uuid
from request_api.utils.cache import cache_filter, response_filter, clear_cache
from request_api.auth import AuthHelper

import boto3
from botocore.exceptions import ClientError
from botocore.config import Config

API = Namespace('FOI Flow Master Data', description='Endpoints for FOI Flow master data')
TRACER = Tracer.get_instance()

@cors_preflight('GET,OPTIONS')
@API.route('/foiflow/applicantcategories')
class FOIFlowApplicantCategories(Resource):
    """Retrieves all active application categories.
    """
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @request_api.cache.cached(
        key_prefix="applicantcategories",
        unless=cache_filter,
        response_filter=response_filter
        )
    def get():
        try:
            data = applicantcategoryservice().getapplicantcategories()
            jsondata = json.dumps(data)
            return jsondata , 200
        except BusinessException:
            return "Error happened while accessing applicant categories" , 500

@cors_preflight('GET,OPTIONS')
@API.route('/foiflow/programareas')
class FOIFlowProgramAreas(Resource):
    """Retrieves all active program areas.
    """
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @request_api.cache.cached(
        key_prefix="programareas",
        response_filter=response_filter,
        unless=cache_filter
        )
    def get():
        try:
            data = programareaservice().getprogramareas()
            jsondata = json.dumps(data)
            return jsondata , 200
        except BusinessException:
            return "Error happened while accessing program areas" , 500


@cors_preflight('GET,OPTIONS')
@API.route('/foiflow/programareasforuser')
class FOIFlowProgramAreas(Resource):
    """Retrieves all active program areas.
    """
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    #@request_api.cache.cached(key_prefix="programareas")
    def get():
        try:
            usertype = AuthHelper.getusertype()
            if (usertype == "iao"):
                data = programareaservice().getprogramareas()
            elif (usertype == 'ministry'):
                groups = AuthHelper.getministrygroups()
                data = programareaservice().getprogramareasforministryuser(groups)
            else:
                data = None

            jsondata = json.dumps(data)
            return jsondata , 200
        except BusinessException:
            return "Error happened while accessing program areas for user" , 500

@cors_preflight('GET,OPTIONS')
@API.route('/foiflow/deliverymodes')
class FOIFlowDeliveryModes(Resource):
    """Retrieves all active delivery modes.
    """
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @request_api.cache.cached(
        key_prefix="deliverymodes",
        unless=cache_filter,
        response_filter=response_filter
        )
    def get():
        try:
            data = deliverymodeservice().getdeliverymodes()
            jsondata = json.dumps(data)
            return jsondata , 200
        except BusinessException:
            return "Error happened while accessing delivery modes" , 500

@cors_preflight('GET,OPTIONS')
@API.route('/foiflow/receivedmodes')
class FOIFlowReceivedModes(Resource):
    """Retrieves all active received modes.
    """
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @request_api.cache.cached(
        key_prefix="receivedmodes",
        unless=cache_filter,
        response_filter=response_filter
        )
    def get():
        try:
            data = receivedmodeservice().getreceivedmodes()
            jsondata = json.dumps(data)
            return jsondata , 200
        except BusinessException:
            return "Error happened while accessing received modes" , 500

@cors_preflight('GET,OPTIONS')
@API.route('/foiflow/divisions/<bcgovcode>')
@API.route('/foiflow/divisions/<bcgovcode>/<specifictopersonalrequests>/<fetchmode>')
class FOIFlowDivisions(Resource):
    """Retrieves all active divisions for the passed in gov code    .
    """
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @request_api.cache.cached(
        unless=cache_filter,
        response_filter=response_filter
        )
    def get(bcgovcode,specifictopersonalrequests=None, fetchmode = None):
        try:
            data = None                        
            if(specifictopersonalrequests is not None and specifictopersonalrequests.lower() == 'true'):                
                match fetchmode:
                    case 'divisions':
                        data = divisionstageservice().getpersonalspecificdivisionandstages(bcgovcode)
                    case 'sections' | 'personaltag':
                        data = divisionstageservice().getpersonalspecificprogramareasections(bcgovcode)
                    case 'divisionsandsections':
                        data = divisionstageservice().getpersonalspecificdivisionsandsections(bcgovcode)
                    case 'people':
                        data = divisionstageservice().getpersonalspecificpeople(bcgovcode)
                    case 'filetypes':
                        data = divisionstageservice().getpersonalspecificfiletypes(bcgovcode)
                    case 'volumes':
                        data = divisionstageservice().getpersonalspecificvolumes(bcgovcode)
                    case _:                        
                        data = divisionstageservice().getpersonalspecificdivisionandstages(bcgovcode)
            else:
                data = divisionstageservice().getdivisionandstages(bcgovcode)               
            jsondata = json.dumps(data)
            return jsondata , 200
        except Exception as exception:
            return {'status': False, 'message': str(type(exception).__name__)}, 400

@cors_preflight('GET,OPTIONS')
@API.route('/foiflow/divisions/<bcgovcode>/all')
class FOIFlowDivisionTags(Resource):
    """Retrieves all active divisions for the passed in gov code    .
    """
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @request_api.cache.cached(
        unless=cache_filter,
        response_filter=response_filter
        )
    def get(bcgovcode):
        try:
            data = divisionstageservice().getalldivisionsandsections(bcgovcode)               
            jsondata = json.dumps(data)
            return jsondata , 200
        except Exception as exception:
            return {'status': False, 'message': str(type(exception).__name__)}, 400     
     
@cors_preflight('GET,OPTIONS')
@API.route('/foiflow/closereasons')
class FOIFlowCloseReasons(Resource):
    """Retrieves all active closure reasons.
    """
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @request_api.cache.cached(
        key_prefix="closereasons",
        unless=cache_filter,
        response_filter=response_filter
        )
    def get():
        try:
            data = closereasonservice().getclosereasons()
            jsondata = json.dumps(data)
            return jsondata , 200
        except BusinessException:
            return "Error happened while accessing received modes" , 500

@cors_preflight('GET,OPTIONS')
@API.route('/foiflow/oss/authheader')
class FOIFlowDocumentStorage(Resource):
    """Retrieves authentication properties for document storage.
    """
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @auth.ismemberofgroups(getrequiredmemberships())
    def post():
        try:

            responsefilejson = storageservice().bulk_upload(request.get_json(), "Attachments")
            return json.dumps(responsefilejson),200
        except BusinessException as exception:
            return {'status': exception.status_code, 'message':exception.message}, 500

@cors_preflight('GET,OPTIONS')
@API.route('/foiflow/oss/presigned/<ministryrequestid>')
@API.route('/foiflow/oss/presigned/<ministryrequestid>/<category>/<bcgovcode>')
class FOIFlowS3Presigned(Resource):

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @auth.documentbelongstosameministry
    def get(ministryrequestid, category="attachments", bcgovcode=None):
        try :
            response = storageservice().retrieve_s3_presigned(request.args.get('filepath'), category, bcgovcode)
            return json.dumps(response),200
        except BusinessException as exception:
         return {'status': exception.status_code, 'message':exception.message}, 500

@cors_preflight('POST,OPTIONS')
@API.route('/foiflow/oss/presigned/<ministryrequestid>/<category>/<bcgovcode>')
class FOIFlowS3Presigned(Resource):

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @auth.documentbelongstosameministry
    def post(ministryrequestid, category, bcgovcode=None):
        try :
            if storageservice().is_valid_category(category) == False:
                return {'status': 400, 'message':"Bad Request"}, 400
            responsefilejson = storageservice().bulk_upload_s3_presigned(ministryrequestid, request.get_json(), category, bcgovcode)
            return json.dumps(responsefilejson),200
        except BusinessException as exception:
         return {'status': exception.status_code, 'message':exception.message}, 500

@cors_preflight('POST,OPTIONS')
@API.route('/foiflow/oss/completemultipart/<ministryrequestid>/<category>/<bcgovcode>')
class FOIFlowS3Presigned(Resource):

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @auth.documentbelongstosameministry
    def post(ministryrequestid, category, bcgovcode=None):
        try :
            if storageservice().is_valid_category(category) == False:
                return {'status': 400, 'message':"Bad Request"}, 400
            responsefilejson = storageservice().complete_upload_s3_presigned(request.get_json(), category, bcgovcode)
            return json.dumps(responsefilejson),200
        except BusinessException as exception:
         return {'status': exception.status_code, 'message':exception.message}, 500

@cors_preflight('GET,OPTIONS')
@API.route('/foiflow/extensionreasons')
class FOIFlowExtensionReasons(Resource):
    """Retrieves all active extension reasons.
    """
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @request_api.cache.cached(
        key_prefix="extensionreasons",
        unless=cache_filter,
        response_filter=response_filter
        )
    def get():
        try:
            data = extensionreasonservice().getextensionreasons()
            jsondata = json.dumps(data)
            return jsondata , 200
        except BusinessException as exception:
            return {'status': exception.status_code, 'message':exception.message}, 500

@cors_preflight('GET,OPTIONS')
@API.route('/foiflow/subjectcodes')
class FOIFlowSubjectCodes(Resource):
    """Retrieves all active subject codes.
    """
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @request_api.cache.cached(
        key_prefix="subjectcodes",
        unless=cache_filter,
        response_filter=response_filter
        )
    def get():
        try:
            data = subjectcodeservice().getsubjectcodes()
            jsondata = json.dumps(data)
            return jsondata , 200
        except BusinessException:
            return "Error happened while accessing subject codes" , 500

@cors_preflight('POST,OPTIONS')
@API.route('/foiflow/cache/refresh')
class FOIFlowRefreshCache(Resource):
    """Clear all cached data and fetch all the
        master data again based on key.
       N.B: This method will be invoked by the nightly
       job without any body so that all masterdata
       is flushed and recalled again.
       For caching a single key 
       (eg:if someone updates any keycloak users)
       Call API through Postman with following body:
       Body: { "key": "keycloakusers" } 
    """
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def post():
        try:
            request_json = request.get_json() if request.data else None
            resp_flag = cacheservice().refreshcache(request_json)
            return {"success": resp_flag } , 200 if resp_flag == True else 500
        except BusinessException:
            return "Error happened while clearing cache" , 500

@cors_preflight('GET,OPTIONS')
@API.route('/foiflow/oipc/reviewtypes')
class FOIFlowOIPCReviewTypes(Resource):
    """Retrieves OIPC review types along with reasons for each type
    """
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @request_api.cache.cached(
        key_prefix="oipcreviewtypesreasons",
        unless=cache_filter,
        response_filter=response_filter
        )
    def get():
        try:
            data = oipcservice().getreviewtypeswithreasons()
            jsondata = json.dumps(data)
            return jsondata , 200
        except BusinessException:
            return "Error happened while accessing OIPC review types and associated reasons" , 500

@cors_preflight('GET,OPTIONS')
@API.route('/foiflow/oipc/statuses')
class FOIFlowOIPCStatuses(Resource):
    """Retrieves OIPC statuses
    """
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @request_api.cache.cached(
        key_prefix="oipcstatuses",
        unless=cache_filter,
        response_filter=response_filter
        )
    def get():
        try:
            data = oipcservice().getstatuses()
            jsondata = json.dumps(data)
            return jsondata , 200
        except BusinessException:
            return "Error happened while accessing OIPC statuses" , 500


@cors_preflight('GET,OPTIONS')
@API.route('/foiflow/oipc/outcomes')
class FOIFlowOIPCOutcomes(Resource):
    """Retrieves OIPC outcomes
    """
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @request_api.cache.cached(
        key_prefix="oipcoutcomes",
        unless=cache_filter,
        response_filter=response_filter
        )
    def get():
        try:
            data = oipcservice().getoutcomes()
            jsondata = json.dumps(data)
            return jsondata , 200
        except BusinessException:
            return "Error happened while accessing OIPC outcomes" , 500

@cors_preflight('GET,OPTIONS')
@API.route('/foiflow/oipc/inquiryoutcomes')
class FOIFlowOIPCInquiryOutcomes(Resource):
    """Retrieves OIPC inquiry outcomes
    """
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @request_api.cache.cached(
        key_prefix="oipcinquiryoutcomes",
        unless=cache_filter,
        response_filter=response_filter
        )
    def get():
        try:
            data = oipcservice().getinquiryoutcomes()
            jsondata = json.dumps(data)
            return jsondata , 200
        except BusinessException:
            return "Error happened while accessing OIPC inquiry outcomes" , 500

@cors_preflight('GET,OPTIONS')
@API.route('/foiflow/openinfo/statuses')
class FOIFlowOpenInformationStatuses(Resource):
    """Retrieves OpenInformtation request statuses
    """
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @request_api.cache.cached(
        unless=cache_filter,
        response_filter=response_filter
    )
    def get():
        try:
            data = openinfoservice().getopeninfostatuses()
            jsondata = json.dumps(data)
            return jsondata , 200
        except BusinessException:
            return "Error happened while accessing OpenInformation statuses" , 500
        
@cors_preflight('GET,OPTIONS')
@API.route('/foiflow/openinfo/exemptions')
class FOIFlowOpenInformationExemptions(Resource):
    """Retrieves OpenInformtation exemptions
    """
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @request_api.cache.cached(
        unless=cache_filter,
        response_filter=response_filter
    )
    def get():
        try:
            data = openinfoservice().getopeninfoexemptions()
            jsondata = json.dumps(data)
            return jsondata , 200
        except BusinessException:
            return "Error happened while accessing OpenInformation exemptions" , 500
        
@cors_preflight('GET,OPTIONS')
@API.route('/foiflow/openinfo/publicationstatuses')
class FOIFlowOpenInformationPublicationStatuses(Resource):
    """Retrieves OpenInformtation publication statuses
    """
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @request_api.cache.cached(
        unless=cache_filter,
        response_filter=response_filter
    )
    def get():
        try:
            data = openinfoservice().getopeninfopublicationstatuses()
            jsondata = json.dumps(data)
            return jsondata , 200
        except BusinessException:
            return "Error happened while accessing OpenInformation publication statuses" , 500