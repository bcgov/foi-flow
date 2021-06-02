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
from request_api.tracer import Tracer
from request_api.utils.util import  cors_preflight
from request_api.exceptions import BusinessException

from request_api.models.FOIRawRequests import FOIRawRequest

API = Namespace('FOIRawRequests', description='Endpoints for FOI request management')
TRACER = Tracer.get_instance()

@cors_preflight('GET,POST,OPTIONS')
@API.route('/foirawrequests')
class FOIRawRequests(Resource):
    """Resource for managing FOI Raw requests."""

    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    def get():
        return 'FOI Requests GET METHOD'

    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    def post():
        """ POST Method for capturing RAW FOI requests before processing"""
        try:
            request_json = request.get_json()
            requestdatajson = request_json['requestdata']
            print(requestdatajson)
            result = FOIRawRequest.saverawrequest(requestdatajson)           
            return {'status': result.success, 'message':result.message} , 200
        except BusinessException as exception:
            response = {'code': exception.code, 'message': exception.message}
            return response, 500