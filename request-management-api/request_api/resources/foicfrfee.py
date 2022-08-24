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
from request_api.services.cfrfeeservice import cfrfeeservice
from request_api.schemas.foicfrfee import FOICFRFeeSchema, FOICFRFeeSanctionSchema
import json
from flask_cors import cross_origin
import logging
from marshmallow import Schema, fields, validate, ValidationError
import asyncio
from request_api.services.eventservice import eventservice

API = Namespace('FOICFRFee', description='Endpoints for FOI CFR Fee Form management')
TRACER = Tracer.get_instance()
"""Custom exception messages
"""
EXCEPTION_MESSAGE_BAD_REQUEST='Bad Request'
        
@cors_preflight('POST,OPTIONS')
@API.route('/foicfrfee/ministryrequest/<ministryrequestid>')
class CreateFOICFRFee(Resource):
    """Creates CFR Fee for ministry request."""
       
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    #@auth.require
    def post(ministryrequestid):      
        try:
            if AuthHelper.getusertype() != "ministry":
                return {'status': False, 'message':'UnAuthorized'}, 403
            requestjson = request.get_json() 
            foicfrfeeschema = FOICFRFeeSchema().load(requestjson)  
            result = cfrfeeservice().createcfrfee(ministryrequestid, foicfrfeeschema,AuthHelper.getuserid())
            asyncio.ensure_future(eventservice().posteventforcfrfeeform(ministryrequestid, AuthHelper.getuserid(), AuthHelper.getusername()))
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
@API.route('/foicfrfee/ministryrequest/<ministryrequestid>/sanction')
class SanctionFOICFRFee(Resource):
    """Updates CFR Fee status and iao preparing field."""
       
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    #@auth.require
    def post(ministryrequestid):      
        try:
            if AuthHelper.getusertype() != "iao":
                return {'status': False, 'message':'UnAuthorized'}, 403
            requestjson = request.get_json() 
            foicfrfeeschema = FOICFRFeeSanctionSchema().load(requestjson)  
            result = cfrfeeservice().sanctioncfrfee(ministryrequestid, foicfrfeeschema,AuthHelper.getuserid())
            asyncio.ensure_future(eventservice().posteventforcfrfeeform(ministryrequestid, AuthHelper.getuserid(), AuthHelper.getusername()))
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
@API.route('/foicfrfee/ministryrequest/<requestid>')
class FOICFRFee(Resource):
    """Retrieves cfr fee form based on ministry id."""

       
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    #@auth.require
    def get(requestid):      
        try:
            result = cfrfeeservice().getcfrfee(requestid)
            return json.dumps(result), 200
        except KeyError as err:
            return {'status': False, 'message':err.messages}, 400        
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500   
        
@cors_preflight('GET,OPTIONS')
@API.route('/foicfrfee/ministryrequest/<requestid>/history')
class FOICFRFee(Resource):
    """Retrieves cfr fee form based on ministry id."""

       
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    #@auth.require
    def get(requestid):      
        try:
            result = cfrfeeservice().getcfrfeehistory(requestid)
            return json.dumps(result), 200
        except KeyError as err:
            return {'status': False, 'message':err.messages}, 400        
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500  