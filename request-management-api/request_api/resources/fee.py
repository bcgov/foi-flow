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
"""API endpoints for managing a Feee resource."""

from datetime import datetime

from flask import request, send_file, Response
from flask_cors import cross_origin
from flask_restx import Namespace, Resource

from request_api.services import FeeService
from request_api.services.document_generation_service import DocumentGenerationService
from request_api.utils.util import  cors_preflight, allowedorigins
from request_api.exceptions import BusinessException
API = Namespace('Fees', description='Endpoints for Fee and payments')


@cors_preflight('GET,OPTIONS')
@API.route('/fees/<string:code>')
class Fee(Resource):

    @staticmethod
    @cross_origin(origins=allowedorigins())
    def get(code):
        try:
            date = request.args.get('date', datetime.today().strftime('%Y-%m-%d'))
            quantity = int(request.args.get('quantity', 1))
            return FeeService.get_fee(code=code, quantity=quantity, valid_date=date), 200
        except BusinessException as e:
            return {'status': e.code, 'message': e.message}, e.status_code


@cors_preflight('POST,OPTIONS')
@API.route('/foirawrequests/<int:request_id>/payments')
class Payment(Resource):

    @staticmethod
    @cross_origin(origins=allowedorigins())
    def post(request_id: int):
        try:
            request_json = request.get_json()
            fee_service: FeeService = FeeService(request_id=request_id)
            pay_response = fee_service.init_payment(request_json)
            return pay_response, 201
        except BusinessException as e:
            return {'status': e.code, 'message': e.message}, e.status_code


@cors_preflight('PUT,OPTIONS')
@API.route('/foirawrequests/<int:request_id>/payments/<int:payment_id>')
class Payment(Resource):

    @staticmethod
    @cross_origin(origins=allowedorigins())
    def put(request_id: int, payment_id: int):
        try:
            request_json = request.get_json()
            fee_service: FeeService = FeeService(request_id=request_id, payment_id=payment_id)
            pay_response = fee_service.complete_payment(request_json)
            return pay_response, 201
        except BusinessException as e:
            return {'status': e.code, 'message': e.message}, e.status_code

@cors_preflight('POST,OPTIONS')
@API.route('/foirawrequests/<int:request_id>/payments/<int:payment_id>/receipt')
class Payment(Resource):

    @staticmethod
    @cross_origin(origins=allowedorigins())
    def post(request_id: int, payment_id: int):
        try:
            request_json = request.get_json()
            fee_service: FeeService = FeeService(request_id=request_id, payment_id=payment_id)
            paid = fee_service.check_if_paid()
            if paid is False:
                return {'status': False, 'message': "Fee has not been paid"}, 400
            document_service : DocumentGenerationService = DocumentGenerationService()
            response = document_service.generate_receipt(data= request_json)
            
            return Response(
                response= response.content,
                status= response.status_code,
                headers= dict(response.headers)
            )

        except BusinessException as e:
            return {'status': e.code, 'message': e.message}, e.status_code
