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

from flask import current_app
from urllib.parse import parse_qsl
import requests
from request_api.exceptions import BusinessException, Error
from request_api.models import DocumentTemplate, DocumentType, Payment
from request_api.services.cdogs_api_service import cdogsApiService


class DocumentGenerationService:
    """document generation Service class."""

    def __init__(self):
        self.cdgos_api_service = cdogsApiService()
        receipt_document_type : DocumentType = DocumentType.get_document_type_by_name('receipt')
        if receipt_document_type is None:
            raise BusinessException(Error.DATA_NOT_FOUND)
        
        self.receipt_template : DocumentTemplate = DocumentTemplate \
            .get_template_by_type(document_type_id = receipt_document_type.document_type_id)
        if self.receipt_template is None:
            raise BusinessException(Error.DATA_NOT_FOUND)  
        

    def generate_receipt(self, data):
        template_cached = False
        if self.receipt_template.cdogs_hash_code:
            current_app.logger.info('Checking if template %s is cached', self.receipt_template.cdogs_hash_code)
            template_cached = self.cdgos_api_service.check_template_cached(self.receipt_template.cdogs_hash_code)
            
        if self.receipt_template.cdogs_hash_code is None or not template_cached:
            current_app.logger.info('Uploading new template')
            self.receipt_template.cdogs_hash_code = self.cdgos_api_service.upload_template()
            self.receipt_template.flush()
            self.receipt_template.commit()     
        
        current_app.logger.info('Generating receipt')
        return self.cdgos_api_service.generate_receipt(templateHashCode= self.receipt_template.cdogs_hash_code, data= data)
            
        
        






