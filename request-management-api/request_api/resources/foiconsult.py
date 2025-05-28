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
class FOIConsultRequestById(Resource):
    """Creates (updates) a new version of foi consult requests"""
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def post(foiministryrequestid, foirequestid):
        try:
            request_json = request.get_json()
            foiconsult = FOIMinistryRequestConsultSchema(many=True).load(request_json)
            userid = AuthHelper.getuserid()
            result = consultservice().createconsultrequest(foiconsult, userid, foiministryrequestid)
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