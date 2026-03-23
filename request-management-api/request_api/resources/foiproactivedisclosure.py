from flask import g, request
from flask_restx import Namespace, Resource
from flask_cors import cross_origin
from request_api.auth import auth, AuthHelper
from request_api.tracer import Tracer
from request_api.utils.util import cors_preflight, allowedorigins
from request_api.exceptions import BusinessException
from request_api.services.proactivedisclosureservice import proactivedisclosureservice
from request_api.utils.enums import IAOTeamWithKeycloackGroup
from marshmallow import ValidationError
import json

API = Namespace('FOIPROACTIVEDISCLOSURE', description='Endpoints for FOI Proactive Disclosure management')
TRACER = Tracer.get_instance()
EXCEPTION_MESSAGE_NOTFOUND_REQUEST='Record not found'
CUSTOM_KEYERROR_MESSAGE = "Key error has occured: "

@cors_preflight('GET,OPTIONS')
@API.route('/foiproactivedisclosure/ministryrequest/<int:foiministryrequestid>')
class FOIProactiveDisclosureRequest(Resource):
    """Return current proactive disclosure request based on foiministryrequestid"""
    @staticmethod
    @cross_origin(origins=allowedorigins())
    @TRACER.trace()
    @auth.require
    @auth.ismemberofgroups(",".join(IAOTeamWithKeycloackGroup.list()))
    def get(foiministryrequestid):
        try:
            result = proactivedisclosureservice().getcurrentfoiproactiverequest(foiministryrequestid)
            return json.dumps(result), 200
        except ValidationError as err:
            return {'status': False, 'message': str(err)}, 400
        except KeyError as error:
            return {'status': False, 'message': CUSTOM_KEYERROR_MESSAGE + str(error)}, 400    
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500

@cors_preflight('POST, OPTIONS') 
@API.route('/foiproactivedisclosure/foirequest/<int:foirequestid>/ministryrequest/<int:foiministryrequestid>')
class FOIProactiveDisclosureRequestById(Resource):
    """Updates proactive disclosure publication details"""
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @auth.ismemberofgroups(",".join(IAOTeamWithKeycloackGroup.list()))
    def post(foiministryrequestid, foirequestid):
        try:
            request_json = request.get_json()
            userid = AuthHelper.getuserid()
            result = proactivedisclosureservice().updateproactivedisclosure(request_json, userid, foiministryrequestid)
            if result.success:
                return {'status': result.success, 'message': result.message, 'id': result.identifier}, 200
            return {'status': result.success, 'message': result.message}, 500
        except ValidationError as err:
            return {'status': False, 'message': str(err)}, 400
        except KeyError as error:
            return {'status': False, 'message': CUSTOM_KEYERROR_MESSAGE + str(error)}, 400    
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500
