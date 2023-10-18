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
"""API endpoints for managing a FOI Payment"""


from flask import g, request
from flask_restx import Namespace, Resource, cors
from flask_expects_json import expects_json
from request_api.auth import auth
from request_api.auth import auth, AuthHelper
from request_api.tracer import Tracer
from request_api.utils.util import  cors_preflight, allowedorigins
from request_api.exceptions import BusinessException, Error
from request_api.services.paymentservice import paymentservice
from request_api.schemas.foipayment import  FOIRequestPaymentSchema


import json
from flask_cors import cross_origin

API = Namespace('FOIPayment', description='Endpoints for FOI Payment management')
TRACER = Tracer.get_instance()
CUSTOM_KEYERROR_MESSAGE = "Key error has occured: "

@cors_preflight('POST,OPTIONS')
@API.route('/foipayment/<requestid>/ministryrequest/<ministryrequestid>')
class CreateFOIPayment(Resource):
    """Handles applicant payment actions"""

       
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def post(requestid, ministryrequestid):      
        try:
            requestjson = request.get_json()
            paymentschema = FOIRequestPaymentSchema().load(requestjson)  
            result = paymentservice().createpayment(requestid, ministryrequestid, paymentschema)
            return {'status': result.success, 'message':result.message,'id':result.identifier} , 200 
        except KeyError as error:
            return {'status': False, 'message': CUSTOM_KEYERROR_MESSAGE + str(error)}, 400        
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500

@cors_preflight('POST,OPTIONS')
@API.route('/foipayment/<requestid>/ministryrequest/<ministryrequestid>/cancel')
class CreateFOIPayment(Resource):
    """Handles applicant payment actions"""

       
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def post(requestid, ministryrequestid):      
        try:
            requestjson = request.get_json()
            paymentschema = FOIRequestPaymentSchema().load(requestjson)
            result = paymentservice().cancelpayment(requestid, ministryrequestid, paymentschema)
            return {'status': result.success, 'message':result.message,'id':result.identifier} , 200 
        except KeyError as error:
            return {'status': False, 'message': CUSTOM_KEYERROR_MESSAGE + str(error)}, 400        
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500

@cors_preflight('GET,OPTIONS')
@API.route('/foipayment/<requestid>/ministryrequest/<ministryrequestid>')
class GetFOIPayment(Resource):
    """Handles applicant payment actions"""

       
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def get(requestid, ministryrequestid):      
        try:
            result = paymentservice().getpayment(requestid, ministryrequestid)
            return json.dumps(result), 200
        except KeyError as error:
            return {'status': False, 'message': CUSTOM_KEYERROR_MESSAGE + str(error)}, 400        
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500

