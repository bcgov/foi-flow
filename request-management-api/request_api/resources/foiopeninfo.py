from flask import g, request
from flask_restx import Namespace, Resource
from flask_cors import cross_origin
from request_api.auth import auth, AuthHelper
from request_api.tracer import Tracer
from request_api.utils.util import  cors_preflight, allowedorigins
from request_api.exceptions import BusinessException
from request_api.schemas.foiopeninfo import FOIOpenInfoSchema, FOIOpenInfoAdditionalFilesSchema, FOIOpenInfoAdditionalFilesDeleteSchema
from request_api.services.openinfoservice import openinfoservice
from request_api.services.publication_events.rest_service import PublishNowRestService
from request_api.utils.enums import IAOTeamWithKeycloackGroup
from marshmallow import ValidationError
import json
import redis
from os import getenv
import logging


API = Namespace('FOIOPENINFO', description='Endpoints for FOI OpenInformation management')
TRACER = Tracer.get_instance()
EXCEPTION_MESSAGE_NOTFOUND_REQUEST='Record not found'
CUSTOM_KEYERROR_MESSAGE = "Key error has occured: "

# GET CALL for oi data -> ALLOWABLE = IAO, OI. RESTRCIT = Ministry
# POST CALL (Create + update oi data) -> ALLOWABLE = IAO (exemption speicifc data), OI (exemption + publicaiton data). RESTRCIT = Ministry. Specific data (exemption or pulibcation) done in FE
# POST, GET, DELETE for additional files -> Allowable = ONLY OI

redis_host = getenv("OPENINFO_REDIS_HOST", "localhost")
redis_port = int(getenv("OPENINFO_REDIS_PORT", 6380))
redis_password = getenv("OPENINFO_REDIS_PASSWORD")
redis_stream_name = getenv(
    "OPENINFO_REDIS_STREAM_NAME",
    "proactivedisclosure.publish.requested"
)

redis_client = redis.Redis(
    host=redis_host,
    port=redis_port,
    db=0,
    password=redis_password,
    decode_responses=True
)

@cors_preflight('GET,OPTIONS')
@API.route('/foiopeninfo/ministryrequest/<int:foiministryrequestid>', defaults={'usertype':None})
@API.route('/foiopeninfo/ministryrequest/<int:foiministryrequestid>/<string:usertype>')
class FOIOpenInfoRequest(Resource):
    """Return current  openinfo request based on foiministryrequestid"""
    @staticmethod
    @cross_origin(origins=allowedorigins())
    @TRACER.trace()
    @auth.require
    @auth.ismemberofgroups(",".join(IAOTeamWithKeycloackGroup.list()))
    def get(foiministryrequestid, usertype=None):
        try:
            result = openinfoservice().getcurrentfoiopeninforequest(foiministryrequestid)
            # if result in (None, {}):
            #     return {"status": False, "message": "Could not find FOIOpenInfoRequest"}, 404
            return  json.dumps(result), 200
        except ValidationError as err:
            return {'status': False, 'message': str(err)}, 400
        except KeyError as error:
            return {'status': False, 'message': CUSTOM_KEYERROR_MESSAGE + str(error)}, 400    
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500

@cors_preflight('POST, PUT, OPTIONS') 
@API.route('/foiopeninfo/foirequest/<int:foirequestid>/ministryrequest/<int:foiministryrequestid>', defaults={'usertype':None})
@API.route('/foiopeninfo/foirequest/<int:foirequestid>/ministryrequest/<int:foiministryrequestid>/<string:usertype>')
class FOIOpenInfoRequestById(Resource):
    """Creates (updates) a new version of foi openinfo requests"""
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @auth.ismemberofgroups(",".join(IAOTeamWithKeycloackGroup.list()))
    def post(foiministryrequestid, foirequestid, usertype):
        try:
            request_json = request.get_json()
            assignee_details = request_json.get('assigneeDetails', {})
            schema_data = request_json.copy()
            schema_data.pop('assigneeDetails', None)
            foiopeninfo = FOIOpenInfoSchema().load(schema_data)   
            userid = AuthHelper.getuserid()
            result = openinfoservice().updateopeninforequest(foiopeninfo, userid, foiministryrequestid, assignee_details)
            if result.success:
                return {'status': result.success, 'message': result.message, 'id': result.identifier}, 200
        except ValidationError as err:
            return {'status': False, 'message': str(err)}, 400
        except KeyError as error:
            return {'status': False, 'message': CUSTOM_KEYERROR_MESSAGE + str(error)}, 400    
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500
        

