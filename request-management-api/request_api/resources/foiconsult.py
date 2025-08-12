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
from request_api.services.watcherservice import watcherservice
from request_api.services.eventservice import eventservice
from request_api.schemas.foiwatcher import  FOIRawRequestWatcherSchema, FOIMinistryRequestWatcherSchema
from request_api.services.eventservice import eventservice
from request_api.schemas.foirequestwrapper import FOIMinistryRequestConsultSchema
from request_api.services.consultservice import consultservice
from marshmallow import Schema, fields, validate, ValidationError
import json
from flask_cors import cross_origin


API = Namespace('FOIConsults', description='Endpoints for FOI consult management')
TRACER = Tracer.get_instance()
EXCEPTION_MESSAGE_NOTFOUND_REQUEST='Record not found'
CUSTOM_KEYERROR_MESSAGE = "Key error has occured: "

@cors_preflight('POST, PUT, OPTIONS') 
@API.route('/foiconsult/<foirequestid>/ministryrequest/<foiministryrequestid>')
@API.route('/foiconsult/<foirequestid>/ministryrequest/<foiministryrequestid>/<string:actiontype>')
class FOIConsultRequestById(Resource):
    """Creates (updates) a new version of foi consult requests"""
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def post(foiministryrequestid, foirequestid, actiontype = None):
        try:
            request_json = request.get_json()
            userid = AuthHelper.getuserid()
            assigneedata = getassigneeparams(request_json)
            
            # Initialize variables with None
            assigneegroup = None
            assigneeEmail = None
            assigneefirstname = None
            assigneelastname = None
            assignee = None

            # Only set values if assigneedata exists
            if assigneedata:
                assigneegroup = assigneedata.get('assigneegroup')
                assigneeEmail = assigneedata.get('assignee')
                assigneefirstname = assigneedata.get('assigneefirstname')
                assigneelastname = assigneedata.get('assigneelastname')
                assignee = getassignee(assigneefirstname, assigneelastname, assigneegroup)
                      
            foiconsult = FOIMinistryRequestConsultSchema(many=True).load(request_json)
            result = consultservice().createconsultrequest(foiconsult, userid, foiministryrequestid, assigneedata)
            return result, 200
        except ValidationError as err:
            return {'status': False, 'message': str(err)}, 400
        except KeyError as error:
            return {'status': False, 'message': CUSTOM_KEYERROR_MESSAGE + str(error)}, 400    
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500
        

@cors_preflight('GET,OPTIONS')
@API.route('/foiconsult/ministryrequest/<ministryrequestid>')
class FOIConsultRequests(Resource):
    """Return current consult requests based on foiministryrequestid"""
    @staticmethod
    @cross_origin(origins=allowedorigins())
    @TRACER.trace()
    @auth.require
    def get(ministryrequestid):
        try:
            result = consultservice().getconsultrequests(ministryrequestid)
            return  result, 200
        except ValidationError as err:
            return {'status': False, 'message': str(err)}, 400
        except KeyError as error:
            return {'status': False, 'message': CUSTOM_KEYERROR_MESSAGE + str(error)}, 400    
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500
        
@cors_preflight('GET,OPTIONS')
@API.route('/foiconsult/axisrequestid/<axisrequestid>')
class FOIOriginalRequestDetails(Resource):
    """Return request details and consult request details based on axisrequestid"""
    @staticmethod
    @cross_origin(origins=allowedorigins())
    @TRACER.trace()
    @auth.require
    def get(axisrequestid):
        try:
            if AuthHelper.getusertype() == "iao":
                jsondata = consultservice().getoriginalrequestDetailsByAxisRequestId(axisrequestid)
                consultrequests = consultservice().getconsultrequests(jsondata['id'])
                isMinistryRequestPresent = jsondata is not None

                if not isMinistryRequestPresent:
                    return {"foiministryrequest": jsondata, "ispresent": False}, 200  
            
                return {"foiministryrequest": jsondata, "ispresent": True}, 200 
            return {"status": False, "message": "Unauthorized user type."}, 403 
        except ValidationError as err:
            return {'status': False, 'message': str(err)}, 400
        except KeyError as error:
            return {'status': False, 'message': CUSTOM_KEYERROR_MESSAGE + str(error)}, 400    
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500


