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
import requests
from request_api.exceptions import BusinessException, Error


class CdogsApiService:
    """cdogs api Service class."""

    file_dir = os.path.dirname(os.path.realpath('__file__'))
    receipt_template_path = os.path.join(file_dir, 'request_api/receipt_templates/receipt_word.docx')

    def generate_receipt(self, template_hash_code: str, data):
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
        
        url = f"{current_app.config['CDOGS_BASE_URL']}/api/v2/template/{template_hash_code}/render"
        return requests.post(url, data= json_request_body, headers= headers)

    def upload_template(self, template_file_path: str = receipt_template_path, access_token: str = None):

        headers = {
        "Authorization": f'Bearer {access_token if access_token else self._get_access_token()}'
        }

        url = f"{current_app.config['CDOGS_BASE_URL']}/api/v2/template"
        template = {'template':('template', open(template_file_path, 'rb'), "multipart/form-data")}

        current_app.logger.info('Uploading template %s', template_file_path)
        response = requests.post(url, headers= headers, files= template)
        
        if response.status_code == 200:
            if hasattr(response.headers, "X-Template-Hash") is False:
                raise BusinessException(Error.DATA_NOT_FOUND)

            current_app.logger.info('Returning new hash %s', response.headers['X-Template-Hash'])
            return response.headers['X-Template-Hash'];
    
        response_json = json.loads(response.content)
        
        if response.status_code == 405 and response_json['detail'] is not None:
            match = re.findall(r"Hash '(.*?)'", response_json['detail']);
            if match:
                current_app.logger.info('Template already hashed with code %s', match[0])
                return match[0]
            
        raise BusinessException(Error.UNDEFINED_ERROR)

    def check_template_cached(self, template_hash_code: str, access_token = None):

        headers = {
        "Authorization": f'Bearer {access_token if access_token else self._get_access_token()}'
        }

        url = f"{current_app.config['CDOGS_BASE_URL']}/api/v2/template/{template_hash_code}"

        response = requests.post(url, headers= headers)
        return response.status_code == 200
        

    @staticmethod
    def _get_access_token():
        token_url = current_app.config['CDOGS_TOKEN_URL']
        service_client = current_app.config['CDOGS_SERVICE_CLIENT']
        service_client_secret = current_app.config['CDOGS_SERVICE_CLIENT_SECRET']

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