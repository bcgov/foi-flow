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
from request_api.auth import auth


from request_api.tracer import Tracer
from request_api.utils.util import  cors_preflight, allowedOrigins
from request_api.exceptions import BusinessException, Error
from request_api.services.applicantcategoryservice import applicantcategoryservice
from request_api.services.programareaservice import programareaservice
from request_api.services.deliverymodeservice import deliverymodeservice
from request_api.services.receivedmodeservice import receivedmodeservice
from request_api.services.divisionstageservice import divisionstageservice
from request_api.services.closereasonservice import closereasonservice
import json
import request_api

API = Namespace('FOI Flow Master Data', description='Endpoints for FOI Flow master data')
TRACER = Tracer.get_instance()

@cors_preflight('GET,OPTIONS')
@API.route('/foiflow/applicantcategories')
class FOIFlowApplicantCategories(Resource):

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedOrigins())      
    @auth.require
    @request_api.cache.cached(key_prefix="applicantcategories")
    def get():
        try:
            data = applicantcategoryservice.getapplicantcategories()
            jsondata = json.dumps(data)
            return jsondata , 200
        except:
            return "Error happened while accessing applicant categories" , 500


@cors_preflight('GET,OPTIONS')
@API.route('/foiflow/programareas')
class FOIFlowProgramAreas(Resource):

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedOrigins())      
    @auth.require
    @request_api.cache.cached(key_prefix="programareas")
    def get():
        try:
            data = programareaservice.getprogramareas()
            jsondata = json.dumps(data)
            return jsondata , 200
        except:
            return "Error happened while accessing applicant categories" , 500

@cors_preflight('GET,OPTIONS')
@API.route('/foiflow/deliverymodes')
class FOIFlowDeliveryModes(Resource):

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedOrigins())       
    @auth.require
    @request_api.cache.cached(key_prefix="deliverymodes")
    def get():
        try:
            data = deliverymodeservice.getdeliverymodes()
            jsondata = json.dumps(data)
            return jsondata , 200
        except:
            return "Error happened while accessing delivery modes" , 500

@cors_preflight('GET,OPTIONS')
@API.route('/foiflow/receivedmodes')
class FOIFlowReceivedModes(Resource):

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedOrigins())       
    @auth.require
    @request_api.cache.cached(key_prefix="receivedmodes")
    def get():
        try:
            data = receivedmodeservice.getreceivedmodes()
            jsondata = json.dumps(data)
            return jsondata , 200
        except:
            return "Error happened while accessing received modes" , 500

@cors_preflight('GET,OPTIONS')
@API.route('/foiflow/divisions/<bcgovcode>')
class FOIFlowDivisions(Resource):

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedOrigins())       
    @auth.require
    def get(bcgovcode):
        try:
            data = divisionstageservice().getdivisionandstages(bcgovcode)
            jsondata = json.dumps(data)
            return jsondata , 200
        except:
            return "Error happened while accessing divisions" , 500 
        
@cors_preflight('GET,OPTIONS')
@API.route('/foiflow/closereasons')
class FOIFlowCloseReasons(Resource):

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedOrigins())       
    @auth.require
    @request_api.cache.cached(key_prefix="closereasons")
    def get():
        try:
            data = closereasonservice.getclosereasons()
            jsondata = json.dumps(data)
            return jsondata , 200
        except:
            return "Error happened while accessing received modes" , 500