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
from request_api.utils.util import  cors_preflight, allowedorigins,str_to_bool,canrestictdata
from request_api.exceptions import BusinessException
from request_api.services.rawrequestservice import rawrequestservice
from request_api.services.documentservice import documentservice
from request_api.services.eventservice import eventservice
import json
import asyncio
from jose import jwt as josejwt
import holidays
from datetime import datetime, timedelta
import os
import pytz



API = Namespace('FOIRawRequests', description='Endpoints for FOI request management')
TRACER = Tracer.get_instance()
with open('request_api/schemas/schemas/rawrequest.json') as f:
        schema = json.load(f)

INVALID_REQUEST_ID = 'Invalid Request Id'

SHORT_DATE_FORMAT = '%Y-%m-%d'
LONG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

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
            statuscode = 401
            requestidisinteger = int(requestid)
            if requestidisinteger :                
                baserequestinfo = rawrequestservice().getrawrequest(requestid)

                assignee = baserequestinfo['assignedTo']
                isiaorestricted = baserequestinfo['isiaorestricted']
                # print('Request # {0} Assigned to {1} and is restricted {2} '.format(requestid,assignee,isiaorestricted))
                if(isiaorestricted and canrestictdata(requestid,assignee,isiaorestricted,True)):
                    jsondata = {'status': 401, 'message':'Restricted Request'}
                    statuscode = 401
                else:
                    jsondata = json.dumps(baserequestinfo)
                    statuscode = 200

            return jsondata , statuscode 
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
            requestdata = getparams(updaterequest)
            assigneegroup = requestdata['assigneegroup']
            assignee = requestdata['assignee']
            assigneefirstname = requestdata['assigneefirstname']
            assigneemiddlename = requestdata['assigneemiddlename']
            assigneelastname = requestdata['assigneelastname']

            if int(requestid) and str(requestid) != "-1" :
                status = rawrequestservice().getstatus(updaterequest)
                if status not in ['Intake in Progress', 'Closed', 'Redirect', 'Peer Review', 'Section 5 Pending', 'On-Hold - Application Fee']:
                    raise ValueError('Invalid request state.')
                result = rawrequestservice().saverawrequestversion(updaterequest,requestid,assigneegroup,assignee,status,AuthHelper.getuserid(),assigneefirstname,assigneemiddlename,assigneelastname, actiontype)                
                assignee = ''
                if(actiontype == 'assignee'):
                    assignee = getassignee(assigneefirstname,assigneelastname,assigneegroup)                  
                asyncio.ensure_future(eventservice().postevent(requestid,"rawrequest",AuthHelper.getuserid(), AuthHelper.getusername(), AuthHelper.isministrymember(),assignee))
                if result.success == True:
                    rawrequestservice().posteventtoworkflow(result.identifier, updaterequest, status)
                    return {'status': result.success, 'message':result.message}, 200
            elif int(requestid) and str(requestid) == "-1":
                result = rawrequestservice().saverawrequest(updaterequest,"intake",AuthHelper.getuserid(),notes="Request submitted from FOI Flow")
                if result.success == True:
                    assignee = getassignee(assigneefirstname,assigneelastname,assigneegroup)
                    asyncio.ensure_future(eventservice().postevent(result.identifier,"rawrequest",AuthHelper.getuserid(),AuthHelper.getusername(),AuthHelper.isministrymember(),assignee))
                    return {'status': result.success, 'message':result.message,'id':result.identifier} , 200                
        except ValueError as valuexception:
            return {'status': 500, 'message':str(valuexception)}, 500
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500

