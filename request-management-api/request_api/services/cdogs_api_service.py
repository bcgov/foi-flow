# Copyright © 2019 Province of British Columbia
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


"""Service for receipt generation."""
import base64
import json
import os
import re

from flask import current_app
from urllib.parse import parse_qsl
import requests
from request_api.exceptions import BusinessException, Error


class cdogsApiService:
    """cdogs api Service class."""

    fileDir = os.path.dirname(os.path.realpath('__file__'))
    receiptTemplatePath = os.path.join(fileDir, 'request_api/receipt_templates/receipt_in_word.docx')

    def generate_receipt(self, templateHashCode: str, data):
        request_body = {
            "options": {
                "cachereport": False,
                "convertTo": "pdf",
                "overwrite": True,
                "reportName": "Receipt"
            },
            "data": data
        }
        json_request_body = json.dumps(request_body)
        access_token = self._get_access_token()
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }

        # if templateHashCode is None:
        #     templateHashCode = self.upload_template(access_token= access_token)

        url = f"{current_app.config['CDOGS_BASE_URL']}/api/v2/template/{templateHashCode}/render"
        try:
            return requests.post(url, data= json_request_body, headers= headers)
        except BaseException as e:
            raise e

    def upload_template(self, templateFilePath: str = receiptTemplatePath, access_token: str = None):
        # return '7b47a9f88f9f967d4f8ff72811615625190e113f84a03d3e606b80e262553003'
        
        headers = {
        "Authorization": f'Bearer {access_token}'
        }

        url = f"{current_app.config['CDOGS_BASE_URL']}/api/v2/template"
        template = {'template':('template', open(templateFilePath, 'rb'), "multipart/form-data")}

        try:
            response = requests.post(url, headers= headers, files= template)
            
            if response.status_code == 405 and response.content['detail'] is not None:
                return re.findall(r"'([^']*)'", response.content['detail'])[0]
            
            if hasattr(response.headers, "X-Template-Hash") is False:
                raise BusinessException(Error.DATA_NOT_FOUND)

            return response.headers['X-Template-Hash'];
        except BaseException as e:
            raise e

    def check_template_cached(self, template_hash_code: str, access_token = None):
        # return '7b47a9f88f9f967d4f8ff72811615625190e113f84a03d3e606b80e262553003'
        
        headers = {
        "Authorization": f'Bearer {access_token if access_token else self._get_access_token()}'
        }

        url = f"{current_app.config['CDOGS_BASE_URL']}/api/v2/template/{template_hash_code}"

        try:
            response = requests.post(url, headers= headers)
            return response.status_code == 200
        except BaseException as e:
            raise e
        

    @staticmethod
    def _get_access_token():
        print("passed")
        token_url = current_app.config['CDOGS_TOKEN_URL']
        service_client = current_app.config['CDOGS_SERVICE_CLIENT']
        service_client_secret = current_app.config['CDOGS_SERVICE_CLIENT_SECRET']
        cdogs_access_token = current_app.config['CDOGS_ACCESS_TOKEN']

        # if cdogs_access_token is not None:
        #     return cdogs_access_token

        print("Get new token")
        basic_auth_encoded = base64.b64encode(
            bytes(service_client + ':' + service_client_secret, 'utf-8')).decode('utf-8')
        data = 'grant_type=client_credentials'
        response = requests.post(
            token_url,
            data=data,
            headers={
                'Authorization': f'Basic {basic_auth_encoded}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        )

        response_json = response.json()
        return response_json['access_token']




