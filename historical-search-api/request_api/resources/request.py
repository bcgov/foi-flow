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
# from request_api.services.rawrequestservice import rawrequestservice
# from request_api.services.documentservice import documentservice
# from request_api.services.eventservice import eventservice
# from request_api.services.unopenedreportservice import unopenedreportservice
from request_api.services.historicalrequestservice import historicalrequestservice
# from request_api.utils.enums import StateName
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
@API.route('/foihistoricalrequest/<requestid>')
class FOIRawRequest(Resource):
    """Retrieve historical request details from EDW"""

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())       
    # @auth.require
    def get(requestid):
        try : 
            statuscode = 200
            jsondata = historicalrequestservice().gethistoricalrequest(requestid)
            return jsondata , statuscode 
        except ValueError:
            return {'status': 500, 'message':INVALID_REQUEST_ID}, 500    
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500
        

@cors_preflight('GET,POST,OPTIONS')
@API.route('/foihistoricalrequest/descriptionhistory/<requestid>')
class FOIRawRequest(Resource):
    """Retrieve historical request details from EDW"""

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())       
    # @auth.require
    def get(requestid):
        try : 
            statuscode = 200
            jsondata = historicalrequestservice().gethistoricalrequestdescriptionhistory(requestid)
            return jsondata , statuscode 
        except ValueError:
            return {'status': 500, 'message':INVALID_REQUEST_ID}, 500    
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500
        
@cors_preflight('GET,POST,OPTIONS')
@API.route('/foihistoricalrequest/extensions/<requestid>')
class FOIRawRequest(Resource):
    """Retrieve historical request details from EDW"""

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())       
    # @auth.require
    def get(requestid):
        try : 
            statuscode = 200
            jsondata = historicalrequestservice().gethistoricalrequestextensions(requestid)
            return jsondata , statuscode 
        except ValueError:
            return {'status': 500, 'message':INVALID_REQUEST_ID}, 500    
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500

    