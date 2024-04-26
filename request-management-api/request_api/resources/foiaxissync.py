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
"""API endpoints for syncing data from AXIS to MOD."""


from flask import g, request
from flask_restx import Namespace, Resource, cors
from flask_expects_json import expects_json
from request_api.auth import auth
from request_api.auth import auth, AuthHelper
from request_api.tracer import Tracer
from request_api.utils.util import  cors_preflight, allowedorigins
from request_api.exceptions import BusinessException, Error
from request_api.services.external.axissyncservice import axissyncservice
import json
from flask_cors import cross_origin
import logging

API = Namespace('foiaxissync', description='Endpoints for syncing AXIS data to MOD system')
TRACER = Tracer.get_instance()
CUSTOM_KEYERROR_MESSAGE = "Key error has occured: "

@cors_preflight('POST,OPTIONS')
@API.route('/foiaxissync/sync/<programarea>/<requesttype>/pageinfo')
class FOIWorkflow(Resource):
    """Sync pageinfo in bulk"""

       
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def post(programarea, requesttype):      
        try:
            logging.info("page info sync action started for programarea=%s | requesttype=%s ",programarea, requesttype)
            result = axissyncservice().syncpagecounts(programarea,requesttype)
            return {'status': result.success, 'message': result.message,'id':programarea} , 200 
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500


