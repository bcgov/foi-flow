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
from request_api.services.eventservice import eventservice
from request_api.tracer import Tracer
from request_api.utils.util import  cors_preflight, allowedorigins, getrequiredmemberships,str_to_bool,canrestictdata,canrestictdata_ministry
from request_api.exceptions import BusinessException
from request_api.services.requestservice import requestservice
from request_api.services.rawrequestservice import rawrequestservice
from request_api.services.eventservice import eventservice
from request_api.schemas.foirequestwrapper import  FOIRequestWrapperSchema, EditableFOIRequestWrapperSchema, FOIRequestMinistrySchema, FOIRequestStatusSchema
from request_api.schemas.foiassignee import FOIRequestAssigneeSchema
from marshmallow import Schema, fields, validate, ValidationError
from request_api.utils.enums import MinistryTeamWithKeycloackGroup
import json
import asyncio

API = Namespace('FOIRequests', description='Endpoints for FOI request management')
TRACER = Tracer.get_instance()
EXCEPTION_MESSAGE_NOTFOUND_REQUEST='Record not found'


@cors_preflight('GET,OPTIONS')
@API.route('/foirequests/<int:foirequestid>/ministryrequest/<int:foiministryrequestid>', defaults={'usertype':None})
@API.route('/foirequests/<int:foirequestid>/ministryrequest/<int:foiministryrequestid>/<string:usertype>')
class FOIRequest(Resource):
    """Retrieve foi request for opened request"""
    
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @auth.ismemberofgroups(getrequiredmemberships())
    def get(foirequestid,foiministryrequestid,usertype = None):
        try :
            jsondata = {}
            statuscode = 200
            if (AuthHelper.getusertype() == "iao") and (usertype is None or (usertype == "iao")):
                jsondata = requestservice().getrequest(foirequestid,foiministryrequestid)
                assignee = jsondata['assignedTo']
                isrestricted = jsondata['iaorestricteddetails']['isrestricted'] if ('isrestricted' in jsondata['iaorestricteddetails']) else False
                if(canrestictdata(foiministryrequestid,assignee,isrestricted,False)):
                    jsondata = {}
                    statuscode = 401
            elif usertype is not None and usertype == "ministry" and AuthHelper.getusertype() == "ministry":
                jsondata = requestservice().getrequestdetailsforministry(foirequestid,foiministryrequestid,AuthHelper.getministrygroups())
                assignee = jsondata['assignedministryperson']
                isrestricted = jsondata['ministryrestricteddetails']['isrestricted'] if ('isrestricted' in jsondata['ministryrestricteddetails']) else False
                if(canrestictdata_ministry(foiministryrequestid,assignee,isrestricted)):
                    jsondata = {}
                    statuscode = 401
            else:
                statuscode = 401 
            return jsondata , statuscode 
        except ValueError:
            return {'status': 500, 'message':"Invalid Request Id"}, 500
        except KeyError as err:
            return {'status': False, 'message':err.messages}, 400        
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500

                       
@cors_preflight('GET,POST,OPTIONS')
@API.route('/foirequests')
class FOIRequests(Resource):
    """Creates foi request"""

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def post():
        """ POST Method for capturing FOI requests before processing"""
        try:
            request_json = request.get_json()
            foirequestschema = FOIRequestWrapperSchema().load(request_json)
            
            assignedgroup = request_json['assignedGroup'] if 'assignedGroup' in foirequestschema  else None
            assignedto = request_json['assignedTo'] if 'assignedTo' in foirequestschema  else None
            assignedtofirstname = request_json["assignedToFirstName"] if request_json.get("assignedToFirstName") != None else None
            assignedtomiddlename = request_json["assignedToMiddleName"] if request_json.get("assignedToMiddleName") != None else None
            assignedtolastname = request_json["assignedToLastName"] if request_json.get("assignedToLastName") != None else None
            rawresult = rawrequestservice().saverawrequestversion(request_json,request_json['id'],assignedgroup,assignedto,"Archived",AuthHelper.getuserid(), assignedtofirstname,assignedtomiddlename,assignedtolastname)               


            
            if rawresult.success == True:
                result = requestservice().saverequest(foirequestschema,AuthHelper.getuserid())
                if result.success == True:
                    requestservice().copywatchers(request_json['id'],result.args[0],AuthHelper.getuserid())
                    requestservice().copycomments(request_json['id'],result.args[0],AuthHelper.getuserid())
                    requestservice().copydocuments(request_json['id'],result.args[0],AuthHelper.getuserid())
                    if 'subjectCode' in request_json:
                        requestservice().copysubjectcode(request_json['subjectCode'],result.args[0],AuthHelper.getuserid())
                    requestservice().postopeneventtoworkflow(result.identifier, request_json,result.args[0])
                    requestservice().createrestrictedrequests(result.args[0],'iao',request_json["isiaorestricted"],AuthHelper.getuserid())
                    
                    eventservice().posteventsync(request_json['id'],"rawrequest",AuthHelper.getuserid(), AuthHelper.getusername(), AuthHelper.isministrymember())

            return {'status': result.success, 'message':result.message,'id':result.identifier, 'ministryRequests': result.args[0]} , 200
        except ValidationError as err:
                    return {'status': False, 'message':err.messages}, 400
        except KeyError as err:
            return {'status': False, 'message':err.messages}, 400                    
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500
        
