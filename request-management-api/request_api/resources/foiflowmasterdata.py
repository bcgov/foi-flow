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

from flask import request
from flask_restx import Namespace, Resource
from flask_cors import cross_origin
from request_api.auth import auth


from request_api.tracer import Tracer
from request_api.utils.util import  cors_preflight, allowedorigins, getrequiredmemberships
from request_api.exceptions import BusinessException
from request_api.services.applicantcategoryservice import applicantcategoryservice
from request_api.services.programareaservice import programareaservice
from request_api.services.deliverymodeservice import deliverymodeservice
from request_api.services.receivedmodeservice import receivedmodeservice
from request_api.services.divisionstageservice import divisionstageservice
from request_api.services.closereasonservice import closereasonservice
from request_api.schemas.foirequestsformslist import  FOIRequestsFormsList
from request_api.services.extensionreasonservice import extensionreasonservice
import json
import request_api
import requests
from aws_requests_auth.aws_auth import AWSRequestsAuth
import os
import uuid
from request_api.utils.cache import cache_filter, response_filter, clear_cache
from request_api.auth import AuthHelper

import boto3
from botocore.exceptions import ClientError
from botocore.config import Config

API = Namespace('FOI Flow Master Data', description='Endpoints for FOI Flow master data')
TRACER = Tracer.get_instance()

@cors_preflight('GET,OPTIONS')
@API.route('/foiflow/applicantcategories')
class FOIFlowApplicantCategories(Resource):
    """Retrieves all active application categories.
    """
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @request_api.cache.cached(
        key_prefix="applicantcategories",
        unless=cache_filter,
        response_filter=response_filter
        )
    def get():
        try:
            data = applicantcategoryservice().getapplicantcategories()
            jsondata = json.dumps(data)
            return jsondata , 200
        except BusinessException:
            return "Error happened while accessing applicant categories" , 500


@cors_preflight('GET,OPTIONS')
@API.route('/foiflow/programareas')
class FOIFlowProgramAreas(Resource):
    """Retrieves all active program areas.
    """
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @request_api.cache.cached(
        key_prefix="programareas",
        response_filter=response_filter,
        unless=cache_filter
        )
    def get():
        try:
            data = programareaservice().getprogramareas()
            jsondata = json.dumps(data)
            return jsondata , 200
        except BusinessException:
            return "Error happened while accessing program areas" , 500


@cors_preflight('GET,OPTIONS')
@API.route('/foiflow/programareasforuser')
class FOIFlowProgramAreas(Resource):
    """Retrieves all active program areas.
    """
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    #@request_api.cache.cached(key_prefix="programareas")
    def get():
        try:
            usertype = AuthHelper.getusertype()
            if (usertype == "iao"):
                data = programareaservice().getprogramareas()
            elif (usertype == 'ministry'):
                groups = AuthHelper.getministrygroups()
                data = programareaservice().getprogramareasforministryuser(groups)
            else:
                data = None

            jsondata = json.dumps(data)
            return jsondata , 200
        except BusinessException:
            return "Error happened while accessing program areas for user" , 500

@cors_preflight('GET,OPTIONS')
@API.route('/foiflow/deliverymodes')
class FOIFlowDeliveryModes(Resource):
    """Retrieves all active delivery modes.
    """
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @request_api.cache.cached(
        key_prefix="deliverymodes",
        unless=cache_filter,
        response_filter=response_filter
        )
    def get():
        try:
            data = deliverymodeservice().getdeliverymodes()
            jsondata = json.dumps(data)
            return jsondata , 200
        except BusinessException:
            return "Error happened while accessing delivery modes" , 500

@cors_preflight('GET,OPTIONS')
@API.route('/foiflow/receivedmodes')
class FOIFlowReceivedModes(Resource):
    """Retrieves all active received modes.
    """
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @request_api.cache.cached(
        key_prefix="receivedmodes",
        unless=cache_filter,
        response_filter=response_filter
        )
    def get():
        try:
            data = receivedmodeservice().getreceivedmodes()
            jsondata = json.dumps(data)
            return jsondata , 200
        except BusinessException:
            return "Error happened while accessing received modes" , 500

