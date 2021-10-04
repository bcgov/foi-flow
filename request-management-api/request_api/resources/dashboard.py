from flask import g, request
import flask
from flask_restx import Namespace, Resource
from flask_cors import cross_origin

from request_api.tracer import Tracer
from request_api.utils.util import  cors_preflight, getgroupsfromtoken, allowedOrigins,getdashboardmemberships


from request_api.auth import auth
from request_api.tracer import Tracer
from request_api.exceptions import BusinessException, Error
from request_api.services.dashboardservice import dashboardservice
from request_api.auth import jwt as _authjwt
import jwt
import json

API = Namespace('FOI Flow Dashboard', description='Endpoints for Dashboard')
TRACER = Tracer.get_instance()

@cors_preflight('GET,OPTIONS')
@API.route('/dashboard', defaults={'ministry':None})
@API.route('/dashboard/<ministry>')
class Dashboard(Resource):
    @staticmethod
    @TRACER.trace()    
    @cross_origin(origins=allowedOrigins())
    @auth.require
    @cors_preflight('GET,POST,OPTIONS') 
    @auth.ismemberofgroups(getdashboardmemberships())
    def get(ministry = None):        
        try:
            groups = getgroupsfromtoken()
            ministrygroups = groups   
            if ministry is None and ['Intake Team','Flex Team'] in groups:                                                               
                requests = dashboardservice.getrequestqueue(groups)                
                jsondata = json.dumps(requests)
                return jsondata , 200
            elif ministry is not None:
                 
                requests = dashboardservice.getrequestqueue(groups)                
                jsondata = json.dumps(requests)
                return jsondata , 200                
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500