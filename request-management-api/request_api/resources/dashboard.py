from flask import g, request
import flask
from flask_restx import Namespace, Resource
from flask_cors import cross_origin

from request_api.tracer import Tracer
from request_api.utils.util import  cors_preflight, getgroupsfromtoken, allowedOrigins,getrequiredmemberships
from request_api.utils.enums import MinistryTeamWithKeycloackGroup
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
@API.route('/dashboard', defaults={'queuetype':None})
@API.route('/dashboard/<queuetype>')
class Dashboard(Resource):
    @staticmethod
    @TRACER.trace()    
    @cross_origin(origins=allowedOrigins())
    #@auth.require
    @cors_preflight('GET,POST,OPTIONS') 
    #@auth.ismemberofgroups(getrequiredmemberships())
    def get(queuetype = None):        
        try:
            requestqueue = []
            #groups = getgroupsfromtoken()
            groups =['Intake Team','Flex Team','Processing Team']           
            ministrygroups = list(set(groups).intersection(MinistryTeamWithKeycloackGroup.list()))
            statuscode = 200                        
            if ('Intake Team' in groups or 'Flex Team' in groups or 'Processing Team' in groups) and (queuetype is None or queuetype == "all"):                                                                                           
                requestqueue = dashboardservice.getrequestqueue(groups)                                                              
            elif  queuetype is not None and queuetype == "ministry" and ministrygroups is not None and len(ministrygroups) > 0:                                                 
                requestqueue = dashboardservice.getministryrequestqueue(ministrygroups)                
            else:
                if len(ministrygroups) == 0 :
                  statuscode = 401           
                
            jsondata = json.dumps(requestqueue)
            return jsondata , statuscode                    
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500