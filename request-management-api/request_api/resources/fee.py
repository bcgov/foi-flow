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
import json
import asyncio

from request_api.services import FeeService
from request_api.services.cfrfeeservice import cfrfeeservice
from request_api.services.requestservice import requestservice
from request_api.services.external.storageservice import storageservice
from request_api.services.eventservice import eventservice

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
            fee_service: FeeService = FeeService(request_id=request_id, code=request_json['fee_code'])
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
            pay_response = fee_service.complete_payment(request_json)[0]
            return pay_response, 201
        except BusinessException as e:
            return {'status': e.code, 'message': e.message}, e.status_code


@cors_preflight('PUT,OPTIONS')
@API.route('/foirequests/<int:ministry_request_id>/payments/<int:payment_id>')
class Payment(Resource):

    @staticmethod
    @cross_origin(origins=allowedorigins())
    def put(ministry_request_id: int, payment_id: int):
        try:
            request_json = request.get_json()
            fee_service: FeeService = FeeService(request_id=ministry_request_id, payment_id=payment_id)
            response, parsed_args = fee_service.complete_payment(request_json)
            if (response['status'] == 'PAID'):
                cfrfeeservice().paycfrfee(ministry_request_id, float(parsed_args.get('trnAmount')))
                receipt_template_path='request_api/receipt_templates/cfr_fee_payment_receipt.docx'
                data = requestservice().getrequestdetails(1, ministry_request_id)
                data['waivedAmount'] = data['cfrfee']['feedata']['estimatedlocatinghrs'] * 30 if data['cfrfee']['feedata']['estimatedlocatinghrs'] < 3 else 90
                data.update({'paymentInfo': {
                    'paymentDate': fee_service.payment['completed_on'],
                    'orderId': fee_service.payment['order_id'],
                    'transactionId': fee_service.payment['transaction_number'],
                    'cardType': parsed_args['cardType']
                }})
                document_service : DocumentGenerationService = DocumentGenerationService('cfr_fee_payment_receipt')
                receipt = document_service.generate_receipt(data,receipt_template_path)
                document_service.upload_receipt('fee_estimate_payment_receipt.pdf', receipt.content, ministry_request_id, data['bcgovcode'], data['idNumber'])
                result = requestservice().updaterequeststatus(1, ministry_request_id, 2)
                if result.success == True:
                    asyncio.ensure_future(eventservice().postpaymentevent(ministry_request_id))
                    requestservice().postfeeeventtoworkflow(result.args[0][0]["axisrequestid"], "PAID")
                    asyncio.ensure_future(eventservice().postevent(ministry_request_id,"ministryrequest","System","System", False))
            return response, 201
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
            documenttypename='receipt'
            document_service : DocumentGenerationService = DocumentGenerationService(documenttypename)
            response = document_service.generate_receipt(data= request_json)
            
            return Response(
                response= response.content,
                status= response.status_code,
                headers= dict(response.headers)
            )

        except BusinessException as e:
            return {'status': e.code, 'message': e.message}, e.status_code