@cors_preflight('POST, GET, OPTIONS') 
@API.route('/foiopeninfoadditionalfiles/foirequest/<int:foirequestid>/ministryrequest/<int:foiministryrequestid>')
class FOIOpenInfoAdditionalFiles(Resource):
    """Gets all open info files by ministryrequestid"""
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @auth.ismemberofgroups(IAOTeamWithKeycloackGroup.oi.value)
    def get(foiministryrequestid, foirequestid):
        try:
            result = openinfoservice().fetchopeninfoadditionalfiles(foiministryrequestid)
            return json.dumps(result), 200
        except ValidationError as err:
            return {'status': False, 'message': str(err)}, 400
        except KeyError as error:
            return {'status': False, 'message': CUSTOM_KEYERROR_MESSAGE + str(error)}, 400    
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500

    """Saves info for open info additional file uploads"""    
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @auth.ismemberofgroups(IAOTeamWithKeycloackGroup.oi.value)
    def post(foiministryrequestid, foirequestid):
        try:
            request_json = request.get_json()
            files = FOIOpenInfoAdditionalFilesSchema().load(request_json)
            userid = AuthHelper.getuserid()
            result = openinfoservice().saveopeninfoadditionalfiles(foiministryrequestid, files, userid)
            if result.success:
                return {'status': result.success, 'message': result.message, 'id': result.identifier}, 200
        except ValidationError as err:
            return {'status': False, 'message': str(err)}, 400
        except KeyError as error:
            return {'status': False, 'message': CUSTOM_KEYERROR_MESSAGE + str(error)}, 400    
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500
        
@cors_preflight('POST, OPTIONS') 
@API.route('/foiopeninfoadditionalfiles/foirequest/<int:foirequestid>/ministryrequest/<int:foiministryrequestid>/delete')
class FOIOpenInfoAdditionalFilesDelete(Resource):
    """Soft delete for open info additional files"""
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @auth.ismemberofgroups(IAOTeamWithKeycloackGroup.oi.value)
    def post(foiministryrequestid, foirequestid):
        try:
            request_json = request.get_json()
            fileids = FOIOpenInfoAdditionalFilesDeleteSchema().load(request_json)
            userid = AuthHelper.getuserid()
            result = openinfoservice().deleteopeninfoadditionalfiles(fileids, userid)
            if result.success:
                return {'status': result.success, 'message': result.message, 'id': result.identifier}, 200
        except ValidationError as err:
            return {'status': False, 'message': str(err)}, 400
        except KeyError as error:
            return {'status': False, 'message': CUSTOM_KEYERROR_MESSAGE + str(error)}, 400    
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500

@cors_preflight('POST,OPTIONS')
@API.route('/foiopeninfo/ministryrequest/<int:foiministryrequestid>/publishnow')
class FOIOpenInfoPublishNow(Resource):
    """Publish Now"""
    
    @staticmethod
    @cross_origin(origins=allowedorigins())
    @TRACER.trace()
    @auth.require
    @auth.ismemberofgroups(",".join(IAOTeamWithKeycloackGroup.list()))
    def post(foiministryrequestid):
        try:
            result = PublishNowRestService().publish_openinfo_now(foiministryrequestid)
            status_code = 200 if result.success else 500
            logging.info(
                "OpenInfo publish-now request completed for ministry request %s with status_code=%s success=%s identifier=%s message=%s",
                foiministryrequestid,
                status_code,
                result.success,
                result.identifier,
                result.message,
            )
            return {'status': result.success, 'message': result.message}, status_code
            
        except ValidationError as err:
            return {'status': False, 'message': str(err)}, 400
        except KeyError as error:
            return {'status': False, 'message': CUSTOM_KEYERROR_MESSAGE + str(error)}, 400    
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message': exception.message}, 500
        except redis.RedisError as redis_err:
            return {'status': False, 'message': f"Failed to queue request: {str(redis_err)}"}, 500

