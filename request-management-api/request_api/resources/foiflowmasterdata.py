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
"""API endpoints for managing a FOI Requests resource."""

from flask import g, request
from flask_restx import Namespace, Resource
from flask_expects_json import expects_json
from flask_cors import cross_origin
from request_api.auth import auth


from request_api.tracer import Tracer
from request_api.utils.util import  cors_preflight, allowedOrigins, getrequiredmemberships
from request_api.exceptions import BusinessException, Error
from request_api.services.applicantcategoryservice import applicantcategoryservice
from request_api.services.programareaservice import programareaservice
from request_api.services.deliverymodeservice import deliverymodeservice
from request_api.services.receivedmodeservice import receivedmodeservice
from request_api.services.divisionstageservice import divisionstageservice
from request_api.services.closereasonservice import closereasonservice
from request_api.schemas.foirequestsformslist import  FOIRequestsFormsList
import json
import request_api
import requests
from aws_requests_auth.aws_auth import AWSRequestsAuth
import os
import uuid

API = Namespace('FOI Flow Master Data', description='Endpoints for FOI Flow master data')
TRACER = Tracer.get_instance()

@cors_preflight('GET,OPTIONS')
@API.route('/foiflow/applicantcategories')
class FOIFlowApplicantCategories(Resource):

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedOrigins())      
    @auth.require
    @request_api.cache.cached(key_prefix="applicantcategories")
    def get():
        try:
            data = applicantcategoryservice().getapplicantcategories()
            jsondata = json.dumps(data)
            return jsondata , 200
        except:
            return "Error happened while accessing applicant categories" , 500


@cors_preflight('GET,OPTIONS')
@API.route('/foiflow/programareas')
class FOIFlowProgramAreas(Resource):

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedOrigins())      
    @auth.require
    @request_api.cache.cached(key_prefix="programareas")
    def get():
        try:
            data = programareaservice().getprogramareas()
            jsondata = json.dumps(data)
            return jsondata , 200
        except:
            return "Error happened while accessing applicant categories" , 500

@cors_preflight('GET,OPTIONS')
@API.route('/foiflow/deliverymodes')
class FOIFlowDeliveryModes(Resource):

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedOrigins())       
    @auth.require
    @request_api.cache.cached(key_prefix="deliverymodes")
    def get():
        try:
            data = deliverymodeservice().getdeliverymodes()
            jsondata = json.dumps(data)
            return jsondata , 200
        except:
            return "Error happened while accessing delivery modes" , 500

@cors_preflight('GET,OPTIONS')
@API.route('/foiflow/receivedmodes')
class FOIFlowReceivedModes(Resource):

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedOrigins())       
    @auth.require
    @request_api.cache.cached(key_prefix="receivedmodes")
    def get():
        try:
            data = receivedmodeservice().getreceivedmodes()
            jsondata = json.dumps(data)
            return jsondata , 200
        except:
            return "Error happened while accessing received modes" , 500

@cors_preflight('GET,OPTIONS')
@API.route('/foiflow/divisions/<bcgovcode>')
class FOIFlowDivisions(Resource):

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedOrigins())       
    @auth.require
    def get(bcgovcode):
        try:
            data = divisionstageservice().getdivisionandstages(bcgovcode)
            jsondata = json.dumps(data)
            return jsondata , 200
        except:
            return "Error happened while accessing divisions" , 500 
        
@cors_preflight('GET,OPTIONS')
@API.route('/foiflow/closereasons')
class FOIFlowCloseReasons(Resource):

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedOrigins())       
    @auth.require
    @request_api.cache.cached(key_prefix="closereasons")
    def get():
        try:
            data = closereasonservice().getclosereasons()
            jsondata = json.dumps(data)
            return jsondata , 200
        except:
            return "Error happened while accessing received modes" , 500

@cors_preflight('GET,OPTIONS')
@API.route('/foiflow/oss/authheader')
class FOIFlowDocumentStorage(Resource):

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedOrigins())       
    @auth.require
    @auth.ismemberofgroups(getrequiredmemberships())
    def post():
        try:

            formsbucket = os.getenv('OSS_S3_FORMS_BUCKET')
            accesskey = os.getenv('OSS_S3_FORMS_ACCESS_KEY_ID') 
            secretkey = os.getenv('OSS_S3_FORMS_SECRET_ACCESS_KEY')
            s3host = os.getenv('OSS_S3_HOST')
            s3region = os.getenv('OSS_S3_REGION')
            s3service = os.getenv('OSS_S3_SERVICE')

            if(accesskey is None or secretkey is None or s3host is None or formsbucket is None):
                return {'status': "Configuration Issue", 'message':"accesskey is None or secretkey is None or S3 host is None or formsbucket is None"}, 500

            requestfilejson = request.get_json()

            for file in requestfilejson:                
                foirequestform = FOIRequestsFormsList().load(file)                
                ministrycode = foirequestform.get('ministrycode')
                requestnumber = foirequestform.get('requestnumber')
                filestatustransition = foirequestform.get('filestatustransition')
                filename = foirequestform.get('filename')
                s3sourceuri = foirequestform.get('s3sourceuri')
                filenamesplittext = os.path.splitext(filename)
                uniquefilename = '{0}{1}'.format(uuid.uuid4(),filenamesplittext[1])                
                auth = AWSRequestsAuth(aws_access_key=accesskey,
                        aws_secret_access_key=secretkey,
                        aws_host=s3host,
                        aws_region=s3region,
                        aws_service=s3service) 

                s3uri = s3sourceuri if s3sourceuri is not None else 'https://{0}/{1}/{2}/{3}/{4}/{5}'.format(s3host,formsbucket,ministrycode,requestnumber,filestatustransition,uniquefilename)        
                
                response = requests.put(s3uri,data=None,auth=auth) if s3sourceuri is None  else requests.get(s3uri,auth=auth)


                file['filepath']=s3uri
                file['authheader']=response.request.headers['Authorization'] 
                file['amzdate']=response.request.headers['x-amz-date']
                file['uniquefilename']=uniquefilename if s3sourceuri is None else ''
                file['filestatustransition']=filestatustransition  if s3sourceuri is None else ''
                
                
            return json.dumps(requestfilejson) , 200
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500
    
            
