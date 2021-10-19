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

from flask import request
from flask_cors import cross_origin
from flask_restx import Namespace, Resource

from request_api.services import FeeService
from request_api.utils.util import cors_preflight, allowedOrigins
from request_api.exceptions import BusinessException, Error

API = Namespace('Fees', description='Endpoints for Fee and payments')


@cors_preflight('GET,OPTIONS')
@API.route('/fees/<string:code>')
class Fee(Resource):

    @staticmethod
    @cross_origin(origins=allowedOrigins())
    def get(code):
        try:
            date = request.args.get('date', datetime.today().strftime('%Y-%m-%d'))
            quantity = int(request.args.get('quantity', 1))
            return FeeService.get_fee(code=code, quantity=quantity, valid_date=date), 200
        except BusinessException as e:
            return {'status': e.code, 'message': e.message}, e.status_code


@cors_preflight('POST,OPTIONS')
@API.route('/foirequests/<int:request_id>/payments')
class Payment(Resource):

    @staticmethod
    @cross_origin(origins=allowedOrigins())
    def post(request_id: int):
        try:
            request_json = request.get_json()
            fee_service: FeeService = FeeService(request_id=request_id)
            pay_response = fee_service.init_payment(request_json)
            return pay_response, 201
        except BusinessException as e:
            return {'status': e.code, 'message': e.message}, e.status_code


@cors_preflight('PUT,OPTIONS')
@API.route('/foirequests/<int:request_id>/payments/<int:payment_id>')
class Payment(Resource):

    @staticmethod
    @cross_origin(origins=allowedOrigins())
    def put(request_id: int, payment_id: int):
        try:
            request_json = request.get_json()
            fee_service: FeeService = FeeService(request_id=request_id, payment_id=payment_id)
            pay_response = fee_service.complete_payment(request_json)
            return pay_response, 201
        except BusinessException as e:
            return {'status': e.code, 'message': e.message}, e.status_code
