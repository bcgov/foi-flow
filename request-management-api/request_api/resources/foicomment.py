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
from request_api.auth import auth, AuthHelper
from request_api.services.eventservice import eventservice
from request_api.tracer import Tracer
from request_api.utils.util import  cors_preflight, allowedorigins,canrestictdata
from request_api.exceptions import BusinessException, Error
from request_api.services.commentservice import commentservice
from request_api.services.rawrequestservice import rawrequestservice
from request_api.schemas.foicomment import  FOIRawRequestCommentSchema, FOIMinistryRequestCommentSchema
from request_api.schemas.foicomment import  EditFOIRawRequestCommentSchema, FOIMinistryRequestCommentSchema
from request_api.services.assigneeservice import assigneeservice
from request_api.services.watcherservice import watcherservice
import json
from flask_cors import cross_origin
import asyncio

API = Namespace('FOIComment', description='Endpoints for FOI Comment management')
TRACER = Tracer.get_instance()
"""Custom exception messages
"""
EXCEPTION_MESSAGE_BAD_REQUEST='Bad Request'
        
@cors_preflight('POST,OPTIONS')
@API.route('/foicomment/ministryrequest')
class CreateFOIRequestComment(Resource):
    """Creates comment for ministry(opened) request."""

       
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def post():      
        try:
            requestjson = request.get_json() 
            minrquescommentschema = FOIMinistryRequestCommentSchema().load(requestjson)  
            result = commentservice().createministryrequestcomment(minrquescommentschema, AuthHelper.getuserid())
            if result.success == True:
                asyncio.ensure_future(eventservice().postcommentevent(result.identifier, "ministryrequest", AuthHelper.getuserid()))
            return {'status': result.success, 'message':result.message,'id':result.identifier} , 200 
        except KeyError as err:
            return {'status': False, 'message':err.messages}, 400        
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500 

@cors_preflight('POST,OPTIONS')
@API.route('/foicomment/rawrequest')
class CreateFOIRawRequestComment(Resource):
    """Creates comment for raw(unopened) request."""

     
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def post():      
        try:
            requestjson = request.get_json() 
            rawrqcommentschema = FOIRawRequestCommentSchema().load(requestjson)  
            result = commentservice().createrawrequestcomment(rawrqcommentschema, AuthHelper.getuserid())
            if result.success == True:
                asyncio.ensure_future(eventservice().postcommentevent(result.identifier, "rawrequest", AuthHelper.getuserid()))
            return {'status': result.success, 'message':result.message,'id':result.identifier} , 200
        except KeyError as err:
            return {'status': False, 'message':err.messages}, 400        
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500 
        
@cors_preflight('GET,OPTIONS')
@API.route('/foicomment/<requesttype>/<requestid>')
class FOIComment(Resource):
    """Retrieves comment based on type: ministry(opened) and raw(unopened)."""

       
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def get(requesttype, requestid):      
        if requesttype != "ministryrequest" and requesttype != "rawrequest":
                return {'status': False, 'message': EXCEPTION_MESSAGE_BAD_REQUEST}, 400 
        try:
            _canrestrictdata = False
            if requesttype == "ministryrequest":
                result = commentservice().getministryrequestcomments(requestid)
            else:
                baserequestinfo = rawrequestservice().getrawrequest(requestid)
                _canrestrictdata = canrestictdata(requestid,baserequestinfo['assignedTo'],baserequestinfo['isiaorestricted'],True)
                result = commentservice().getrawrequestcomments(requestid)
            
            if(_canrestrictdata == False):
                return json.dumps(result), 200
            else:
                return {'status': 401, 'message':'Restricted Request'} , 401
        except KeyError as err:
            return {'status': False, 'message':err.messages}, 400        
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500   
        


@cors_preflight('PUT,OPTIONS')
@API.route('/foicomment/<requesttype>/<commentid>/disable')
class FOIDisableComment(Resource):
    """Disable comment based on type: ministry(opened) and raw(unopened)."""

      
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def put(requesttype, commentid):      
        if requesttype != "ministryrequest" and requesttype != "rawrequest":
                return {'status': False, 'message': EXCEPTION_MESSAGE_BAD_REQUEST}, 400 
        try:
            if requesttype == "ministryrequest":
                result = commentservice().disableministryrequestcomment(commentid, AuthHelper.getuserid())
            else:
                result = commentservice().disablerawrequestcomment(commentid, AuthHelper.getuserid())
            if result.success == True:
                asyncio.ensure_future(eventservice().postcommentevent(result.identifier, requesttype, AuthHelper.getuserid(), True))
            return {'status': result.success, 'message':result.message,'id':result.identifier} , 200 
        except KeyError as err:
            return {'status': False, 'message':err.messages}, 400        
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500
        

@cors_preflight('PUT,OPTIONS')
@API.route('/foicomment/<requesttype>/<commentid>')
class FOIUpdateComment(Resource):
    """Update comment based on type: ministry(opened) and raw(unopened)."""

      
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def put(requesttype, commentid):      
        if requesttype != "ministryrequest" and requesttype != "rawrequest":
                return {'status': False, 'message': EXCEPTION_MESSAGE_BAD_REQUEST}, 400 
        try:
            requestjson = request.get_json()              
            if requesttype == "ministryrequest":
                commentschema = FOIMinistryRequestCommentSchema().load(requestjson)
                result = commentservice().updateministryrequestcomment(commentid, commentschema, AuthHelper.getuserid())
            else:
                commentschema = EditFOIRawRequestCommentSchema().load(requestjson)
                result = commentservice().updaterawrequestcomment(commentid, commentschema, AuthHelper.getuserid())
            return {'status': result.success, 'message':result.message,'id':result.identifier} , 200 
        except KeyError as err:
            return {'status': False, 'message':err.messages}, 400        
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500


# @cors_preflight('GET,OPTIONS')
# @API.route('/foicomment/ministryrequest/<ministryrequestid>/restricted')
# class FOIRestrictedRequestTagList(Resource):

#     @staticmethod    
#     @cross_origin(origins=allowedorigins())
#     @auth.require
#     def get(ministryrequestid=None):
#         try :            
#              result = assigneeservice().getmembersbygroupname(groupname) 
#              result = watcherservice().getministryrequestwatchers(ministryrequestid,AuthHelper.isministrymember())
#              #request = FOIRequest.getrequest(foirequestid)

#         except ValueError:
#             return {'status': 500, 'message':"Invalid Request"}, 400    
#         except BusinessException as exception:            
#             return {'status': exception.status_code, 'message':exception.message}, 500 

@cors_preflight('GET,OPTIONS')
@API.route('/foicomment/rawrequest/<requestid>/restricted')
class FOIRestrictedRequestTagList(Resource):

    @staticmethod    
    @cross_origin(origins=allowedorigins())
    @auth.require
    def get(requestid=None):
        try :       
            watchers = watcherservice().getrawrequestwatchers(requestid)
            baserequestinfo = rawrequestservice().getrawrequest(requestid)
            result = commentservice().createcommenttagginguserlist(watchers, baserequestinfo)
            #request = FOIRequest.getrequest(foirequestid)
            return json.dumps(result), 200
        except ValueError:
            return {'status': 500, 'message':"Invalid Request"}, 400    
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500 