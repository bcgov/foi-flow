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
"""API endpoints for managing a FOI CFR Fee resource."""


from flask import g, request
from flask_restx import Namespace, Resource, cors
from flask_expects_json import expects_json
from request_api.auth import auth, AuthHelper
from request_api.tracer import Tracer
from request_api.utils.util import  cors_preflight, allowedorigins
from request_api.exceptions import BusinessException, Error
from request_api.services.feewaiverservice import feewaiverservice
from request_api.services.cfrfeeservice import cfrfeeservice
from request_api.schemas.foifeewaiver import FOIFeeWaiverIAOSchema, FOIFeeWaiverMinistrySchema
import json
from flask_cors import cross_origin
import logging
from marshmallow import Schema, fields, validate, ValidationError
import asyncio
from request_api.services.eventservice import eventservice

API = Namespace('FOIFeeWaiver', description='Endpoints for FOI Fee Waiver Form management')
TRACER = Tracer.get_instance()
"""Custom exception messages
"""
EXCEPTION_MESSAGE_BAD_REQUEST='Bad Request'

@cors_preflight('POST,OPTIONS')
@API.route('/foifeewaiver/ministryrequest/<ministryrequestid>')
class CreateFOIFeeWaiver(Resource):
    """Endpoint for IAO User"""

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def post(ministryrequestid):
        try:
            if AuthHelper.getusertype() != "iao":
                return {'status': False, 'message':'Unauthorized'}, 403
            requestjson = request.get_json()
            feewaiverschema = FOIFeeWaiverIAOSchema().load(requestjson)
            result = feewaiverservice().savefeewaiver(ministryrequestid, feewaiverschema, AuthHelper.getuserid())
            # asyncio.ensure_future(eventservice().posteventforfeewaiver(ministryrequestid, AuthHelper.getuserid(), AuthHelper.getusername()))
            return {'status': result.success, 'message':result.message,'id':result.identifier} , 200
        except ValidationError as verr:
            logging.error(verr)
            return {'status': False, 'message':verr.messages}, 400
        except KeyError as err:
            logging.error(err)
            return {'status': False, 'message': EXCEPTION_MESSAGE_BAD_REQUEST}, 400
        except BusinessException as exception:
            return {'status': exception.status_code, 'message':exception.message}, 500

@cors_preflight('POST,OPTIONS')
@API.route('/foifeewaiver/ministryrequest/<ministryrequestid>/decision')
class ApproveFOIFeeWaiver(Resource):
    """Endpoint for ministry user"""

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def post(ministryrequestid):
        try:
            if AuthHelper.getusertype() != "ministry":
                return {'status': False, 'message':'UnAuthorized'}, 403
            requestjson = request.get_json()
            feewaiverschema = FOIFeeWaiverMinistrySchema().load(requestjson)
            result = feewaiverservice().savefeewaiver(ministryrequestid, feewaiverschema,AuthHelper.getuserid())
            cfrfeeservice().waivecfrfee(ministryrequestid, feewaiverschema['formdata']['decision']['amount'] , AuthHelper.getuserid())
            # asyncio.ensure_future(eventservice().posteventforcfrfeeform(ministryrequestid, AuthHelper.getuserid(), AuthHelper.getusername()))
            return {'status': result.success, 'message':result.message,'id':result.identifier} , 200
        except ValidationError as verr:
            logging.error(verr)
            return {'status': False, 'message':verr.messages}, 400
        except KeyError as err:
            logging.error(err)
            return {'status': False, 'message': EXCEPTION_MESSAGE_BAD_REQUEST}, 400
        except BusinessException as exception:
            return {'status': exception.status_code, 'message':exception.message}, 500

@cors_preflight('GET,OPTIONS')
@API.route('/foifeewaiver/ministryrequest/<requestid>')
class FOIFeeWaiver(Resource):
    """Retrieves fee waiver form based on ministry id."""

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def get(requestid):
        try:
            result = feewaiverservice().getfeewaiver(requestid)
            return json.dumps(result), 200
        except KeyError as err:
            return {'status': False, 'message':err.messages}, 400
        except BusinessException as exception:
            return {'status': exception.status_code, 'message':exception.message}, 500