@cors_preflight('GET,POST,PUT,OPTIONS')
@API.route('/foirequests/<int:foirequestid>/ministryrequest/<int:foiministryrequestid>')
class FOIRequestsById(Resource):
    """Creates a new version of foi request for iao updates"""

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def post(foirequestid,foiministryrequestid):
        """ POST Method for capturing FOI requests before processing"""
        try:
            request_json = request.get_json()   
            foirequestschema = FOIRequestWrapperSchema().load(request_json)  
            result = requestservice().saverequestversion(foirequestschema, foirequestid, foiministryrequestid,AuthHelper.getuserid())
            if result.success == True:
                asyncio.ensure_future(eventservice().postevent(foiministryrequestid,"ministryrequest",AuthHelper.getuserid(),AuthHelper.getusername(),AuthHelper.isministrymember()))
                metadata = json.dumps({"id": result.identifier, "ministries": result.args[0]})
                requestservice().posteventtoworkflow(foiministryrequestid,  foirequestschema, json.loads(metadata),"iao")
                return {'status': result.success, 'message':result.message,'id':result.identifier, 'ministryRequests': result.args[0]} , 200
            else:
                 return {'status': False, 'message':EXCEPTION_MESSAGE_NOTFOUND_REQUEST,'id':foirequestid} , 404
        except ValidationError as err:
            return {'status': False, 'message':err.messages}, 400
        except KeyError as err:
            return {'status': False, 'message':err.messages}, 400    
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500
    
@cors_preflight('POST,OPTIONS')
@API.route('/foirequests/<int:foirequestid>/ministryrequest/<int:foiministryrequestid>/<string:usertype>')
@API.route('/foirequests/<int:foirequestid>/ministryrequest/<int:foiministryrequestid>/<string:usertype>/<string:actiontype>')
class FOIRequestsByIdAndType(Resource):
    """Creates a new version of foi request for ministry updates"""

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def post(foirequestid,foiministryrequestid,actiontype = None,usertype = None):
        """ POST Method for capturing FOI requests before processing"""
        try:
            if usertype != "ministry" and actiontype != "assignee":
                return {'status': False, 'message':'Bad Request'}, 400
            request_json = request.get_json()
            assigneename =''
            if actiontype == "assignee":
                ministryrequestschema = FOIRequestAssigneeSchema().load(request_json)                
                if(usertype == "iao"):
                    assigneename = getiaoassigneename(ministryrequestschema)                    
                elif(usertype == "ministry"):
                   assigneename = getministryassigneename(ministryrequestschema)               
            else:
                ministryrequestschema = FOIRequestMinistrySchema().load(request_json)
                print(ministryrequestschema)
            result = requestservice().saveministryrequestversion(ministryrequestschema, foirequestid, foiministryrequestid,AuthHelper.getuserid(), usertype)
            if result.success == True:
                asyncio.ensure_future(eventservice().postevent(foiministryrequestid,"ministryrequest",AuthHelper.getuserid(),AuthHelper.getusername(), AuthHelper.isministrymember(),assigneename, ministryrequestschema))
                metadata = json.dumps({"id": result.identifier, "ministries": result.args[0]})
                requestservice().posteventtoworkflow(foiministryrequestid, ministryrequestschema, json.loads(metadata),usertype)
                return {'status': result.success, 'message':result.message,'id':result.identifier, 'ministryRequests': result.args[0]} , 200
            else:
                 return {'status': False, 'message':EXCEPTION_MESSAGE_NOTFOUND_REQUEST,'id':foirequestid} , 404
        except ValidationError as err:
            return {'status': False, 'message':err.messages}, 400
        except KeyError as err:
            return {'status': False, 'message':err.messages}, 400
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500