@cors_preflight('GET,OPTIONS')
@API.route('/foiflow/divisions/<bcgovcode>')
class FOIFlowDivisions(Resource):
    """Retrieves all active divisions for the passed in gov code    .
    """
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @request_api.cache.cached(
        unless=cache_filter,
        response_filter=response_filter
        )
    def get(bcgovcode):
        try:
            data = divisionstageservice().getdivisionandstages(bcgovcode)
            jsondata = json.dumps(data)
            return jsondata , 200
        except BusinessException:
            return "Error happened while accessing divisions" , 500

@cors_preflight('GET,OPTIONS')
@API.route('/foiflow/closereasons')
class FOIFlowCloseReasons(Resource):
    """Retrieves all active closure reasons.
    """
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @request_api.cache.cached(
        key_prefix="closereasons",
        unless=cache_filter,
        response_filter=response_filter
        )
    def get():
        try:
            data = closereasonservice().getclosereasons()
            jsondata = json.dumps(data)
            return jsondata , 200
        except BusinessException:
            return "Error happened while accessing received modes" , 500

@cors_preflight('GET,OPTIONS')
@API.route('/foiflow/oss/authheader')
class FOIFlowDocumentStorage(Resource):
    """Retrieves authentication properties for document storage.
    """
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
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

@cors_preflight('GET,OPTIONS')
@API.route('/foiflow/oss/presigned/<ministryrequestid>')
class FOIFlowS3Presigned(Resource):

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @auth.documentbelongstosameministry
    def get(ministryrequestid):
        try :
            formsbucket = os.getenv('OSS_S3_FORMS_BUCKET')
            accesskey = os.getenv('OSS_S3_FORMS_ACCESS_KEY_ID')
            secretkey = os.getenv('OSS_S3_FORMS_SECRET_ACCESS_KEY')
            s3host = os.getenv('OSS_S3_HOST')
            s3region = os.getenv('OSS_S3_REGION')
            filepath = request.args.get('filepath')

            s3client = boto3.client('s3',config=Config(signature_version='s3v4'),
            endpoint_url='https://{0}/'.format(s3host),
            aws_access_key_id= accesskey,
            aws_secret_access_key= secretkey,region_name= s3region
                )

            filename, file_extension = os.path.splitext(filepath)
            response = s3client.generate_presigned_url(
                ClientMethod='get_object',
                Params=   {'Bucket': formsbucket, 'Key': '{0}'.format(filepath),'ResponseContentType': '{0}/{1}'.format('image' if file_extension in ['.png','.jpg','.jpeg','.gif'] else 'application',file_extension.replace('.',''))},
                ExpiresIn=3600,HttpMethod='GET'
                )

            return json.dumps(response),200
        except BusinessException as exception:
         return {'status': exception.status_code, 'message':exception.message}, 500

@cors_preflight('GET,OPTIONS')
@API.route('/foiflow/extensionreasons')
class FOIFlowExtensionReasons(Resource):
    """Retrieves all active extension reasons.
    """
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @request_api.cache.cached(
        key_prefix="extensionreasons",
        unless=cache_filter,
        response_filter=response_filter
        )
    def get():
        try:
            data = extensionreasonservice().getextensionreasons()
            jsondata = json.dumps(data)
            return jsondata , 200
        except BusinessException as exception:
            return {'status': exception.status_code, 'message':exception.message}, 500

@cors_preflight('POST,OPTIONS')
@API.route('/foiflow/cache/flushall')
class FOIFlowProgramAreas(Resource):
    """Retrieves all active program areas.
    """
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def post():
        try:
            resp_flag = clear_cache()
            return {"success": resp_flag } , 200 if resp_flag == True else 500
        except BusinessException:
            return "Error happened while clearing cache" , 500