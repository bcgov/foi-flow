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

import re
from flask import g, request
from flask_restx import Namespace, Resource, cors
from flask_expects_json import expects_json

from request_api.tracer import Tracer
from request_api.utils.util import  cors_preflight
from request_api.exceptions import BusinessException, Error
from request_api.services.rawrequestservice import rawrequestservice
import json
import uuid

API = Namespace('FOIRawRequests', description='Endpoints for FOI request management')
TRACER = Tracer.get_instance()

@cors_preflight('GET,POST,OPTIONS')
@API.route('/foirawrequest/<requestid>')
class FOIRawRequest(Resource):

    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')       
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


@cors_preflight('GET,POST,PUT,OPTIONS')
@API.route('/foirawrequestbpm/addwfinstanceid/<_requestid>')
class FOIRawRequestBPMProcess(Resource):

    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')  ##todo: This will get replaced with Allowed Origins
    def put(_requestid=None):
            request_json = request.get_json()
            try:

                _wfinstanceid = request_json['wfinstanceid']
                               
                requestid = int(_requestid)
                wfinstanceid = uuid.UUID(_wfinstanceid, version=4)
                result = rawrequestservice.updateworkflowinstance(wfinstanceid,requestid)

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
    @cors.crossdomain(origin='*')   
    def get(requestid=None):
        ## todo : This code will get re-furshibed with BPM WF validation to list
        try:                                       
                unopenedrequests = rawrequestservice.getrawrequests()     
                jsondata = json.dumps(unopenedrequests)
                return jsondata , 200            
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500     

    with open('request_api/schemas/schemas/rawrequest.json') as f:
        schema = json.load(f)

    

    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')  ##todo: This will get replaced with Allowed Origins
    @expects_json(schema)
    def post():
        """ POST Method for capturing RAW FOI requests before processing"""
        try:
            request_json = request.get_json()
            requestdatajson = request_json['requestData']           
            result = rawrequestservice.saverawrequest(requestdatajson)
            return {'status': result.success, 'message':result.message,'id':result.identifier} , 200
        except TypeError:
            return {'status': "TypeError", 'message':"Error while parsing JSON in request"}, 500   
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500