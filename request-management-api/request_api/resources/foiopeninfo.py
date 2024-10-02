from flask import g, request
from flask_restx import Namespace, Resource
from flask_expects_json import expects_json
from flask_cors import cross_origin
from request_api.auth import auth, AuthHelper
from request_api.services.eventservice import eventservice
from request_api.tracer import Tracer
from request_api.utils.util import  cors_preflight, allowedorigins, getrequiredmemberships,str_to_bool,canrestictdata,canrestictdata_ministry
from request_api.exceptions import BusinessException
from request_api.schemas.foiopeninfo import FOIOpenInfoSchema
from request_api.services.openinfoservice import openinfoservice
from marshmallow import Schema, fields, validate, ValidationError
import json
import asyncio

API = Namespace('FOIRequests', description='Endpoints for FOI request management')
TRACER = Tracer.get_instance()
EXCEPTION_MESSAGE_NOTFOUND_REQUEST='Record not found'
CUSTOM_KEYERROR_MESSAGE = "Key error has occured: "

@cors_preflight('GET,OPTIONS')
@API.route('/foiopeninfo/ministryrequest/<int:foiministryrequestid>/<string:usertype>')
class FOIOpenInfoRequest(Resource):
    """Return openinfo request based on foiministryrequestid"""
    @staticmethod
    @cross_origin(origins=allowedorigins())
    @auth.require
    def get(ministryrequestid,usertype=None):
        pass

@cors_preflight('POST,OPTIONS') 
@API.route('/foiopeninfo/foirequest/<int:foirequestid>/ministryrequest/<int:foiministryrequestid>/<string:usertype>')
class FOIOpenInfoRequestById(Resource):
    """Creates a foi openinfo request for ministry(opened) requests"""
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def post(foiministryrequestid):
        try:
            request_json = request.get_json()
            foiopeninfo = FOIOpenInfoSchema().load(request_json)
            userid = AuthHelper.getuserid()
            result = openinfoservice.createopeninforequest(foiopeninfo, userid, foiministryrequestid)
            if result.success:
                return {'status': result.success, 'message': result.message, 'id': result.identifier}, 200
        except ValidationError as err:
            return {'status': False, 'message': str(err)}, 400
        except KeyError as error:
            return {'status': False, 'message': CUSTOM_KEYERROR_MESSAGE + str(error)}, 400    
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500

@cors_preflight('PUT,OPTIONS') 
# PUT AND POST ROUTES. IF FE DATA CONTAINS OR SENDS FOIOPENINFO DATA WITH A EXISTING FOIOPENINFOREQUESTID use PUT ROUTE AND USE UPDATESERVICE. IF POST route sent and fe data does not contain a foiopeninforequetst id use post route and createfoiopen service
@API.route('/foiopeninfo/foirequest/<int:foirequestid>/ministryrequest/<int:foiministryrequestid>/<string:usertype>')
class FOIOpenInfoRequestById(Resource):
    """Creates (updates) a new version of foi openinfo requests"""
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def put(foiministryrequestid):
        try:
            request_json = request.get_json()
            foiopeninfo = FOIOpenInfoSchema().load(request_json)
            userid = AuthHelper.getuserid()
            result = openinfoservice.updateopeninforequest(foiopeninfo, userid, foiministryrequestid)
            if result.success:
                return {'status': result.success, 'message': result.message, 'id': result.identifier}, 200
        except ValidationError as err:
            return {'status': False, 'message': str(err)}, 400
        except KeyError as error:
            return {'status': False, 'message': CUSTOM_KEYERROR_MESSAGE + str(error)}, 400    
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500