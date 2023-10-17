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


from flask import g, request
from flask_restx import Namespace, Resource, cors
from flask_expects_json import expects_json
from request_api.auth import auth
from request_api.auth import auth, AuthHelper
from request_api.tracer import Tracer
from request_api.utils.util import  cors_preflight, allowedorigins
from request_api.exceptions import BusinessException, Error
from request_api.services.watcherservice import watcherservice
from request_api.services.eventservice import eventservice
from request_api.schemas.foiwatcher import  FOIRawRequestWatcherSchema, FOIMinistryRequestWatcherSchema
from request_api.services.eventservice import eventservice
import json
from flask_cors import cross_origin


API = Namespace('FOIWatcher', description='Endpoints for FOI watcher management')
TRACER = Tracer.get_instance()

@cors_preflight('GET,OPTIONS')
@API.route('/foiwatcher/rawrequest/<requestid>')
class FOIRawRequestWatcher(Resource):
    """Retrieve watchers for unopened request"""

       
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def get(requestid):      
        try:
            result = watcherservice().getrawrequestwatchers(requestid)
            return json.dumps(result), 200
        except ValueError as err:
            return {'status': 500, 'message':err.messages}, 500
        except KeyError as error:
            return {'status': False, 'message': f"{error=}"}, 400        
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500

@cors_preflight('POST,OPTIONS')
@API.route('/foiwatcher/rawrequest')
class CreateFOIRawRequestWatcher(Resource):
    """Create watcher for unopened request"""

       
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def post():      
        try:
            requestjson = request.get_json()
            rawrquestwatcherschema = FOIRawRequestWatcherSchema().load(requestjson)
            result = watcherservice().createrawrequestwatcher(rawrquestwatcherschema, AuthHelper.getuserid(), AuthHelper.getusergroups())
            if result.success == True:
                eventservice().posteventforwatcher(requestjson["requestid"], requestjson, "rawrequest",AuthHelper.getuserid(), AuthHelper.getusername())
            return {'status': result.success, 'message':result.message} , 200 
        except KeyError as error:
            return {'status': False, 'message': f"{error=}"}, 400        
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500
        
@cors_preflight('PUT,OPTIONS')
@API.route('/foiwatcher/rawrequest/disable/<requestid>')
class DisableFOIRawRequestWatcher(Resource):
    """Disable watcher for unopened request"""

       
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def put(requestid):      
        try:
            result = watcherservice().disablerawrequestwatchers(requestid, AuthHelper.getuserid())
            return {'status': result.success, 'message':result.message,'id':result.identifier} , 200 
        except KeyError as error:
            return {'status': False, 'message': f"{error=}"}, 400        
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500
                  
@cors_preflight('GET,OPTIONS')
@API.route('/foiwatcher/ministryrequest/<ministryrequestid>')
class FOIRequestWatcher(Resource):
    """Retrieve watchers for opened request"""

       
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def get(ministryrequestid):      
        try:
            result = watcherservice().getministryrequestwatchers(ministryrequestid,AuthHelper.isministrymember())
            return json.dumps(result), 200
        except KeyError as error:
            return {'status': False, 'message': f"{error=}"}, 400        
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500         
        
@cors_preflight('POST,OPTIONS')
@API.route('/foiwatcher/ministryrequest')
class CreateFOIRequestWatcher(Resource):
    """Create watcher for opened request"""

       
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def post():      
        try:
            requestjson = request.get_json()
            minrquestwatcherschema = FOIMinistryRequestWatcherSchema().load(requestjson)
            result = watcherservice().createministryrequestwatcher(minrquestwatcherschema, AuthHelper.getuserid(),AuthHelper.getusergroups())
            if result.success == True:
                eventservice().posteventforwatcher(requestjson["ministryrequestid"], requestjson, "ministryrequest", AuthHelper.getuserid(), AuthHelper.getusername())
            return {'status': result.success, 'message':result.message} , 200 
        except KeyError as error:
            return {'status': False, 'message': f"{error=}"}, 400        
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500 
        
@cors_preflight('PUT,OPTIONS')
@API.route('/foiwatcher/ministryrequest/disable/<ministryrequestid>')
class DisableFOIRequestWatcher(Resource):
    """Disable watcher for opened request"""

       
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def put(ministryrequestid):      
        try:
            result = watcherservice().disableministryrequestwatchers(ministryrequestid, AuthHelper.getuserid())
            return {'status': result.success, 'message':result.message,'id':result.identifier} , 200 
        except KeyError as error:
            return {'status': False, 'message': f"{error=}"}, 400        
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500