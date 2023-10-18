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
from request_api.services.workflowservice import workflowservice
import json
from flask_cors import cross_origin
import logging

API = Namespace('FOIWorkflow', description='Endpoints for FOI workflow management')
TRACER = Tracer.get_instance()

@cors_preflight('POST,OPTIONS')
@API.route('/foiworkflow/<requesttype>/<requestid>/sync')
class FOIWorkflow(Resource):
    """Retrieve watchers for unopened request"""

       
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def post(requesttype, requestid):      
        try:
            logging.info("request details = %s | %s", requesttype, requestid)
            response = workflowservice().syncwfinstance(requesttype, requestid, True)
            return json.dumps({"message": str(response)}), 200
        except ValueError as err:
            return {'status': 500, 'message':err.messages}, 500
        except KeyError as error:
            return {'status': False, 'message': str(type(error).__name__)}, 400        
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500


