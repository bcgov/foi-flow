from flask import g, request
import flask
from flask_restx import Namespace, Resource, cors
from request_api.auth import auth
from request_api.tracer import Tracer
from request_api.utils.util import  cors_preflight, getgroupsfromtoken
from request_api.exceptions import BusinessException, Error
from request_api.services.dashboardservice import dashboardservice
from request_api.auth import jwt as _authjwt
import jwt
import json

API = Namespace('FOI Flow Dashboard', description='Endpoints for Dashboard')
TRACER = Tracer.get_instance()

@cors_preflight('GET,POST,OPTIONS')
@API.route('/dashboard')

class Dashboard(Resource):
    @staticmethod
    @TRACER.trace()    
    @cors.crossdomain(origin='*')
    @auth.require
    @cors_preflight('GET,POST,OPTIONS') 
    @auth.ismemberofgroups('Intake Team,Flex Team')
    def get():        
        try:    
                groups = getgroupsfromtoken()                
                requests = dashboardservice.getrequestqueue(groups)                
                jsondata = json.dumps(requests)
                return jsondata , 200            
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500