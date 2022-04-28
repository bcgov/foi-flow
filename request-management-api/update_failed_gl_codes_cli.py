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
"""CLI to update the GL codes for failed reconciliation.

CLI accepts the transaction numbers as the arguments and call PayBC API to update the GL codes.
"""
import getopt
import json
import sys
from typing import List

import requests
from flask import current_app
from request_api import app, create_app
from request_api.models import Payment, FeeCode, RevenueAccount
from request_api.services.fee_service import FeeService


def update_failed_gl_codes(transaction_numbers: List[str]) -> None:  # pylint: disable=too-many-locals
    """Update the GL codes in PayBC for the list of transactions."""
    paybc_transaction_url: str = current_app.config.get('PAYBC_API_BASE_URL')
    paybc_ref_number: str = current_app.config.get('PAYBC_REF_NUMBER')

    for transaction_number in transaction_numbers:
        try:
            print('Beginning transaction', transaction_number)
            # Find the payment record and create a fee_service instance.
            payment: Payment = Payment.find_paid_transaction(transaction_number)
            print('Found payment record')
            fee_service: FeeService = FeeService(request_id=payment.request_id, payment_id=payment.payment_id)

            payment_details: dict = fee_service.get_paybc_transaction_details()
            print('Received payment details', payment_details.get('paymentstatus'))
            # Process only of the status of the payment is PAID, else ignore
            if payment_details.get('paymentstatus') == 'PAID':
                has_gl_completed: bool = True
                # Check if any of the revenue line GL status is REJCTED or PAID (and not COMPLETED)
                for revenue in payment_details.get('revenue'):
                    print('Revenue GL Status', revenue.get('glstatus'))
                    if revenue.get('glstatus') in ('PAID', 'RJCT'):
                        has_gl_completed = False

                # Update the payment with new revenue account
                if not has_gl_completed:
                    # Find the fee code which is used for the payment
                    fee_code: FeeCode = FeeCode.find_by_id(payment.fee_code_id)
                    # Now find the latest fee_code record for the same code to make sure we use latest GL config.
                    fee_code: FeeCode = FeeCode.get_fee(code=fee_code.code, valid_date=None)
                    revenue_account: RevenueAccount = RevenueAccount.find_by_id(fee_code.revenue_account_id)
                    # Build the new payload.
                    post_revenue_payload = {
                        'revenue': [
                            {
                                'lineNumber': '1',
                                'revenueAccount': f'{revenue_account.client}.{revenue_account.responsibility_centre}'
                                                  f'.{revenue_account.service_line}.{revenue_account.stob}'
                                                  f'.{revenue_account.project_code}.000000.0000',
                                'revenueAmount': format(payment.total, '.2f')
                            }
                        ]
                    }

                    access_token = fee_service.get_paybc_token().json().get('access_token')
                    endpoint = f'{paybc_transaction_url}/paybc/payment/{paybc_ref_number}/{transaction_number}'
                    print('Update GL Status endpoint', endpoint, post_revenue_payload)
                    response = requests.post(
                        endpoint,
                        headers={
                            'Authorization': f'Bearer {access_token}',
                            'Content-Type': 'application/json'
                        },
                        timeout=current_app.config.get('CONNECT_TIMEOUT'),
                        data=json.dumps(post_revenue_payload)
                    )
                    response.raise_for_status()
                    print('Successfully updated for transaction', transaction_number)
                    print(response.json())

        except Exception as e:  # pylint: disable=broad-except
            print(e)
            print('Failed processing of', transaction_number)


if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ht:", ["txns="])
    except getopt.GetoptError:
        sys.exit(2)

    failed_transaction_numbers: List[str] = []
    for opt, arg in opts:
        if opt == '-h':
            sys.exit()
        elif opt in ("-t", "--txns"):
            failed_transaction_numbers = [x.strip() for x in arg.split(',')]
    with app.app_context():
        create_app()
        update_failed_gl_codes(failed_transaction_numbers)
