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
from sqlalchemy.sql.elements import Null
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
@API.route('/foirawrequest/<requestid>')
class FOIRequest(Resource):
    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')   
    def get(requestid):
        try :
            request = FOIRawRequest.get_request(requestid)

            requestrawdata = request['requestrawdata']
            requestType = requestrawdata['requestType']['requestType']
            ispersonal = True if requestType == 'personal' else False
            contactInfo = requestrawdata.get('contactInfo')
            decriptionTimeframe = requestrawdata.get('descriptionTimeframe')
            contactInfoOptions = requestrawdata.get('contactInfoOptions')
            _createdDate = parse(request['created_at'])

            baserequestInfo = {'id' : request['requestid'] ,
                        'requestType':requestType,
                        'firstName':contactInfo['firstName'],
                        'middleName':requestrawdata['contactInfo']['middleName'],
                        'lastName':contactInfo['lastName'],
                        'businessName':contactInfo['businessName'],                        
                        'currentState':'Unopened',#request['created_at']
                        'receivedDate':_createdDate.strftime('%Y %b, %d'),
                        'receivedDateUF':request['created_at'],
                        'assignedTo': "Unassigned",
                        'xgov':'No',
                        'idNumber': 'U-00'+ str(request['requestid']),
                        'email':contactInfoOptions['email'],
                        'phonePrimary':contactInfoOptions['phonePrimary'],
                        'phoneSecondary':contactInfoOptions['phoneSecondary'],
                        'address':contactInfoOptions['address'],
                        'city':contactInfoOptions['city'],
                        'postal':contactInfoOptions['postal'],
                        'province':contactInfoOptions['province'],
                        'country':contactInfoOptions['country'],
                        'description':decriptionTimeframe['description'],
                        'fromDate':decriptionTimeframe['fromDate'],
                        'correctionalServiceNumber':decriptionTimeframe['correctionalServiceNumber'],
                        'publicServiceEmployeeNumber':decriptionTimeframe['publicServiceEmployeeNumber'],
                        'topic':decriptionTimeframe['topic'],
                        'selectedMinistries':requestrawdata['ministry']['selectedMinistry'],
                        }

            if ispersonal:
                childInformation = requestrawdata.get('childInformation')
                anotherpersonInformation = requestrawdata.get('anotherInformation')                                   
                adoptiveParents = requestrawdata.get('adoptiveParents')
               
                haschildInfo = True if childInformation != None  else False
                hasanotherpersonInfo = True if anotherpersonInformation != None  else False
                hasadoptiveParentInfo = True if   adoptiveParents != None else False

                additionalpersonalInfo =  {
                            'alsoKnownAs':contactInfo['alsoKnownAs'],
                            'requestFor':requestrawdata['selectAbout'],
                            'birthDate':contactInfo['birthDate'] ,
                            
                            'childFirstName':childInformation['firstName'] if haschildInfo   else '',
                            'childmiddleName':childInformation['middleName'] if haschildInfo else '',
                            'childlastName':childInformation['lastName'] if haschildInfo else '',
                            'childalsoKnownAs':childInformation['alsoKnownAs'] if haschildInfo else '',                    
                            'childbirthDate':childInformation['dateOfBirth'] if haschildInfo else '',

                            'anotherFirstName':anotherpersonInformation['firstName'] if hasanotherpersonInfo else '',
                            'anothermiddleName':anotherpersonInformation['middleName'] if hasanotherpersonInfo else '',
                            'anotherastName':anotherpersonInformation['lastName'] if hasanotherpersonInfo else '',
                            'anotheralsoKnownAs':anotherpersonInformation['alsoKnownAs'] if hasanotherpersonInfo else '',
                            'anotherbirthDate':anotherpersonInformation['dateOfBirth'] if hasanotherpersonInfo else '',

                            'adoptiveMotherFirstName' : adoptiveParents['motherFirstName'] if hasadoptiveParentInfo else '',
                            'adoptiveMotherLastName' : adoptiveParents['motherLastName'] if hasadoptiveParentInfo else '',
                            'adoptiveFatherLastName' : adoptiveParents['fatherLastName'] if hasadoptiveParentInfo else '',
                            'adoptiveFatherFirstName' : adoptiveParents['fatherFirstName'] if hasadoptiveParentInfo else ''
                        } 
                baserequestInfo['additionalpersonalInfo'] = additionalpersonalInfo        
            
            jsondata = json.dumps(baserequestInfo)
            return jsondata , 200  
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 50

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
                requests = FOIRawRequest.getrequests()
                unopenedrequests =[]
                for  request in requests:
                    _createdDate = parse(request['created_at'])                
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
                data = {}
                data['id'] = result.identifier
                json_data = json.dumps(data)
                asyncio.run(redispubservice.publishtoredischannel(json_data))
            return {'status': result.success, 'message':result.message} , 200
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500