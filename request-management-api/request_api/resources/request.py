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
from request_api.utils.util import  cors_preflight, allowedorigins
from request_api.exceptions import BusinessException
from request_api.services.rawrequestservice import rawrequestservice
from request_api.services.documentservice import documentservice
from request_api.services.eventservice import eventservice
import json
from jose import jwt as josejwt
from request_api.services.asyncwrapperservice import asyncwrapperservice

API = Namespace('FOIRawRequests', description='Endpoints for FOI request management')
TRACER = Tracer.get_instance()
with open('request_api/schemas/schemas/rawrequest.json') as f:
        schema = json.load(f)

INVALID_REQUEST_ID = 'Invalid Request Id'

@cors_preflight('GET,POST,OPTIONS')
@API.route('/foirawrequest/<requestid>')
@API.route('/foirawrequest/<requestid>/<string:actiontype>')
class FOIRawRequest(Resource):
    """Consolidates create and retrival of raw request"""

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())       
    @auth.require
    def get(requestid=None):
        try : 
            jsondata = {}
            requestidisinteger = int(requestid)
            if requestidisinteger :                
                baserequestinfo = rawrequestservice().getrawrequest(requestid)                                    
                jsondata = json.dumps(baserequestinfo)
            return jsondata , 200 
        except ValueError:
            return {'status': 500, 'message':INVALID_REQUEST_ID}, 500    
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500

    @staticmethod
    #@Tracer.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def post(requestid=None, actiontype=None):
        try :                        
            updaterequest = request.get_json()
            if int(requestid) and str(requestid) != "-1" :
                status = rawrequestservice().getstatus(updaterequest)
                rawrequest = rawrequestservice().getrawrequest(requestid)
                requestdata = getparams(updaterequest)

                assigneegroup = requestdata['assigneegroup']
                assignee = requestdata['assignee']
                assigneefirstname = requestdata['assigneefirstname']
                assigneemiddlename = requestdata['assigneemiddlename']
                assigneelastname = requestdata['assigneelastname']
                result = rawrequestservice().saverawrequestversion(updaterequest,requestid,assigneegroup,assignee,status,AuthHelper.getuserid(),assigneefirstname,assigneemiddlename,assigneelastname, actiontype)
                asyncwrapperservice().postevent(requestid,"rawrequest",AuthHelper.getuserid(), AuthHelper.getusername(), AuthHelper.isministrymember())
                if result.success == True:
                    rawrequestservice().posteventtoworkflow(result.identifier, rawrequest['wfinstanceid'], updaterequest, status)
                    return {'status': result.success, 'message':result.message}, 200
            elif int(requestid) and str(requestid) == "-1":
                result = rawrequestservice().saverawrequest(updaterequest,"intake",AuthHelper.getuserid(),notes="Request submitted from FOI Flow")
                if result.success == True:
                    asyncwrapperservice().postevent(result.identifier,"rawrequest",AuthHelper.getuserid(),AuthHelper.getusername(),AuthHelper.isministrymember())
                    return {'status': result.success, 'message':result.message,'id':result.identifier} , 200                
        except ValueError:
            return {'status': 500, 'message':INVALID_REQUEST_ID}, 500    
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500
    
def getparams(updaterequest):
    return {
        'assigneegroup': updaterequest["assignedGroup"] if 'assignedGroup' in updaterequest  else None,
        'assignee': updaterequest["assignedTo"] if 'assignedTo' in updaterequest else None,
        'assigneefirstname': updaterequest["assignedToFirstName"] if updaterequest.get("assignedToFirstName") != None else None,
        'assigneemiddlename': updaterequest["assignedToMiddleName"] if updaterequest.get("assignedToMiddleName") != None else None,
        'assigneelastname': updaterequest["assignedToLastName"] if updaterequest.get("assignedToLastName") != None else None
    }

