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
from request_api.services.documentservice import documentservice
from request_api.schemas.foidocument import  CreateDocumentSchema, RenameDocumentSchema, ReplaceDocumentSchema, ReclassifyDocumentSchema
import json
from marshmallow import Schema, fields, validate, ValidationError
from flask_cors import cross_origin
import boto3


API = Namespace('FOIDocument', description='Endpoints for FOI Document management')
TRACER = Tracer.get_instance()  
        
    
@cors_preflight('GET,OPTIONS')
@API.route('/foidocument/<requesttype>/<requestid>')
class GetFOIDocument(Resource):
    """Resource for managing FOI requests."""

       
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def get(requestid, requesttype): 
        if requesttype != "ministryrequest" and requesttype != "rawrequest":
            return {'status': False, 'message':'Bad Request'}, 400          
        try:
            result = documentservice().getrequestdocumentsbyrole(requestid, requesttype, AuthHelper.isministrymember())
            return json.dumps(result), 200
        except KeyError as error:
            return {'status': False, 'message': f"{error=}"}, 400        
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500   

@cors_preflight('POST,OPTIONS')
@API.route('/foidocument/<requesttype>/<requestid>')
class CreateFOIDocument(Resource):
    """Resource for managing FOI requests."""

       
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def post(requestid, requesttype):      
        try:
            if requesttype != "ministryrequest" and requesttype != "rawrequest":
                return {'status': False, 'message':'Bad Request'}, 400
            requestjson = request.get_json() 
            documentschema = CreateDocumentSchema().load(requestjson)
            result = documentservice().createrequestdocument(requestid, documentschema, AuthHelper.getuserid(), requesttype)
            return {'status': result.success, 'message':result.message} , 200 
        except ValidationError as err:
             return {'status': False, 'message': err}, 400
        except KeyError as error:
            return {'status': False, 'message': f"{error=}"}, 400        
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500 
        

@cors_preflight('POST,OPTIONS')
@API.route('/foidocument/<requesttype>/<requestid>/documentid/<documentid>/rename')
class RenameFOIDocument(Resource):
    """Resource for managing FOI requests."""

       
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def post(requestid, documentid, requesttype):      
        try:
            requestjson = request.get_json() 
            documentschema = RenameDocumentSchema().load(requestjson)
            result = documentservice().createrequestdocumentversion(requestid, documentid, documentschema, AuthHelper.getuserid(), requesttype)
            return {'status': result.success, 'message':result.message,'id':result.identifier} , 200 
        except ValidationError as err:
            return {'status': False, 'message': err}, 400
        except KeyError as error:
            return {'status': False, 'message': f"{error=}"}, 400        
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500 
        
@cors_preflight('POST,OPTIONS')
@API.route('/foidocument/<requesttype>/<requestid>/documentid/<documentid>/reclassify')
class ReclassifyFOIDocument(Resource):
    """Resource for reclassifying uploaded attachments of FOI requests."""

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def post(requesttype, requestid, documentid):
        try:
            requestjson = request.get_json()
            documentschema = ReclassifyDocumentSchema().load(requestjson)
            activedocuments = documentservice().getactiverequestdocuments(requestid, requesttype)
            documentpath = 'no documentpath found'
            if (requesttype == 'ministryrequest'):
                for document in activedocuments:
                    if document['foiministrydocumentid'] == int(documentid):
                        documentpath = document['documentpath']
            else:
                for document in activedocuments:
                    if document['foidocumentid'] == int(documentid):
                        documentpath = document['documentpath']

            # move document in S3
            moveresult = documentservice().copyrequestdocumenttonewlocation(documentschema['category'], documentpath)
            # save new version of document with updated documentpath
            if moveresult['status'] == 'success':
                 result = documentservice().createrequestdocumentversion(requestid, documentid, documentschema, AuthHelper.getuserid(), requesttype)
                 return {'status': result.success, 'message':result.message,'id':result.identifier} , 200
            return {'status': False, 'message': "Something went wrong moving the document's location" }, 500
        except ValidationError as err:
            return {'status': False, 'message': err}, 400
        except KeyError as error:
            return {'status': False, 'message': f"{error=}"}, 400
        except BusinessException as exception:
            return {'status': exception.status_code, 'message':exception.message}, 500

@cors_preflight('POST,OPTIONS')
@API.route('/foidocument/<requesttype>/<requestid>/documentid/<documentid>/replace')
class ReplaceFOIDocument(Resource):
    """Resource for managing FOI requests."""

       
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def post(requestid, documentid, requesttype):      
        try:
            requestjson = request.get_json() 
            documentschema = ReplaceDocumentSchema().load(requestjson)
            result = documentservice().createrequestdocumentversion(requestid, documentid, documentschema, AuthHelper.getuserid(), requesttype)
            return {'status': result.success, 'message':result.message,'id':result.identifier} , 200 
        except ValidationError as err:
            return {'status': False, 'message': err}, 400
        except KeyError as error:
            return {'status': False, 'message': f"{error=}"}, 400        
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500 
        
        
@cors_preflight('POST,OPTIONS')
@API.route('/foidocument/<requesttype>/<requestid>/documentid/<documentid>/delete')
class DeleteFOIDocument(Resource):
    """Resource for managing FOI requests."""

       
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def post(requestid, documentid, requesttype):      
        try:
            result = documentservice().deleterequestdocument(requestid, documentid, AuthHelper.getuserid(), requesttype)
            return {'status': result.success, 'message':result.message,'id':result.identifier} , 200 
        except KeyError as error:
            return {'status': False, 'message': f"{error=}"}, 400        
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500 