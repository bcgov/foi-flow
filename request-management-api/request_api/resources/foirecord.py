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
"""API endpoints for managing a FOI Request record resource."""


from flask import g, request
from flask_restx import Namespace, Resource, cors
from flask_expects_json import expects_json
from request_api.auth import auth, AuthHelper
from request_api.tracer import Tracer
from request_api.utils.util import  cors_preflight, allowedorigins, getrequiredmemberships
from request_api.exceptions import BusinessException, Error
from request_api.services.recordservice import recordservice
from request_api.schemas.foirecord import  FOIRequestBulkCreateRecordSchema, FOIRequestBulkRetryRecordSchema, FOIRequestRecordDownloadSchema, FOIRequestReplaceRecordSchema, FOIRequestRecordUpdateSchema, FOIRequestPersonalAttributesUpdateSchema
from marshmallow import INCLUDE
import json
from flask_cors import cross_origin
import asyncio
import traceback


API = Namespace('FOIWatcher', description='Endpoints for FOI record management')
TRACER = Tracer.get_instance()
CUSTOM_KEYERROR_MESSAGE = "Key error has occured: "

@cors_preflight('GET,OPTIONS')
@API.route('/foirecord/<requestid>/ministryrequest/<ministryrequestid>')
class FOIRequestGetRecord(Resource):
    """Retrieve watchers for unopened request"""


    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @auth.ismemberofgroups(getrequiredmemberships())
    def get(requestid, ministryrequestid):
        try:
            result = recordservice().fetch(requestid, ministryrequestid)
            return json.dumps(result), 200
        except KeyError as error:
            return {'status': False, 'message': CUSTOM_KEYERROR_MESSAGE + str(error)}, 400
        except Exception as exception:
            return {'status': False, 'message': str(exception)}, 500

@cors_preflight('POST,OPTIONS')
@API.route('/foirecord/<requestid>/ministryrequest/<ministryrequestid>')
class FOIRequestBulkCreateRecord(Resource):
    """Resource for Creating FOI records."""


    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @auth.ismemberofgroups(getrequiredmemberships())
    def post(requestid, ministryrequestid):
        try:
            requestjson = request.get_json()
            recordschema = FOIRequestBulkCreateRecordSchema().load(requestjson)
            response = recordservice().create(requestid, ministryrequestid, recordschema, AuthHelper.getuserid())
            respcode = 200 if response.success == True else 500
            return {'status': response.success, 'message':response.message,'data': response.args[0]} , respcode
        except KeyError as error:
            return {'status': False, 'message': CUSTOM_KEYERROR_MESSAGE + str(error)}, 400
        except BusinessException as exception:
            return {'status': exception.status_code, 'message':exception.message}, 500

@cors_preflight('POST,OPTIONS')
@API.route('/foirecord/<requestid>/ministryrequest/<ministryrequestid>/update')
class UpdateFOIDocument(Resource):
    """Resource for soft delete FOI requests."""


    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @auth.ismemberofgroups(getrequiredmemberships())
    def post(requestid, ministryrequestid):
        try:
            requestjson = request.get_json()
            data = FOIRequestRecordUpdateSchema().load(requestjson)
            result = recordservice().update(requestid, ministryrequestid, data, AuthHelper.getuserid())
            return {'status': result.success, 'message':result.message,'id':result.identifier} , 200
        except KeyError as error:
            return {'status': False, 'message': CUSTOM_KEYERROR_MESSAGE + str(error)}, 400
        except BusinessException as exception:
            return {'status': exception.status_code, 'message':exception.message}, 500

@cors_preflight('POST,OPTIONS')
@API.route('/foirecord/<requestid>/ministryrequest/<ministryrequestid>/updatepersonalattributes')
class UpdateFOIDocument(Resource):
    """Resource for soft delete FOI requests."""


    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @auth.ismemberofgroups(getrequiredmemberships())
    def post(requestid, ministryrequestid):
        try:
            requestjson = request.get_json()
            data = FOIRequestPersonalAttributesUpdateSchema().load(requestjson)
            result = recordservice().updatepersonalattributes(requestid, ministryrequestid, data, AuthHelper.getuserid())
            return {'status': result.success, 'message':result.message,'id':result.identifier} , 200
        except KeyError as error:
            return {'status': False, 'message': CUSTOM_KEYERROR_MESSAGE + str(error)}, 400
        except BusinessException as exception:
            return {'status': exception.status_code, 'message':exception.message}, 500

