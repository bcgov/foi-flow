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
from request_api.auth import auth
from request_api.auth import auth, AuthHelper
from request_api.tracer import Tracer
from request_api.utils.util import  cors_preflight, allowedorigins
from request_api.exceptions import BusinessException, Error
from request_api.services.recordservice import recordservice
from request_api.schemas.foirecord import  FOIRequestCreateRecordSchema, FOIRequestBulkCreateRecordSchema
import json
from flask_cors import cross_origin


API = Namespace('FOIWatcher', description='Endpoints for FOI record management')
TRACER = Tracer.get_instance()

@cors_preflight('GET,OPTIONS')
@API.route('/foirecord/<requestid>/ministryrequest/<ministryrequestid>')
class FOIRequestGetRecord(Resource):
    """Retrieve watchers for unopened request"""

       
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def get(requestid, ministryrequestid):      
        try:
            result = recordservice().fetch(requestid, ministryrequestid)
            return json.dumps(result), 200
        except KeyError as err:
            return {'status': False, 'message':err.messages}, 400        
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500

@cors_preflight('POST,OPTIONS')
@API.route('/foirecord/<requestid>/ministryrequest/<ministryrequestid>')
class FOIRequestBulkCreateRecord(Resource):
    """Resource for Creating FOI records."""

       
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def post(requestid, ministryrequestid):      
        try:
            requestjson = request.get_json()
            recordschema = FOIRequestBulkCreateRecordSchema().load(requestjson)
            print(requestid)
            print(ministryrequestid)
            print(recordschema)
            response = recordservice().create(requestid, ministryrequestid, recordschema, AuthHelper.getuserid())
            respcode = 200 if response.success == True else 500
            return {'status': response.success, 'message':response.message,'data': response.args[0]} , respcode
        except KeyError as err:
            return {'status': False, 'message':err.messages}, 400        
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500