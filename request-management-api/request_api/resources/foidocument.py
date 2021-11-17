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
from request_api.services.documentservice import documentservice
from request_api.schemas.foidocument import  CreateDocumentSchema, RenameDocumentSchema, ReplaceDocumentSchema 
import json
from flask_cors import cross_origin


API = Namespace('FOIDocument', description='Endpoints for FOI Document management')
TRACER = Tracer.get_instance()  
        
    
@cors_preflight('GET,OPTIONS')
@API.route('/foidocument/ministryrequest/<requestid>')
class CreateFOIDocument(Resource):
    """Resource for managing FOI requests."""

       
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedOrigins())
    @auth.require
    def get(requestid):      
        try:
            result = documentservice().getministryrequestdocuments(requestid)
            return json.dumps(result), 200
        except ValueError:
            return {'status': 500, 'message':"Invalid Request Id"}, 500
        except KeyError as err:
            return {'status': False, 'message':err.messages}, 400        
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500   

@cors_preflight('POST,OPTIONS')
@API.route('/foidocument/ministryrequest/<requestid>')
class CreateFOIDocument(Resource):
    """Resource for managing FOI requests."""

       
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedOrigins())
    @auth.require
    def post(requestid):      
        try:
            requestjson = request.get_json() 
            documentschema = CreateDocumentSchema().load(requestjson)
            result = documentservice().createministryrequestdocument(requestid, documentschema, AuthHelper.getUserId())
            return {'status': result.success, 'message':result.message} , 200 
        except ValueError:
            return {'status': 500, 'message':"Invalid Request Id"}, 500
        except KeyError as err:
            return {'status': False, 'message':err.messages}, 400        
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500 
        

@cors_preflight('POST,OPTIONS')
@API.route('/foidocument/ministryrequest/<requestid>/documentid/<documentid>/rename')
class RenameFOIDocument(Resource):
    """Resource for managing FOI requests."""

       
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedOrigins())
    @auth.require
    def post(requestid, documentid):      
        try:
            requestjson = request.get_json() 
            documentschema = RenameDocumentSchema().load(requestjson)
            result = documentservice().renameministryrequestdocument(requestid, documentid, documentschema, AuthHelper.getUserId())
            return {'status': result.success, 'message':result.message,'id':result.identifier} , 200 
        except ValueError:
            return {'status': 500, 'message':"Invalid Request Id"}, 500
        except KeyError as err:
            return {'status': False, 'message':err.messages}, 400        
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500 
        
@cors_preflight('POST,OPTIONS')
@API.route('/foidocument/ministryrequest/<requestid>/documentid/<documentid>/replace')
class ReplaceFOIDocument(Resource):
    """Resource for managing FOI requests."""

       
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedOrigins())
    @auth.require
    def post(requestid, documentid):      
        try:
            requestjson = request.get_json() 
            documentschema = ReplaceDocumentSchema().load(requestjson)
            result = documentservice().replaceministryrequestdocument(requestid, documentid, documentschema, AuthHelper.getUserId())
            return {'status': result.success, 'message':result.message,'id':result.identifier} , 200 
        except ValueError:
            return {'status': 500, 'message':"Invalid Request Id"}, 500
        except KeyError as err:
            return {'status': False, 'message':err.messages}, 400        
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500 
        
        
@cors_preflight('POST,OPTIONS')
@API.route('/foidocument/ministryrequest/<requestid>/documentid/<documentid>/delete')
class ReplaceFOIDocument(Resource):
    """Resource for managing FOI requests."""

       
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedOrigins())
    @auth.require
    def post(requestid, documentid):      
        try:
            result = documentservice().deleteministryrequestdocument(requestid, documentid, AuthHelper.getUserId())
            return {'status': result.success, 'message':result.message,'id':result.identifier} , 200 
        except ValueError:
            return {'status': 500, 'message':"Invalid Request Id"}, 500
        except KeyError as err:
            return {'status': False, 'message':err.messages}, 400        
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500 