@cors_preflight('POST,OPTIONS')
@API.route('/foirecord/<requestid>/ministryrequest/<ministryrequestid>/retry')
class RetryFOIDocument(Resource):
    """Resource for soft delete FOI requests."""

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @auth.ismemberofgroups(getrequiredmemberships())
    def post(requestid, ministryrequestid):
        try:
            requestjson = request.get_json()
            recordschema = FOIRequestBulkRetryRecordSchema().load(requestjson, unknown=INCLUDE)
            result = recordservice().retry(requestid, ministryrequestid, recordschema)
            return {'status': result.success, 'message':result.message,'id':result.identifier} , 200
        except KeyError as error:
            return {'status': False, 'message': CUSTOM_KEYERROR_MESSAGE + str(error)}, 400
        except BusinessException as exception:
            return {'status': exception.status_code, 'message':exception.message}, 500
        
@cors_preflight('POST,OPTIONS')
@API.route('/foirecord/<requestid>/ministryrequest/<ministryrequestid>/record/<recordid>/replace')
class ReplaceFOIDocument(Resource):
    """Resource for replacing records on FOI requests."""
       
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @auth.ismemberofgroups(getrequiredmemberships())
    def post(requestid, ministryrequestid,recordid):
        try:
            requestjson = request.get_json()            
            recordschema = FOIRequestReplaceRecordSchema().load(requestjson, unknown=INCLUDE)            
            result = recordservice().replace(requestid, ministryrequestid,recordid, recordschema,AuthHelper.getuserid())

            return {'status': result.success, 'message':result.message,'id':result.identifier} , 200
        except KeyError as error:
            return {'status': False, 'message': CUSTOM_KEYERROR_MESSAGE + str(error)}, 400
        except BusinessException as exception:
            return {'status': exception.status_code, 'message':exception.message}, 500
        
@cors_preflight('POST,OPTIONS')
@API.route('/foirecord/<requestid>/ministryrequest/<ministryrequestid>/triggerdownload/<recordstype>')
class FOIRequestDownloadRecord(Resource):
    """Resource for Creating FOI records."""


    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @auth.ismemberofgroups(getrequiredmemberships())
    def post(requestid, ministryrequestid, recordstype):
        try:
            requestjson = request.get_json()
            recordschema = FOIRequestRecordDownloadSchema().load(requestjson)
            response = recordservice().triggerpdfstitchservice(requestid, ministryrequestid, recordschema, AuthHelper.getuserid())
            respcode = 200 if response.success == True else 500
            return {'status': response.success, 'message':response.message,'id':response.identifier}, respcode
        except KeyError as error:
            return {'status': False, 'message': CUSTOM_KEYERROR_MESSAGE + str(error)}, 400
        except BusinessException as exception:
            return {'status': exception.status_code, 'message':exception.message}, 500

@cors_preflight('GET,OPTIONS')
@API.route('/foirecord/<requestid>/ministryrequest/<ministryrequestid>/download/<recordstype>')
class FOIRequestDownloadRecord(Resource):
    """Resource for Creating FOI records."""


    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @auth.ismemberofgroups(getrequiredmemberships())
    def get(requestid, ministryrequestid, recordstype):
        try:
            result = recordservice().getpdfstitchpackagetodownload(ministryrequestid, recordstype.lower())
            return json.dumps(result), 200
        except KeyError as error:
            return {'status': False, 'message': CUSTOM_KEYERROR_MESSAGE + str(error)}, 400
        except BusinessException as exception:
            return {'status': exception.status_code, 'message':exception.message}, 500

@cors_preflight('GET,OPTIONS')
@API.route('/foirecord/<requestid>/ministryrequest/<ministryrequestid>/<recordstype>/pdfstitchjobstatus')
class FOIRequestPDFStitchStatus(Resource):
    """Resource for Creating FOI records."""


    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @auth.ismemberofgroups(getrequiredmemberships())
    def get(requestid, ministryrequestid, recordstype):
        try:
            result = recordservice().getpdfstichstatus(ministryrequestid, recordstype.lower())
            #("getpdfstichstatus result == ", result)
            return result, 200
        except KeyError as error:
            print(CUSTOM_KEYERROR_MESSAGE + str(error))
            return {'status': False, 'message': CUSTOM_KEYERROR_MESSAGE + str(error)}, 400  
        except BusinessException as exception:
            print("BusinessException == ", exception.message)
            return {'status': exception.status_code, 'message':exception.message}, 500
        except Exception as error:
            print("Exception error == ", error)
            return {'status': False, 'message': str(error)}, 500
    
