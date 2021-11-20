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
from request_api.utils.util import  cors_preflight, allowedOrigins
from request_api.exceptions import BusinessException, Error
from request_api.services.watcherservice import watcherservice
from request_api.schemas.foiwatcher import  FOIRawRequestWatcherSchema, FOIMinistryRequestWatcherSchema
import json
from flask_cors import cross_origin


API = Namespace('FOIWatcher', description='Endpoints for FOI watcher management')
TRACER = Tracer.get_instance()

@cors_preflight('GET,OPTIONS')
@API.route('/foiwatcher/rawrequest/<requestid>')
class FOIRawRequestWatcher(Resource):
    """Resource for managing FOI requests."""

       
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedOrigins())
    #@auth.require
    def get(requestid):      
        try:
            result = watcherservice().getrawrequestwatchers(requestid)
            return json.dumps(result), 200
        except ValueError:
            return {'status': 500, 'message':"Invalid Request Id"}, 500
        except KeyError as err:
            return {'status': False, 'message':err.messages}, 400        
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500

@cors_preflight('POST,OPTIONS')
@API.route('/foiwatcher/rawrequest')
class CreateFOIRawRequestWatcher(Resource):
    """Resource for managing FOI requests."""

       
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedOrigins())
    #@auth.require
    def post():      
        try:
            requestjson = request.get_json() 
            rawrquestwatcherschema = FOIRawRequestWatcherSchema().load(requestjson)  
            result = watcherservice().createrawrequestwatcher(rawrquestwatcherschema, AuthHelper.getUserId(), AuthHelper.getUserGroups())
            return {'status': result.success, 'message':result.message} , 200 
        except ValueError:
            return {'status': 500, 'message':"Invalid Request Id"}, 500
        except KeyError as err:
            return {'status': False, 'message':err.messages}, 400        
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500
        
@cors_preflight('PUT,OPTIONS')
@API.route('/foiwatcher/rawrequest/disable/<requestid>')
class DisableFOIRawRequestWatcher(Resource):
    """Resource for managing FOI requests."""

       
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedOrigins())
    #@auth.require
    def put(requestid):      
        try:
            result = watcherservice().disablerawrequestwatchers(requestid, AuthHelper.getUserId())
            return {'status': result.success, 'message':result.message,'id':result.identifier} , 200 
        except ValueError:
            return {'status': 500, 'message':"Invalid Request Id"}, 500
        except KeyError as err:
            return {'status': False, 'message':err.messages}, 400        
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500
                  
@cors_preflight('GET,OPTIONS')
@API.route('/foiwatcher/ministryrequest/<ministryrequestid>')
class FOIRequestWatcher(Resource):
    """Resource for managing FOI requests."""

       
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedOrigins())
    #@auth.require
    def get(ministryrequestid):      
        try:
            result = watcherservice().getministryrequestwatchers(ministryrequestid,AuthHelper.isMinistryMember())
            return json.dumps(result), 200
        except ValueError:
            return {'status': 500, 'message':"Invalid Request Id"}, 500
        except KeyError as err:
            return {'status': False, 'message':err.messages}, 400        
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500         
        
@cors_preflight('POST,OPTIONS')
@API.route('/foiwatcher/ministryrequest')
class CreateFOIRequestWatcher(Resource):
    """Resource for managing FOI requests."""

       
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedOrigins())
    #@auth.require
    def post():      
        try:
            requestjson = request.get_json() 
            minrquestwatcherschema = FOIMinistryRequestWatcherSchema().load(requestjson)  
            result = watcherservice().createministryrequestwatcher(minrquestwatcherschema, AuthHelper.getUserId(),AuthHelper.getUserGroups())
            return {'status': result.success, 'message':result.message} , 200 
        except ValueError:
            return {'status': 500, 'message':"Invalid Request Id"}, 500
        except KeyError as err:
            return {'status': False, 'message':err.messages}, 400        
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500 
        
@cors_preflight('PUT,OPTIONS')
@API.route('/foiwatcher/ministryrequest/disable/<ministryrequestid>')
class DisableFOIRequestWatcher(Resource):
    """Resource for managing FOI requests."""

       
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedOrigins())
    #@auth.require
    def put(ministryrequestid):      
        try:
            result = watcherservice().disableministryrequestwatchers(ministryrequestid, AuthHelper.getUserId())
            return {'status': result.success, 'message':result.message,'id':result.identifier} , 200 
        except ValueError:
            return {'status': 500, 'message':"Invalid Request Id"}, 500
        except KeyError as err:
            return {'status': False, 'message':err.messages}, 400        
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500