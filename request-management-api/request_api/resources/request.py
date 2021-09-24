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
from flask_restx import Namespace, Resource
from flask_expects_json import expects_json
from flask_cors import cross_origin
from request_api.auth import auth, AuthHelper
from request_api.tracer import Tracer
from request_api.utils.util import  cors_preflight, allowedOrigins
from request_api.exceptions import BusinessException, Error
from request_api.services.rawrequestservice import rawrequestservice
from request_api.services.dashboardservice import dashboardservice
from request_api.services.external.bpmservice import bpmservice
import json
import uuid
from jose import jwt as josejwt

API = Namespace('FOIRawRequests', description='Endpoints for FOI request management')
TRACER = Tracer.get_instance()
with open('request_api/schemas/schemas/rawrequest.json') as f:
        schema = json.load(f)

@cors_preflight('GET,POST,OPTIONS')
@API.route('/foirawrequest/<requestid>')
class FOIRawRequest(Resource):

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedOrigins())       
    @auth.require
    def get(requestid=None):
        try : 
            jsondata = {}
            requestidisInteger = int(requestid)
            if requestidisInteger :                
                baserequestInfo = rawrequestservice.getrawrequest(requestid)                                    
                jsondata = json.dumps(baserequestInfo)
            return jsondata , 200 
        except ValueError:
            return {'status': 500, 'message':"Invalid Request Id"}, 500    
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500

    @staticmethod
    #@Tracer.trace()
    @cross_origin(origins=allowedOrigins())
    @auth.require
    def post(requestid=None):
        try :                        
            updaterequest = request.get_json()
                        
            if int(requestid) and str(requestid) != "-1" :
                status = 'Assignment in progress' 
                
                try:
                    #TODO:Need to refine this logic from ENUM
                    if(updaterequest["requeststatusid"] is not None and updaterequest["requeststatusid"] == 4):                    
                        status = 'Redirect'

                    if(updaterequest["requeststatusid"] is not None and updaterequest["requeststatusid"] == 3):                    
                        status = 'Closed'    
                except  KeyError:
                    print("Key Error on requeststatusid, ignore will be intake in progress")    
                
                rawRequest = rawrequestservice.getrawrequest(requestid)     
                assigneeGroup = updaterequest["assignedGroup"] if 'assignedGroup' in updaterequest  else None
                assignee = updaterequest["assignedTo"] if 'assignedTo' in updaterequest  else None                                         
                result = rawrequestservice.saverawrequestversion(updaterequest,requestid,assigneeGroup, assignee,status,AuthHelper.getUserId())                
                if result.success == True:   
                    rawrequestservice.postEventToWorkflow(result.identifier , rawRequest['wfinstanceid'], assigneeGroup, assignee, status)
                    return {'status': result.success, 'message':result.message}, 200
            elif int(requestid) and str(requestid) == "-1":
                result = rawrequestservice.saverawrequest(updaterequest,"intake",AuthHelper.getUserId())               
                return {'status': result.success, 'message':result.message,'id':result.identifier} , 200
        except ValueError:
            return {'status': 500, 'message':"Invalid Request Id"}, 500    
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500

@cors_preflight('GET,POST,PUT,OPTIONS')
@API.route('/foirawrequestbpm/addwfinstanceid/<_requestid>')
class FOIRawRequestBPMProcess(Resource):

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedOrigins())
    @auth.require
    def put(_requestid=None):
            request_json = request.get_json()
            try:

                _wfinstanceid = request_json['wfinstanceid']
                status = request_json['status'] if request_json.get('status') is not None else 'unopened'
                notes = request_json['notes'] if request_json.get('notes') is not None else 'Workflow Update'
                requestid = int(_requestid)                                                               
                result = rawrequestservice.updateworkflowinstancewithstatus(_wfinstanceid,requestid,status,notes,AuthHelper.getUserId())
                if result.identifier != -1 :                
                    return {'status': result.success, 'message':result.message}, 200
                else:
                    return {'status': result.success, 'message':result.message}, 404
            except KeyError as keyexception:
                return {'status': "Invalid PUT request", 'message':"Key Error on JSON input, please confirm requestid and wfinstanceid"}, 500
            except ValueError as valuexception:
                return {'status': "BAD Request", 'message': str(valuexception)}, 500           
                       
@cors_preflight('GET,POST,OPTIONS')
@API.route('/foirawrequests')
class FOIRawRequests(Resource):
    """Resource for managing FOI Raw requests."""
    
    
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedOrigins())
    @expects_json(schema)
    def post():
        """ POST Method for capturing RAW FOI requests before processing"""
        try:
            request_json = request.get_json()
            requestdatajson = request_json['requestData']           
            result = rawrequestservice.saverawrequest(requestdatajson,"onlineform",None)
            return {'status': result.success, 'message':result.message,'id':result.identifier} , 200
        except TypeError:
            return {'status': "TypeError", 'message':"Error while parsing JSON in request"}, 500   
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500