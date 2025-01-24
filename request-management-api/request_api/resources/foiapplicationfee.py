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
"""API endpoints for managing a FOI Application Fee resource."""

from flask import g, request
from flask_restx import Namespace, Resource
from request_api.auth import auth, AuthHelper
from request_api.tracer import Tracer
from request_api.utils.util import  cors_preflight, allowedorigins
from request_api.exceptions import BusinessException, Error
from request_api.services.applicationfeeservice import applicationfeeservice
from request_api.schemas.foiapplicationfee import FOIApplicationFeeDataSchema, FOIApplicationFeeReceiptDataSchema
import json
from flask_cors import cross_origin
import logging
from marshmallow import ValidationError

API = Namespace('FOIApplicationFee', description='Endpoints for FOI Application Fee Form management')
TRACER = Tracer.get_instance()
"""Custom exception messages
"""
EXCEPTION_MESSAGE_BAD_REQUEST='Bad Request'
CUSTOM_KEYERROR_MESSAGE = "Key error has occured: "

@cors_preflight('GET,OPTIONS')
@API.route('/foiapplicationfee/foirequest/<requestid>/ministryrequest/<ministryrequestid>')
class FOICFRFee(Resource):
    """Retrieves application fee form based on either request id or ministry id."""
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def get(requestid, ministryrequestid):      
        try:
            ministryrequestid = None if ministryrequestid.lower()not in ['null', 'None', 'undefined'] else ministryrequestid
            if ministryrequestid is None and requestid.lower() in ['null', 'None', 'undefined']:
                return [], 200
            result = applicationfeeservice().getapplicationfee(requestid, ministryrequestid)
            return json.dumps(result), 200
        except KeyError as error:
            return {'status': False, 'message': CUSTOM_KEYERROR_MESSAGE + str(error)}, 400
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500   


@cors_preflight('POST,OPTIONS')
@API.route('/foiapplicationfee/foirequest/<requestid>/ministryrequest/<ministryrequestid>')
class SanctionFOICFRFee(Resource):
    """Saves or updates Application Fee."""
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def post(requestid, ministryrequestid):      
        try:
            if AuthHelper.getusertype() != "iao":
                return {'status': False, 'message':'UnAuthorized'}, 403
            requestjson = request.get_json() 
            ministryrequestid = None if ministryrequestid.lower() in ['null', 'none', 'undefined'] else ministryrequestid
            foiapplicationfeeschema = FOIApplicationFeeDataSchema().load(requestjson)
            result = applicationfeeservice().saveapplicationfee(requestid, ministryrequestid, foiapplicationfeeschema,AuthHelper.getuserid(), AuthHelper.getusername())
            receipts = []
            for receipt in foiapplicationfeeschema['receipts']:
                if 'receiptid' not in receipt:
                    # Create new receipts
                    receipt['createdby'] = AuthHelper.getuserid()
                    receipt['applicationfeeid'] = result.identifier
                    receipt['isactive'] = True
                    applicationfeereceiptschema = FOIApplicationFeeReceiptDataSchema().load(receipt)
                    savedreceipt = applicationfeeservice().saveapplicationfeereceipt(applicationfeereceiptschema)
                    receipts.append(savedreceipt)
                elif 'isactive' in receipt and receipt['isactive'] == False:
                    # Deactivate deleted receipts
                    applicationfeeservice().deactivateapplicationfeereceipt(receipt['receiptid'], AuthHelper.getuserid())
            return {'status': result.success, 'message':result.message,'id':result.identifier} , 200 
        except ValidationError as verr:
            logging.error(verr)
            return {'status': False, 'message': str(verr)}, 400     
        except KeyError as error:
            logging.error(CUSTOM_KEYERROR_MESSAGE + str(error))
            return {'status': False, 'message': CUSTOM_KEYERROR_MESSAGE + str(error)}, 400       
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500 

        