def getassignee(assigneefirstname,assigneelastname,assigneegroup):
    if(assigneefirstname !='' and assigneelastname!=''):
        return  "{0}, {1}".format(assigneelastname,assigneefirstname)
    else: 
        return  assigneegroup

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
                asyncio.ensure_future(eventservice().postevent(result.identifier,"rawrequest",userid,username,False,''))
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

            #add received date to json
            receiveddatetext = requestdatajson["receivedDateUF"] if 'receivedDateUF' in requestdatajson else datetime.now(pytz.timezone("America/Vancouver")).strftime(LONG_DATE_FORMAT)
            receiveddate = _skiptoworkday(receiveddatetext, 0)
            requestdatajson['receivedDate'] = receiveddate.strftime(SHORT_DATE_FORMAT)
            requestdatajson['receivedDateUF'] = receiveddate.strftime(LONG_DATE_FORMAT)

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


def _skiptoworkday(datetimevalue, extradiff=0):
    """skip weekend, holiday, weekdays (after 16:30)"""
    receiveddate = datetime.strptime(datetimevalue, LONG_DATE_FORMAT) if isinstance(datetimevalue, str) else datetimevalue

    ca_holidays = _getholidays()
    diff = 0
    if receiveddate.isoweekday() in [6, 7]: #weekend - add 1 day
        diff += 1
        if _isholiday(receiveddate.strftime(SHORT_DATE_FORMAT), ca_holidays): #holiday in weekend - add an extra day
            extradiff += 1
    else:
        if _isholiday(receiveddate.strftime(SHORT_DATE_FORMAT), ca_holidays): #holiday in weekdays - add 1 day
            diff += 1
        else: # submitted after 16:30 in weekdays
            if receiveddate.hour > 16 or (receiveddate.hour == 16 and receiveddate.minute > 30):
                diff += 1
            else:
                receiveddate += timedelta(days=extradiff)
                return receiveddate

    receiveddate += timedelta(days=diff)
    receiveddate = receiveddate.replace(hour=0, minute=0, second=0, microsecond=0) #reset time
    return _skiptoworkday(receiveddate, extradiff)

def _getholidays():        
    ca_holidays = []
    for date, name in sorted(holidays.CA(prov='BC', years=datetime.today().year).items()):
        ca_holidays.append(date.strftime(SHORT_DATE_FORMAT))
    if 'FOI_ADDITIONAL_HOLIDAYS' in os.environ and os.getenv('FOI_ADDITIONAL_HOLIDAYS') != '':
        _addldays = os.getenv('FOI_ADDITIONAL_HOLIDAYS')
        for _addlday in _addldays.split(","):
            ca_holidays.append(_addlday.strip().replace('XXXX',str(datetime.today().year)))

    if 'FOI_INVALID_HOLIDAYS' in os.environ and os.getenv('FOI_INVALID_HOLIDAYS') != '': #remove dec 24, dec 27 from holidays
        _invaliddays = os.getenv('FOI_INVALID_HOLIDAYS')
        for _invalidday in _invaliddays.split(","):
            if _invalidday in ca_holidays:
                ca_holidays.remove(_invalidday.strip().replace('XXXX',str(datetime.today().year)))
    
    return ca_holidays

def _isholiday(input, ca_holidays):
    return input in ca_holidays   

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

@cors_preflight('GET,POST,OPTIONS')
@API.route('/foirawrequest/restricted/<requestid>')
class FOIRawRequestIAORestricted(Resource):

    @staticmethod    
    @cross_origin(origins=allowedorigins())
    @auth.require
    def post(requestid=None):
        try :            
            if int(requestid) and str(requestid) != "-1" :
                request_json = request.get_json()                
                _isiaorestricted = request_json['isrestricted'] if request_json['isrestricted'] is not None else False                
                isiaorestricted = str_to_bool(_isiaorestricted)
                result = rawrequestservice().saverawrequestiaorestricted(requestid,isiaorestricted,AuthHelper.getuserid())
                if result.success:
                  return {'status': result.success, 'message':result.message,'id':result.identifier} , 200
                else:
                  return {'status': result.success, 'message':result.message,'id':result.identifier} , 500  
        except ValueError:
            return {'status': 500, 'message':"Invalid Request"}, 400    
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500  