@cors_preflight('GET,OPTIONS')
@API.route('/foirawrequest/axisrequestid/<axisrequestid>')
class FOIAXISRequest(Resource):
    """Check if axis request id already exists in db"""

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())       
    @auth.require
    def get(axisrequestid=None):
        try : 
            isaxisrequestidpresent = rawrequestservice().isaxisrequestidpresent(axisrequestid)                                   
            return {"axisrequestid" : axisrequestid, "ispresent": isaxisrequestidpresent}, 200
        except ValueError:
            return {'status': 500, 'message':INVALID_REQUEST_ID}, 500    
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500

@cors_preflight('GET,POST,OPTIONS')
@API.route('/foirawrequest/loadtest/<requestid>')
class FOIRawRequestLoadTest(Resource):
    """Consolidates create and retrival of raw request"""

    @staticmethod
    #@Tracer.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def post(requestid=None):
        try:
            updaterequest = request.get_json()
            userid = updaterequest['assignedTo']
            username = 'Super Tester'
            if int(requestid) and str(requestid) == "-1":
                result = rawrequestservice().saverawrequest(updaterequest,"intake",userid,notes="Request submitted from FOI Flow")               
                asyncwrapperservice().postevent(result.identifier,"rawrequest",userid,username,False)
                return {'status': result.success, 'message':result.message,'id':result.identifier} , 200
        except ValueError:
            return {'status': 400, 'message':INVALID_REQUEST_ID}, 400    
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500


@cors_preflight('GET,POST,PUT,OPTIONS')
@API.route('/foirawrequestbpm/addwfinstanceid/<_requestid>')
class FOIRawRequestBPMProcess(Resource):
    """Updates raw request"""
    
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def put(_requestid=None):
            request_json = request.get_json()
            try:

                _wfinstanceid = request_json['wfinstanceid']
                notes = request_json['notes'] if request_json.get('notes') is not None else 'Workflow Update'
                requestid = int(_requestid)                                                               
                result = rawrequestservice().updateworkflowinstancewithstatus(_wfinstanceid,requestid,notes,AuthHelper.getuserid())
                if result.identifier != -1 :                
                    return {'status': result.success, 'message':result.message}, 200
                else:
                    return {'status': result.success, 'message':result.message}, 404
            except KeyError:
                return {'status': "Invalid PUT request", 'message':"Key Error on JSON input, please confirm requestid and wfinstanceid"}, 500
            except ValueError as valuexception:
                return {'status': "BAD Request", 'message': str(valuexception)}, 500           
                       
@cors_preflight('GET,POST,OPTIONS')
@API.route('/foirawrequests')
class FOIRawRequests(Resource):
    """Resource for retriving all raw requests."""
     
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @expects_json(schema)
    def post():
        """ POST Method for capturing RAW FOI requests before processing"""
        try:
            request_json = request.get_json()
            requestdatajson = request_json['requestData']  
            #get attachments
            attachments = requestdatajson['Attachments'] if 'Attachments' in requestdatajson else None
            notes = 'Request submission from FOI WebForm'
            #save request
            if attachments is not None:
                requestdatajson.pop('Attachments')
            result = rawrequestservice().saverawrequest(requestdatajson=requestdatajson,sourceofsubmission="onlineform",userid=None,notes=notes)
            if result.success:
                documentservice().uploadpersonaldocuments(result.identifier, attachments)                   
            return {'status': result.success, 'message':result.message,'id':result.identifier} , 200
        except TypeError:
            return {'status': "TypeError", 'message':"Error while parsing JSON in request"}, 500   
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500
        
@cors_preflight('GET,OPTIONS')
@API.route('/foirawrequest/<requestid>/fields')
class FOIRawRequestFields(Resource):
    """Consolidates create and retrival of raw request"""

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())       
    @auth.require
    def get(requestid):
        try : 
            # here we want to get the value of names (i.e. ?names=ministries)
            if request.args['names'] == "ministries":
                baserequestinfo = rawrequestservice().getrawrequestfields(requestid,["ministries"])                                    
                return json.dumps(baserequestinfo), 200
        except ValueError:
            return {'status': 500, 'message':"Invalid Request"}, 400    
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500