def getiaoassigneename(assigneeschema):
    if(assigneeschema['assignedToFirstName'] != '' and assigneeschema['assignedToLastName'] != ''):
        return '{0}, {1}'.format(assigneeschema['assignedToLastName'],assigneeschema['assignedToFirstName'])
    elif (assigneeschema['assignedgroup'] != '' and assigneeschema['assignedToFirstName'] ==  '' and assigneeschema['assignedToLastName'] ==  ''):
        return   assigneeschema['assignedgroup']            

def getministryassigneename(assigneeschema):
    if (assigneeschema['assignedministrypersonLastName'] != '' and assigneeschema['assignedministrypersonFirstName'] != '' ):
        return '{0}, {1}'.format(assigneeschema['assignedministrypersonLastName'],assigneeschema['assignedministrypersonFirstName'])    
    elif (assigneeschema['assignedministrygroup'] != ''  and assigneeschema['assignedministrypersonLastName'] == '' and assigneeschema['assignedministrypersonFirstName'] == ''):
         return assigneeschema ['assignedministrygroup'] 

@cors_preflight('GET,POST,PUT,OPTIONS')
@API.route('/foirequests/<int:foirequestid>')
class FOIRequestUpdateById(Resource): 
    """Updates an foi request"""
        
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def put(foirequestid):
        """ PUT Method for capturing FOI requests before processing"""
        try:
            request_json = request.get_json()
            foirequestschema = EditableFOIRequestWrapperSchema().load(request_json)
            result = requestservice().updaterequest(foirequestschema, foirequestid,AuthHelper.getuserid())
            if result != {}:
                return {'status': result.success, 'message':result.message,'id':result.identifier} , 200
            else:
                 return {'status': False, 'message':EXCEPTION_MESSAGE_NOTFOUND_REQUEST,'id':foirequestid} , 404
        except ValidationError as err:
            return {'status': False, 'message':err.messages}, 40
        except BusinessException as exception:
            return {'status': exception.status_code, 'message':exception.message}, 500


@cors_preflight('GET,OPTIONS')
@API.route('/foirequests/<int:foirequestid>/ministryrequest/<int:foiministryrequestid>/payonline')
class FOIRequestDetailsByMinistryId(Resource):
    """Retrieve foi request for opened request"""
    
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def get(foirequestid, foiministryrequestid):
        try :
            jsondata = {}
            statuscode = 200            
            jsondata = requestservice().getrequestdetails(foirequestid, foiministryrequestid)            
            return jsondata , statuscode 
        except ValueError:
            return {'status': 500, 'message':"Invalid Request Id"}, 500
        except KeyError as err:
            return {'status': False, 'message':err.messages}, 400        
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500


@cors_preflight('GET,POST,OPTIONS')
@API.route('/foirequests/restricted/<ministryrequestid>/<type>')
class FOIRestrictedMinistryRequest(Resource):

    @staticmethod    
    @cross_origin(origins=allowedorigins())
    @auth.require
    def post(ministryrequestid=None,type=None):
        try :            
            if (int(ministryrequestid) and str(ministryrequestid) != "-1") or (type is not None and (type.lower() == 'iao' or type.lower() == 'ministry')) :
                request_json = request.get_json()                  
                _isrestricted = request_json['isrestricted'] if request_json['isrestricted'] is not None else False                
                isrestricted = str_to_bool(_isrestricted)                                                           
                result = requestservice().saverestrictedrequest(ministryrequestid,type,isrestricted,AuthHelper.getuserid())
                if result.success:
                  return {'status': result.success, 'message':result.message,'id':result.identifier} , 200
                else:
                  return {'status': result.success, 'message':result.message,'id':result.identifier} , 500  
        except ValueError:
            return {'status': 500, 'message':"Invalid Request"}, 400    
        except BusinessException as exception:
            return {'status': exception.status_code, 'message':exception.message}, 500

@cors_preflight('GET,POST,OPTIONS')
@API.route('/foirequests/ministryrequestid/<int:ministryrequestid>', defaults={'usertype':None})
@API.route('/foirequests/ministryrequestid/<ministryrequestid>/<usertype>')
class FOIRequestByMinistryId(Resource):
    """Return request based on ministryrequestid"""
    @staticmethod
    @cross_origin(origins=allowedorigins())
    @auth.require
    def get(ministryrequestid,usertype=None):
        try :
            return FOIRequest.get(requestservice().getrequestid(ministryrequestid), ministryrequestid, usertype)
        except ValueError:
            return {'status': 500, 'message':"Invalid Request"}, 400
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500 