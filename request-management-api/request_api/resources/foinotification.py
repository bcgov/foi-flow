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
from request_api.services.notificationservice import notificationservice
from request_api.services.eventservice import eventservice
import json
from flask_cors import cross_origin


API = Namespace('FOINotification', description='Endpoints for FOI notification management')
TRACER = Tracer.get_instance()

@cors_preflight('GET,OPTIONS')
@API.route('/foinotifications')
class FOINotification(Resource):
    """Resource for managing FOI requests."""

       
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def get():      
        try:
            result = notificationservice().getnotifications(AuthHelper.getuserid())
            return json.dumps(result), 200
        except ValueError:
            return {'status': 500, 'message':"Invalid Request Id"}, 500
        except KeyError as error:
            return {'status': False, 'message': f"{error=}"}, 400        
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500

@cors_preflight('DELETE,OPTIONS')
@API.route('/foinotifications')
@API.route('/foinotifications/<string:type>')
@API.route('/foinotifications/<string:idnumber>/<int:notficationid>')
class FOIDismissNotification(Resource):
    """Resource for managing FOI requests."""

       
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def delete(type=None,idnumber=None,notficationid=None):      
        try:
            result = notificationservice().dismissnotification(AuthHelper.getuserid(), type, idnumber, notficationid)
            if result.success == True:
                return {'status': result.success, 'message':result.message,'id':result.identifier} , 200
            return {'status': result.success, 'message':result.message,'id':result.identifier} , 500
        except ValueError:
            return {'status': 500, 'message':"Invalid Request Id"}, 500
        except KeyError as error:
            return {'status': False, 'message': f"{error=}"}, 400        
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500
        
@cors_preflight('POST,OPTIONS')
@API.route('/foinotifications/reminder')
class FOIReminderNotification(Resource):
    """Resource for managing FOI requests."""

       
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def post():      
        try:
            reminderresponse = eventservice().postreminderevent()
            respcode = 200 if reminderresponse.success == True else 500
            return {'status': reminderresponse.success, 'message':reminderresponse.message,'id': reminderresponse.identifier} , respcode
        except KeyError as error:
            return {'status': False, 'message': f"{error=}"}, 400        
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500
        

@cors_preflight('POST,OPTIONS')
@API.route('/foinotifications/<int:request_id>/ministryrequest/<int:ministry_request_id>/payment/expiry')
class FOIReminderNotification(Resource):
    """Resource for managing FOI requests."""

       
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def post(request_id: int, ministry_request_id: int):      
        try:
            reminderresponse = eventservice().postpaymentexpiryevent(ministry_request_id)
            respcode = 200 if reminderresponse.success == True else 500
            return {'status': reminderresponse.success, 'message':reminderresponse.message,'id': reminderresponse.identifier} , respcode
        except KeyError as error:
            return {'status': False, 'message': f"{error=}"}, 400        
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500