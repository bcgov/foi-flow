from flask import g, request
import flask
from flask_restx import Namespace, Resource
from flask_cors import cross_origin

from request_api.tracer import Tracer
from request_api.utils.util import  cors_preflight, getgroupsfromtoken, allowedorigins,getrequiredmemberships
from request_api.utils.enums import MinistryTeamWithKeycloackGroup, UserGroup
from request_api.auth import auth
from request_api.tracer import Tracer
from request_api.exceptions import BusinessException
from request_api.services.dashboardservice import dashboardservice
import json

API = Namespace('FOI Flow Dashboard', description='Endpoints for Dashboard')
TRACER = Tracer.get_instance()

@cors_preflight('GET,OPTIONS')
@API.route('/dashboard', defaults={'queuetype':None})
@API.route('/dashboard/<queuetype>')
class Dashboard(Resource):
    """ Retrives the foi request based on the queue type.
    """
    @staticmethod
    @TRACER.trace()    
    @cross_origin(origins=allowedorigins())
    @auth.require
    @cors_preflight('GET,POST,OPTIONS') 
    @auth.ismemberofgroups(getrequiredmemberships())
    def get(queuetype = None):        
        try:
            requestqueue = []
            groups = getgroupsfromtoken()           
            ministrygroups = list(set(groups).intersection(MinistryTeamWithKeycloackGroup.list()))
            statuscode = 200 
            if (UserGroup.intake.value in groups or UserGroup.flex.value in groups or UserGroup.processing.value in groups) and (queuetype is None or queuetype == "all"):                                                                                           
                requestqueue = dashboardservice().getrequestqueue(groups)                                                              
            elif  queuetype is not None and queuetype == "ministry" and len(ministrygroups) > 0:                                                 
                requestqueue = dashboardservice().getministryrequestqueue(ministrygroups)                
            else:
                if len(ministrygroups) == 0 :
                  statuscode = 401           
                
            jsondata = json.dumps(requestqueue)
            return jsondata , statuscode                    
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500