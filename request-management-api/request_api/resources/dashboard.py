from flask import g, request
from flask_restx import Namespace, Resource, cors

from request_api.tracer import Tracer
from request_api.utils.util import  cors_preflight
from request_api.exceptions import BusinessException, Error
from request_api.services.dashboardservice import dashboardservice

import json

API = Namespace('FOI Flow Dashboard', description='Endpoints for Dashboard')
TRACER = Tracer.get_instance()

@cors_preflight('GET,POST,OPTIONS')
@API.route('/dashboard')
class Dashboard(Resource):
    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')   
    def get():
        ## todo : This code will get re-furshibed with BPM WF validation to list
        try:                                                       
                unopenedrequests = dashboardservice.getrequestqueue()
                jsondata = json.dumps(unopenedrequests)
                return jsondata , 200            
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500