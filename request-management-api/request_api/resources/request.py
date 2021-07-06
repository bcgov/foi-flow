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
from request_api.tracer import Tracer
from request_api.utils.util import  cors_preflight
from request_api.exceptions import BusinessException, Error

from request_api.models.FOIRawRequests import FOIRawRequest
from flask_expects_json import expects_json
import json
#import redis
import asyncio
from request_api.utils.redispublisher import RedisPublisherService
from dateutil.parser import *
from datetime import datetime

API = Namespace('FOIRawRequests', description='Endpoints for FOI request management')
TRACER = Tracer.get_instance()
redispubservice = RedisPublisherService()

@cors_preflight('GET,POST,OPTIONS')
@API.route('/foirawrequests')
class FOIRawRequests(Resource):
    """Resource for managing FOI Raw requests."""

    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    def get():
        ## todo : This code will get re-furshibed with BPM WF validation to list
        try:
            requests = FOIRawRequest.getrequests()
            unopenedrequests =[]
            for  request in requests:
                _createdDate = parse(request['created_at'],)
                #print(_createdDate.strftime('%Y %b, %d'))
                unopenrequest= {'id' : request['requestid'] ,
                'firstName':request['requestrawdata']['contactInfo']['firstName'],
                 'lastName':request['requestrawdata']['contactInfo']['lastName'],
                 'requestType':request['requestrawdata']['requestType']['requestType'],
                 'currentState':'Unopened',#request['created_at']
                 'receivedDate':_createdDate.strftime('%Y %b, %d'),
                 'receivedDateUF':request['created_at'],
                 'assignedTo': "Unassigned",
                 'xgov':'No',
                 'idNumber': 'U-00'+ str(request['requestid'])
                 }
                unopenedrequests.append(unopenrequest)
                  
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
            result = FOIRawRequest.saverawrequest(requestdatajson)
            if(result.success):            
                asyncio.run(redispubservice.publishtoredischannel(result.identifier))       
            return {'status': result.success, 'message':result.message} , 200
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500