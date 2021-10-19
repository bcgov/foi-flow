from datetime import date
from datetime import datetime
from typing import Dict
from urllib.parse import unquote_plus, urlencode

import pytz
from flask import current_app

from request_api.exceptions import BusinessException, Error
from request_api.models import FeeCode, Payment, RevenueAccount, FOIRawRequest
from .hash_service import HashService


class FeeService:
    """ FOI Fee management service

    This service class manages all CRUD operations related to Fee

    """

    def __init__(self, request_id: int, payment_id=None):
        self.request_id = request_id
        if FOIRawRequest.get_request(request_id) is None:
            raise BusinessException(Error.INVALID_INPUT)
        self.payment: Payment = Payment.find_by_id(payment_id) if payment_id else None

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
        """Initialize payment request."""
        fee = FeeCode.get_fee(
            code=pay_request.get('fee_code'), valid_date=date.today()
        )
        if not fee:
            raise BusinessException(Error.INVALID_INPUT)

        quantity = int(pay_request.get('quantity', 1))
        self.payment = Payment(
            fee_code_id=fee.fee_code_id,
            quantity=quantity,
            total=quantity * fee.fee,
            status='PENDING',
            request_id=self.request_id
        ).flush()

        self.payment.paybc_url = self._get_paybc_url(fee)
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

        # validate if hashValue matches with rest of the values hashed
        hash_value = parsed_args.pop('hashValue', None)
        pay_response_url_without_hash = urlencode(parsed_args)

        # Check if trnApproved is 1=Success, 0=Declined
        trn_approved: str = parsed_args.get('trnApproved')
        if trn_approved == '1' and not HashService.is_valid_checksum(pay_response_url_without_hash, hash_value):
            current_app.logger.warning(f'Transaction is approved, but hash is not matching : {response_url}')
            raise BusinessException(Error.INVALID_INPUT)

        self.payment.order_id = parsed_args.get('trnOrderId')
        self.payment.completed_on = datetime.now()
        if trn_approved == '1':
            self.payment.status = 'PAID'
        else:
            self.payment.status = parsed_args.get('messageText').upper()
        self.payment.commit()

        return self._dump()

    def _dump(self):
        pay_response = dict(
            paybc_url=self.payment.paybc_url,
            payment_id=self.payment.payment_id,
            request_id=self.payment.request_id,
            status=self.payment.status
        )
        return pay_response

    def _get_paybc_url(self, fee_code: FeeCode):
        """Return the payment system url."""
        date_val = datetime.now().astimezone(pytz.timezone(current_app.config['LEGISLATIVE_TIMEZONE'])).strftime(
            '%Y-%m-%d')
        return_url = f"{current_app.config['FOI_WEB_PAY_URL']}/{self.payment.request_id}/{self.payment.payment_id}"  # TODO
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
