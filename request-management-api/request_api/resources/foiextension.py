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


from sqlalchemy.log import Identified
from flask import g, request
from flask_restx import Namespace, Resource, cors
from flask_expects_json import expects_json
from request_api.auth import auth
from request_api.auth import auth, AuthHelper
from request_api.tracer import Tracer
from request_api.utils.util import  cors_preflight, allowedorigins, getgroupsfromtoken, getrequiredmemberships
from request_api.utils.enums import UserGroup
from request_api.exceptions import BusinessException, Error
from request_api.services.extensionservice import extensionservice
from request_api.schemas.foiextension import  FOIRequestExtensionSchema

import json
from flask_cors import cross_origin


API = Namespace('FOIExtension', description='Endpoints for FOI Extension management')
TRACER = Tracer.get_instance()
"""Custom exception messages
"""
EXCEPTION_MESSAGE_BAD_REQUEST='Bad Request'

@cors_preflight('GET,OPTIONS')
@API.route('/foiextension/ministryrequest/<requestid>')
class GetFOIExtensions(Resource):
    """Resource for managing FOI requests."""

       
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def get(requestid):
        try:
            extensionrecords = extensionservice().getrequestextensions(requestid)            
            return json.dumps(extensionrecords), 200
        except KeyError as err:
            return {'status': False, 'message':err.messages}, 400        
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500 
        
@cors_preflight('POST,OPTIONS')
@API.route('/foiextension/foirequest/<requestid>/ministryrequest/<ministryrequestid>')
class CreateFOIRequestExtension(Resource):
    """Creates extension for ministry(opened) request."""

       
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @auth.ismemberofgroups(getrequiredmemberships())
    def post(requestid, ministryrequestid):      
        try:
            statuscode = 200
            groups = getgroupsfromtoken()   
            requestjson = request.get_json()
            rquesextensionschema = FOIRequestExtensionSchema().load(requestjson)
            if (UserGroup.intake.value in groups or UserGroup.flex.value in groups or UserGroup.processing.value in groups):           
                result = extensionservice().createrequestextension(requestid, ministryrequestid, rquesextensionschema, AuthHelper.getuserid())
                success = result.success
                message = result.message
                identifier = result.identifier
            else:
                statuscode = 401
                success = False
                message = 'Unautherized user'
                identifier = -1
            return {'status': success, 'message':message,'id':identifier} , statuscode 
        except KeyError as err:
            return {'status': False, 'message':err.messages}, 400        
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500 

@cors_preflight('POST,OPTIONS')
@API.route('/foiextension/<ministryrequestid>/<extensionid>/edit')#/foidocument/<requesttype>/<requestid>/documentid/<documentid>/replace
class EditFOIRequestExtension(Resource):
    """Edits extension for ministry(opened) request."""

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @auth.ismemberofgroups(getrequiredmemberships())
    def post(ministryrequestid, extensionid):      
        try:
            statuscode = 200
            groups = getgroupsfromtoken()   
            requestjson = request.get_json()
            rquesextensionschema = FOIRequestExtensionSchema().load(requestjson)
            if (UserGroup.intake.value in groups or UserGroup.flex.value in groups or UserGroup.processing.value in groups):           
                result = extensionservice().createrequestextensionversion(ministryrequestid, extensionid, rquesextensionschema, AuthHelper.getuserid())
                success = result.success
                message = result.message
                identifier = result.identifier
            else:
                statuscode = 401
                success = False
                message = 'Unautherized user'
                identifier = -1
            return {'status': success, 'message':message,'id':identifier} , statuscode 
        except KeyError as err:
            return {'status': False, 'message':err.messages}, 400        
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500 