# @cors_preflight('POST,OPTIONS')
# @API.route('/foiconsult/<int:ministryid>/ministryconsultrequest/<int:consultid>/<string:usertype>', defaults={'consultid': None})
# @API.route('/foiconsult/<int:ministryid>/ministryconsultrequest/<int:consultid>/<string:usertype>/<string:actiontype>', defaults={'consultid': None})
# class FOIConsultRequestsByIdAndType(Resource):
#     """Creates a new version of foi consult request for ministry updates"""

#     @staticmethod
#     @TRACER.trace()
#     @cross_origin(origins=allowedorigins())
#     @auth.require
#     def post(foirequestid,foiministryrequestid,actiontype = None,usertype = None):
#         """ POST Method for capturing FOI requests before processing"""
#         try:
#             if usertype != "ministry" and actiontype != "assignee":
#                 return {'status': False, 'message':'Bad Request'}, 400
#             request_json = request.get_json()
#             assigneename =''
#             if actiontype == "assignee":
#                 ministryrequestschema = FOIRequestAssigneeSchema().load(request_json)                
#                 if(usertype == "iao"):
#                     assigneename = getiaoassigneename(ministryrequestschema)                    
#                 elif(usertype == "ministry"):
#                    assigneename = getministryassigneename(ministryrequestschema)               
#             else:
#                 ministryrequestschema = FOIRequestMinistrySchema().load(request_json)
#             result = requestservice().saveministryrequestversion(ministryrequestschema, foirequestid, foiministryrequestid,AuthHelper.getuserid(), usertype)
#             if result.success == True:
#                 event_loop = asyncio.get_running_loop()
#                 asyncio.run_coroutine_threadsafe(eventservice().postevent(foiministryrequestid,"ministryrequest",AuthHelper.getuserid(),AuthHelper.getusername(), AuthHelper.isministrymember(),assigneename), event_loop)
#                 metadata = json.dumps({"id": result.identifier, "ministries": result.args[0]})
#                 requestservice().posteventtoworkflow(foiministryrequestid, ministryrequestschema, json.loads(metadata),usertype)
#                 return {'status': result.success, 'message':result.message,'id':result.identifier, 'ministryRequests': result.args[0]} , 200
#             else:
#                  return {'status': False, 'message':EXCEPTION_MESSAGE_NOTFOUND_REQUEST,'id':foirequestid} , 404
#         except ValidationError as err:
#             return {'status': False, 'message': str(err)}, 400
#         except KeyError as error:
#             return {'status': False, 'message': CUSTOM_KEYERROR_MESSAGE + str(error)}, 400
#         except BusinessException as exception:            
#             return {'status': exception.status_code, 'message':exception.message}, 500
        
def getassigneeparams(request_json):
    # Handle single item or first item if it's a list
    updaterequest = request_json[0] if isinstance(request_json, list) else request_json
    
    if not updaterequest or not updaterequest.get("consultAssigneeVal"):
        return None
        
    consultAssigneeVal = updaterequest.get("consultAssigneeVal", {})
    
    return {
        'assigneegroup': consultAssigneeVal.get("assignedGroup"),
        'assignee': consultAssigneeVal.get("assignedTo"),  # This will be used as email/username
        'assigneefirstname': consultAssigneeVal.get("assignedToFirstName"),
        'assigneemiddlename': None,
        'assigneelastname': consultAssigneeVal.get("assignedToLastName"),
        'assigneename': consultAssigneeVal.get("assignedToName"),
        'username': consultAssigneeVal.get("assignedTo"),  # Adding username field
        'email': consultAssigneeVal.get("assignedTo"),     # Adding email field
        'groupname': consultAssigneeVal.get("assignedGroup")  # Adding groupname field
    }

def getassignee(assigneefirstname,assigneelastname,assigneegroup):
    if(assigneefirstname !='' and assigneelastname!=''):
        return  "{0}, {1}".format(assigneelastname,assigneefirstname)
    else: 
        return  assigneegroup    