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
from request_api.auth import auth

from request_api.tracer import Tracer
from request_api.utils.util import  cors_preflight
from request_api.exceptions import BusinessException, Error
from request_api.services.applicantcategoryservice import applicantcategoryservice
from request_api.services.programareaservice import programareaservice
from request_api.services.deliverymodeservice import deliverymodeservice
from request_api.services.receivedmodeservice import receivedmodeservice
from request_api.services.external.keycloakadminservice import KeycloakAdminService
import json

API = Namespace('FOI Flow Master Data', description='Endpoints for FOI Flow master data')
TRACER = Tracer.get_instance()

@cors_preflight('GET,OPTIONS')
@API.route('/foiflow/applicantcategories')
class FOIFlowApplicantCategories(Resource):

    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    @auth.require
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
    @cors.crossdomain(origin='*')
    @auth.require
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
    @cors.crossdomain(origin='*')
    @auth.require
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
    @cors.crossdomain(origin='*')
    @auth.require
    def get():
        try:
            data = receivedmodeservice.getreceivedmodes()
            jsondata = json.dumps(data)
            return jsondata , 200
        except:
            return "Error happened while accessing received modes" , 500

@cors_preflight('GET,OPTIONS')
@API.route('/foiflow/intake/teammembers')
class IntakeTeamMembers(Resource):

    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    @auth.require
    def get():
        try:
            keycloakadminservice = KeycloakAdminService()
            data = keycloakadminservice.getusers()              
            return json.dumps(data) , 200
        except:
            return "Error happened while accessing intake teammembers from keycloak" , 500          