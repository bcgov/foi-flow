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
"""API endpoints for managing a FOI Email Communication"""


from flask import g, request
from flask_restx import Namespace, Resource, cors
from flask_expects_json import expects_json
from request_api.auth import auth
from request_api.auth import auth, AuthHelper
from request_api.tracer import Tracer
from request_api.utils.util import  cors_preflight, allowedorigins
from request_api.exceptions import BusinessException, Error
from request_api.services.emailservice import emailservice
from request_api.services.requestservice import requestservice
from request_api.utils.enums import ServiceName
from request_api.schemas.foiemail import  FOIEmailSchema

import json
from flask_cors import cross_origin

API = Namespace('FOIEmail', description='Endpoints for FOI EMAIL management')
TRACER = Tracer.get_instance()

@cors_preflight('POST,OPTIONS')
@API.route('/foiemail/<requestid>/ministryrequest/<ministryrequestid>/<servicename>')
class FOISendEmail(Resource):
    """Retrieve watchers for unopened request"""

       
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def post(requestid, ministryrequestid, servicename):      
        try:
            requestjson = request.get_json()
            emailschema = FOIEmailSchema().load(requestjson)
            result = emailservice().send(servicename.upper(), requestid, ministryrequestid, emailschema)
            return json.dumps(result), 200 if result["success"] == True else 500
        except ValueError as err:
            return {'status': 500, 'message': str(err)}, 500
        except KeyError as error:
            return {'status': False, 'message': str(type(error).__name__)}, 400        
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500

@cors_preflight('POST,OPTIONS')
@API.route('/foiemail/<requestid>/ministryrequest/<ministryrequestid>/<servicename>/acknowledge')
class FOIAcknowledgeSendEmail(Resource):
    """Retrieve watchers for unopened request"""

       
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def post(requestid, ministryrequestid, servicename):      
        try:
            result = emailservice().acknowledge(servicename.upper(), requestid, ministryrequestid)
            return json.dumps(result), 200 if result["success"] == True else 500
        except ValueError as err:
            return {'status': 500, 'message': str(err)}, 500
        except KeyError as error:
            return {'status': False, 'message': str(type(error).__name__)}, 400        
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500
        
