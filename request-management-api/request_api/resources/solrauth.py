from flask import g, request
from flask_restx import Namespace, Resource, cors
from request_api.auth import auth
from request_api.auth import auth, AuthHelper
from request_api.tracer import Tracer
from request_api.utils.util import  cors_preflight, allowedorigins
from request_api.exceptions import BusinessException, Error
from request_api.services.requestservice import requestservice
from flask_cors import cross_origin
import base64
import os

API = Namespace('FOISolr', description='Endpoints for FOI Solr Search')
TRACER = Tracer.get_instance()

@cors_preflight('GET,OPTIONS')
@API.route('/foicrosstextsearch/authstring')
class FOISolr(Resource):
    """Get users"""

       
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @auth.isiao
    def get():      
        try:                        
            usernamepassword ="%s:%s" % (os.getenv("FOI_SOLR_USERNAME"),os.getenv("FOI_SOLR_PASSWORD"))     
            unamepassword_bytes = usernamepassword.encode("utf-8")
            # Encode the bytes to Base64
            base64_encoded = base64.b64encode(unamepassword_bytes)
            return base64_encoded, 200
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500
        

@cors_preflight('POST,OPTIONS')
@API.route('/foicrosstextsearch/requests')
class FOISolrSearch(Resource):
    """Get request details for 
    keyword search dashboard"""

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @auth.isiao
    def post():      
        try:
            #print("\nArgs:",request.args)
            payload = request.get_json()
            if 'requestnumbers' in payload:
                requestnumbers = payload["requestnumbers"]                      
                requestdetails = requestservice().getrequestsdetailsforsearch(requestnumbers)
                return requestdetails, 200
            else:
                raise Exception("Request Numbers are not provided for searching from SOLR result.")
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500