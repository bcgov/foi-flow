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
from flask_cors import cross_origin
from request_api.auth import auth
from request_api.tracer import Tracer
from request_api.utils.util import  cors_preflight, allowedOrigins
from request_api.exceptions import BusinessException, Error
from request_api.services.requestservice import requestservice
from request_api.services.rawrequestservice import rawrequestservice
from request_api.schemas.foirequestwrapper import  FOIRequestWrapperSchema, EditableFOIRequestWrapperSchema
from marshmallow import Schema, fields, validate, ValidationError
import json


API = Namespace('FOIRequests', description='Endpoints for FOI request management')
TRACER = Tracer.get_instance()


@cors_preflight('GET,POST,OPTIONS')
@API.route('/foirequests/<int:foirequestid>/ministryrequest/<int:foiministryrequestid>')
class FOIRequest(Resource):

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedOrigins())
    @auth.require
    def get(foirequestid,foiministryrequestid):
        try :            
            jsondata = {}
            jsondata = requestservice().getrequest(foirequestid=foirequestid,foiministryrequestid=foiministryrequestid)
            return jsondata , 200 
        except ValueError:
            return {'status': 500, 'message':"Invalid Request Id"}, 500    
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500

                       
@cors_preflight('GET,POST,OPTIONS')
@API.route('/foirequests')
class FOIRequests(Resource):
    """Resource for managing FOI requests."""

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedOrigins())
    @auth.require
    def post():
        """ POST Method for capturing FOI requests before processing"""
        try:
            request_json = request.get_json() 
            fOIRequestsSchema = FOIRequestWrapperSchema().load(request_json)       
            assignedGroup = request_json['assignedGroup'] if 'assignedGroup' in fOIRequestsSchema  else None
            assignedTo = request_json['assignedTo'] if 'assignedTo' in fOIRequestsSchema  else None
            rawresult = rawrequestservice.saverawrequestversion(request_json,request_json['id'],assignedGroup,assignedTo,"Open In Progress")               
            if rawresult.success == True:                
                result = requestservice().saverequest(fOIRequestsSchema)
                if result.success == True:
                    metadata = json.dumps({"id": result.identifier, "ministries": result.args[0], "assignedGroup": assignedGroup, "assignedTo": assignedTo})
                    requestservice().postEventToWorkflow(rawresult.args[0],json.loads(metadata))
            return {'status': result.success, 'message':result.message,'id':result.identifier, 'ministryRequests': result.args[0]} , 200
        except ValidationError as err:
                    return {'status': False, 'message':err.messages}, 400
        except TypeError:
            return {'status': "TypeError", 'message':"Error while parsing JSON in request"}, 500   
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500
        
@cors_preflight('GET,POST,PUT,OPTIONS')
@API.route('/foirequests/<int:foirequestid>/ministryrequest/<int:foiministryrequestid>')
class FOIRequestsById(Resource):
    """Resource for managing FOI requests."""

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedOrigins())
    @auth.require
    def post(foirequestid,foiministryrequestid):
        """ POST Method for capturing FOI requests before processing"""
        try:
            request_json = request.get_json()
            fOIRequestsSchema = FOIRequestWrapperSchema().load(request_json)                                    
            result = requestservice().saveRequestVersion(fOIRequestsSchema, foirequestid, foiministryrequestid)
            if result.success == True:
                metadata = json.dumps({"id": result.identifier, "ministries": result.args[0]})               
                requestservice().updateEventToWorkflow(fOIRequestsSchema,json.loads(metadata))
                return {'status': result.success, 'message':result.message,'id':result.identifier, 'ministryRequests': result.args[0]} , 200
            else:
                 return {'status': False, 'message':'Record not found','id':foirequestid} , 404
        except ValidationError as err:
            return {'status': False, 'message':err.messages}, 40
        except TypeError:
            return {'status': "TypeError", 'message':"Error while parsing JSON in request"}, 500   
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500
    


@cors_preflight('GET,POST,PUT,OPTIONS')
@API.route('/foirequests/<int:foirequestid>')
class FOIRequestUpdateById(Resource): 
    
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedOrigins())
    @auth.require
    def put(foirequestid):
        """ PUT Method for capturing FOI requests before processing"""
        try:
            request_json = request.get_json()
            fOIRequestsSchema = EditableFOIRequestWrapperSchema().load(request_json)
            result = requestservice().updaterequest(fOIRequestsSchema, foirequestid)
            if result != {}:
                return {'status': result.success, 'message':result.message,'id':result.identifier} , 200
            else:
                 return {'status': False, 'message':'Record not found','id':foirequestid} , 404
        except ValidationError as err:
            return {'status': False, 'message':err.messages}, 40
        except TypeError:
            return {'status': "TypeError", 'message':"Error while parsing JSON in request"}, 500
        except BusinessException as exception:
            return {'status': exception.status_code, 'message':exception.message}, 500