@cors_preflight('GET,OPTIONS')
@API.route('/foirecord/<requestid>/ministryrequest/<ministryrequestid>/<recordstype>/recrodschanged')
class FOIRequestRecordsChanged(Resource):
    """Resource for Creating FOI records."""


    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @auth.ismemberofgroups(getrequiredmemberships())
    def get(requestid, ministryrequestid, recordstype):
        try:
            result = recordservice().isrecordschanged(ministryrequestid, recordstype.lower())
            #print("records changed == ", result)
            return result, 200
        except KeyError as error:
            print(CUSTOM_KEYERROR_MESSAGE + str(error))
            return {'status': False, 'message': CUSTOM_KEYERROR_MESSAGE + str(error)}, 400
        except BusinessException as exception:
            print("BusinessException == ", exception.message)
            return {'status': exception.status_code, 'message':exception.message}, 500
        except Exception as error:
            print("Exception error == ", error)
            return {'status': False, 'message': str(error)}, 500


# this is for inflight request pagecount calculation option 1
@cors_preflight('POST,OPTIONS')
@API.route('/updatepagecount')
class UpdateRequestsPageCount(Resource):
    """updatepagecount option 1."""

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def post():
        try:
            requestjson = request.get_json()
            ministryrequestid = requestjson['ministryrequestid']  if requestjson.get("ministryrequestid") != None else None
            if ministryrequestid:
                event_loop = asyncio.get_running_loop()
                asyncio.run_coroutine_threadsafe(recordservice().updatepagecount(ministryrequestid, AuthHelper.getuserid()), event_loop)
                return {'status': True, 'message': 'async updatepagecount function called'} , 200
            else:
                return {'status': True, 'message':'ministryrequestid is none'} , 200
        except KeyError as error:
            return {'status': False, 'message': CUSTOM_KEYERROR_MESSAGE + str(error)}, 400
        except BusinessException as exception:
            return {'status': exception.status_code, 'message':exception.message}, 500
    
# this is for inflight request pagecount calculation option 2
@cors_preflight('POST,OPTIONS')
@API.route('/updatepagecount/option2')
class UpdateRequestsPageCountOption2(Resource):
    """updatepagecount option 2"""

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def post():
        try:
            requestjson = request.get_json()
            ministryrequestid = requestjson['ministryrequestid']  if requestjson.get("ministryrequestid") != None else None
            requestid = requestjson['requestid']  if requestjson.get("requestid") != None else None
            print(f'option 2 >>> requestid = {requestid}, ministryrequestid = {ministryrequestid}')
            if ministryrequestid:
                event_loop = asyncio.get_running_loop()
                asyncio.run_coroutine_threadsafe(recordservice().calculatepagecount(requestid, ministryrequestid, AuthHelper.getuserid()), event_loop)
                return {'status': True, 'message': 'async calculatepagecount function called'} , 200
            else:
                return {'status': True, 'message':'ministryrequestid is none'} , 200
        except KeyError as error:
            return {'status': False, 'message': CUSTOM_KEYERROR_MESSAGE + str(error)}, 400
        except BusinessException as exception:
            return {'status': exception.status_code, 'message':exception.message}, 500
        
@cors_preflight('GET,OPTIONS')
@API.route('/foirecord/historical/<axisrequestid>')
class FOIRequestGetRecord(Resource):
    """Fetch documents for historical records"""


    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @auth.ismemberofgroups(getrequiredmemberships())
    def get(axisrequestid):
        try:
            result = recordservice().gethistoricaldocuments(axisrequestid)
            return json.dumps(result), 200
        except KeyError as error:
            traceback.print_exc() 
            return {'status': False, 'message': CUSTOM_KEYERROR_MESSAGE + str(error)}, 400
        except Exception as exception:
            traceback.print_exc() 
            return {'status': False, 'message': str(exception)}, 500