@cors_preflight('POST,OPTIONS')
@API.route('/foiopeninfo/ministryrequest/<int:foiministryrequestid>/unpublish')
class FOIOpenInfoUnpublish(Resource):
    """Unpublish"""
    
    @staticmethod
    @cross_origin(origins=allowedorigins())
    @TRACER.trace()
    @auth.require
    @auth.ismemberofgroups(",".join(IAOTeamWithKeycloackGroup.list()))
    def post(foiministryrequestid):
        try:
            # Fetch the data for unpublishing
            db_result = openinfoservice().getopeninforequestforunpublishing(foiministryrequestid)

            if not db_result:
                return {"status": True, "message": "No data found to unpublish for this request"}, 200

            result = db_result[0]

            try:
                # Convert to JSON
                json_data = json.dumps(result, default=str) 
            except (TypeError, ValueError) as err:
                return {'status': False, 'message': f"JSON serialization failed: {err}"}, 500

            # Push to queue for unpublishing
            redis_client.rpush(redis_stream_name, json_data)
            
            return {'status': True, 'message': 'Request queued for unpublishing successfully'}, 202
            
        except ValidationError as err:
            return {'status': False, 'message': str(err)}, 400
        except KeyError as error:
            return {'status': False, 'message': CUSTOM_KEYERROR_MESSAGE + str(error)}, 400    
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message': exception.message}, 500
        except redis.RedisError as redis_err:
            return {'status': False, 'message': f"Failed to queue request: {str(redis_err)}"}, 500

# for proactive disclosure
@cors_preflight('POST,OPTIONS')
@API.route('/foiopeninfo/ministryrequest/<int:foiministryrequestid>/pdpublishnow')
class FOIPDOpenInfoPublishNow(Resource):
    """Publish Now"""
    
    @staticmethod
    @cross_origin(origins=allowedorigins())
    @TRACER.trace()
    @auth.require
    @auth.ismemberofgroups(",".join(IAOTeamWithKeycloackGroup.list()))
    def post(foiministryrequestid):
        try:
            logging.info(
                "PD publish-now request received foiministryrequestid=%s",
                foiministryrequestid,
            )
            result = PublishNowRestService().publish_proactive_disclosure_now(foiministryrequestid)
            if not result.success:
                status_code = 500
            else:
                status_code = 200
            logging.info(
                "PD publish-now request completed for ministry request %s with status_code=%s success=%s identifier=%s message=%s",
                foiministryrequestid,
                status_code,
                result.success,
                result.identifier,
                result.message,
            )
            return {'status': result.success, 'message': result.message}, status_code
            
        except ValidationError as err:
            return {'status': False, 'message': str(err)}, 400
        except KeyError as error:
            return {'status': False, 'message': CUSTOM_KEYERROR_MESSAGE + str(error)}, 400    
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message': exception.message}, 500
        except redis.RedisError as redis_err:
            logging.exception(
                "PD publish-now queueing failed foiministryrequestid=%s error=%s",
                foiministryrequestid,
                redis_err,
            )
            return {'status': False, 'message': f"Failed to queue request: {str(redis_err)}"}, 500

@cors_preflight('POST,OPTIONS')
@API.route('/foiopeninfo/ministryrequest/<int:foiministryrequestid>/pdunpublish')
class FOIPDOpenInfoUnpublish(Resource):
    """Unpublish"""
    
    @staticmethod
    @cross_origin(origins=allowedorigins())
    @TRACER.trace()
    @auth.require
    @auth.ismemberofgroups(",".join(IAOTeamWithKeycloackGroup.list()))
    def post(foiministryrequestid):
        try:
            # Fetch the data for unpublishing
            db_result = openinfoservice().getpdopeninforequestforunpublishing(foiministryrequestid)
            
            if not db_result:
                return {"status": True, "message": "No data found to unpublish for this request"}, 200

            result = db_result[0]

            try:
                # Convert to JSON
                json_data = json.dumps(result, default=str) 
            except (TypeError, ValueError) as err:
                return {'status': False, 'message': f"JSON serialization failed: {err}"}, 500

            # Push to queue for unpublishing
            redis_client.rpush(redis_stream_name, json_data)
            
            return {'status': True, 'message': 'Request queued for unpublishing successfully'}, 202
            
        except ValidationError as err:
            return {'status': False, 'message': str(err)}, 400
        except KeyError as error:
            return {'status': False, 'message': CUSTOM_KEYERROR_MESSAGE + str(error)}, 400    
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message': exception.message}, 500
        except redis.RedisError as redis_err:
            return {'status': False, 'message': f"Failed to queue request: {str(redis_err)}"}, 500
