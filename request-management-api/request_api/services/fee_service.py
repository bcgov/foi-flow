import base64
from datetime import date
from datetime import datetime
from typing import Dict
from urllib.parse import unquote_plus, urlencode

import pytz
import requests
from flask import current_app

from request_api.exceptions import BusinessException, Error
from request_api.models import FeeCode, Payment, RevenueAccount, FOIRawRequest, FOIMinistryRequest
from request_api.services.cfrfeeservice import cfrfeeservice
from request_api.utils.enums import FeeType
from .hash_service import HashService


class FeeService:
    """ FOI Fee management service

    This service class manages all CRUD operations related to Fee

    """

    def __init__(self, request_id: int, code: str=None, payment_id=None):
        self.request_id = request_id
        if payment_id:
            self.payment: Payment = Payment.find_by_id(payment_id)
            self.fee_code: FeeCode = FeeCode.find_by_id(self.payment.fee_code_id)
        else:
            self.payment = None
            self.fee_code: FeeCode = FeeCode.get_fee(code=code, valid_date=date.today())
        if not self.fee_code:
            raise BusinessException(Error.INVALID_INPUT)

        # If application fee, use raw request id, else use minsitry request id
        if self.fee_code.code == FeeType.application.value:
            self.request = FOIRawRequest.get_request(request_id)
            if self.request is None:
                raise BusinessException(Error.INVALID_INPUT)
        else:
            self.request = FOIMinistryRequest.getrequestbyministryrequestid(request_id)
            if self.request is None:
                raise BusinessException(Error.INVALID_INPUT)

    @staticmethod
    def get_fee(code: str, quantity: int, valid_date: date):
        """Return fee details."""
        fee_code: FeeCode = FeeCode.get_fee(
            code=code, valid_date=valid_date
        )
        if not fee_code:
            raise BusinessException(Error.DATA_NOT_FOUND)

        fee_response = dict(
            fee_code=code,
            fee=fee_code.fee,
            quantity=quantity,
            total=quantity * fee_code.fee,
            description=fee_code.description
        )

        return fee_response

    def init_payment(self, pay_request: Dict):
        return_route = pay_request.get('return_route')
        quantity = int(pay_request.get('quantity', 1))
        if self.fee_code.code == FeeType.processing.value:
            total = self._get_cfr_fee(self.request_id, pay_request)
        else:
            total = quantity * self.fee_code.fee
        self.payment = Payment(
            fee_code_id=self.fee_code.fee_code_id,
            quantity=quantity,
            total=total,
            status='PENDING',
            request_id=self.request_id
        ).flush()

        self.payment.paybc_url = self._get_paybc_url(self.fee_code, return_route)
        self.payment.transaction_number = self._get_transaction_number()
        self.payment.commit()
        pay_response = self._dump()
        return pay_response

    def complete_payment(self, pay_response: Dict):
        """Complete payment."""
        response_url = pay_response.get('response_url')
        current_app.logger.debug('response_url : %s', response_url)
        
        if self.payment.status == 'PAID' or not response_url:
            raise BusinessException(Error.INVALID_INPUT)

        self.payment.response_url = response_url
        self.payment.commit()

        parsed_args = HashService.parse_url_params(response_url)
        
        # Validate transaction number
        if self.payment.transaction_number != parsed_args.get('pbcTxnNumber'):
            raise BusinessException(Error.INVALID_INPUT)

        # Check if trnApproved is 1=Success, 0=Declined
        trn_approved: bool = parsed_args.get('trnApproved') == '1'
        if trn_approved:
            self._validate_hash(parsed_args, response_url)

        #  Add paybc api call to verify
        #  handle duplicate payment response.
        paybc_status = None
        if trn_approved or parsed_args.get('trnNumber', '').upper() == 'DUPLICATE PAYMENT':
            paybc_status = self._validate_with_paybc(trn_approved)

        self.payment.order_id = parsed_args.get('trnOrderId')
        self.payment.completed_on = datetime.now()
        self.payment.status = 'PAID' if paybc_status == 'PAID' else parsed_args.get('messageText').upper()
        self.payment.commit()

        return self._dump(), parsed_args

    def check_if_paid(self):
        """Check payment."""

        return self.payment.status == 'PAID'

    def _validate_with_paybc(self, trn_approved):
        paybc_status = None
        paybc_response = self.get_paybc_transaction_details()
        print("<<<<<<<<< paybc_response >>>>>>>>>>>>>>")
        print(paybc_response)
        if trn_approved and (paybc_status := paybc_response.get('paymentstatus')) != 'PAID':
            raise BusinessException(Error.INVALID_INPUT)
        if paybc_status == 'PAID' and self.payment.total != float(paybc_response.get('trnamount')):
            raise BusinessException(Error.INVALID_INPUT)
        return paybc_status

    def _validate_hash(self, parsed_args, response_url):
        # validate if hashValue matches with rest of the values hashed
        hash_value = parsed_args.pop('hashValue', None)
        pay_response_url_without_hash = urlencode(parsed_args)
        if not HashService.is_valid_checksum(pay_response_url_without_hash, hash_value):
            current_app.logger.warning(f'Transaction is approved, but hash is not matching : {response_url}')
            raise BusinessException(Error.INVALID_INPUT)

    def _dump(self):
        pay_response = dict(
            paybc_url=self.payment.paybc_url,
            payment_id=self.payment.payment_id,
            request_id=self.payment.request_id,
            status=self.payment.status,
            total=self.payment.total
        )
        return pay_response

    def _get_paybc_url(self, fee_code: FeeCode, return_route):
        """Return the payment system url."""
        date_val = datetime.now().astimezone(pytz.timezone(current_app.config['LEGISLATIVE_TIMEZONE'])).strftime(
            '%Y-%m-%d')
        if self.fee_code.code == FeeType.application.value:
            base_url = current_app.config['FOI_WEB_PAY_URL']
        if self.fee_code.code == FeeType.processing.value:
            base_url = current_app.config['FOI_FFA_URL']
        return_url = f"{base_url}{return_route if return_route else ''}/{self.payment.request_id}/{self.payment.payment_id}"
        revenue_account: RevenueAccount = RevenueAccount.find_by_id(fee_code.revenue_account_id)

        url_params_dict = {'trnDate': date_val,
                           'pbcRefNumber': current_app.config.get('PAYBC_REF_NUMBER'),
                           'glDate': date_val,
                           'description': 'Direct_Sale',
                           'trnNumber': self._get_transaction_number(),
                           'trnAmount': self.payment.total,
                           'paymentMethod': 'CC',
                           'redirectUri': return_url,
                           'currency': 'CAD',
                           'revenue': self._get_gl_coding(self.payment.total, revenue_account)
                           }

        url_params = urlencode(url_params_dict)
        # unquote is used below so that unescaped url string can be hashed
        url_params_dict['hashValue'] = HashService.encode(unquote_plus(url_params))
        encoded_query_params = urlencode(url_params_dict)  # encode it again to inlcude the hash
        paybc_url = current_app.config.get('PAYBC_PORTAL_URL')
        return f'{paybc_url}?{encoded_query_params}'

    @staticmethod
    def _get_gl_coding(total, revenue_account: RevenueAccount):
        return f'1:{revenue_account.client}.{revenue_account.responsibility_centre}.' \
               f'{revenue_account.service_line}.{revenue_account.stob}.{revenue_account.project_code}' \
               f'.000000.0000' \
               f":{format(total, '.2f')}"

    def _get_transaction_number(self):
        return f"{current_app.config.get('PAYBC_TXN_PREFIX')}{self.payment.payment_id:0>8}"

    def get_paybc_transaction_details(self):
        # Call PAYBC web service, get access token and use it in get txn call
        access_token = self.get_paybc_token().json().get('access_token')

        paybc_transaction_url: str = current_app.config.get('PAYBC_API_BASE_URL')
        paybc_ref_number: str = current_app.config.get('PAYBC_REF_NUMBER')

        endpoint = f'{paybc_transaction_url}/paybc/payment/{paybc_ref_number}/{self.payment.transaction_number}'
        response = requests.get(
            endpoint,
            headers={
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            },
            timeout=current_app.config.get('CONNECT_TIMEOUT')
        )
        print("<<<<<<< response >>>>>>>>>")
        print(response)
        return response.json()

    def get_paybc_token(self):
        """Generate oauth token from payBC which will be used for all communication."""
        current_app.logger.debug('<Getting token')
        token_url = current_app.config.get('PAYBC_API_BASE_URL') + '/oauth/token'
        basic_auth_encoded = base64.b64encode(
            bytes(current_app.config.get('PAYBC_API_CLIENT') + ':' + current_app.config.get(
                'PAYBC_API_SECRET'), 'utf-8')).decode('utf-8')
        data = 'grant_type=client_credentials'
        response = requests.post(
            token_url,
            data=data,
            headers={
                'Authorization': f'Basic {basic_auth_encoded}',
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            timeout=current_app.config.get('CONNECT_TIMEOUT')
        )

        current_app.logger.debug('>Getting token')
        return response

    def _get_cfr_fee(self, ministry_request_id, pay_request):
        if pay_request.get('retry', False):
            return Payment.find_failed_transaction(pay_request['transaction_number']).total
        else:
            fee = cfrfeeservice().getapprovedcfrfee(ministry_request_id)['feedata']['balanceremaining']
            if pay_request.get('half', False):
                return fee/2
            else:
                return fee
