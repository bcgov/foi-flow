import json

import pytest

from request_api.services.hash_service import HashService


@pytest.mark.parametrize('fee_code, expected_status_code', [('FOI0001', 200), ('TEST', 404)])
def test_get_fee(app, client, fee_code, expected_status_code):
    response = client.get(f'/api/fees/{fee_code}', content_type='application/json')
    assert response.status_code == expected_status_code


def test_create_payment(app, client):
    foi_req = client.post(f'/api/foirawrequests', data=json.dumps({'requestData': {}}), content_type='application/json')
    request_id = foi_req.json.get('id')
    fee_code = 'FOI0001'
    pay_response = client.post(f'/api/foirawrequests/{request_id}/payments', data=json.dumps({
        'fee_code': fee_code,
        'quantity': 5
    }), content_type='application/json')
    assert pay_response.status_code == 201
    fee_response = client.get(f'/api/fees/{fee_code}?quantity=5', content_type='application/json')
    assert pay_response.json.get('total') == fee_response.json.get('total')
    assert pay_response.json.get('status') == 'PENDING'


def test_complete_payment(app, client, monkeypatch):
    with app.app_context():
        fee_code = 'FOI0001'
        quantity = 5

        total_fee = client.get(f'/api/fees/{fee_code}?quantity={quantity}', content_type='application/json')

        # Mock paybc response to return success message
        def mock_paybc_response(self):  # pylint: disable=unused-argument; mocks of library methods
            return {
                'paymentstatus': 'PAID',
                'trnamount': total_fee.json.get('total')
            }

        monkeypatch.setattr('request_api.services.fee_service.FeeService._get_paybc_transaction_details',
                            mock_paybc_response)

        foi_req = client.post(f'/api/foirawrequests', data=json.dumps({'requestData': {}}),
                              content_type='application/json')
        request_id = foi_req.json.get('id')

        pay_response = client.post(f'/api/foirawrequests/{request_id}/payments', data=json.dumps({
            'fee_code': fee_code,
            'quantity': quantity
        }), content_type='application/json')
        pay_id = pay_response.json.get('payment_id')
        txn_number = f"{app.config.get('PAYBC_TXN_PREFIX')}{pay_id:0>8}"
        response_url = f'trnApproved=1&messageText=Approved&trnOrderId=20595&trnAmount=50.00&paymentMethod=CC&' \
                       f'cardType=VI&authCode=TEST&trnDate=2021-10-18&pbcTxnNumber={txn_number}'
        response_url = f'{response_url}&hashValue={HashService.encode(response_url)}'
        # Update payment
        pay_response = client.put(f'/api/foirawrequests/{request_id}/payments/{pay_id}', data=json.dumps({
            'response_url': response_url
        }), content_type='application/json')
        assert pay_response.json.get('status') == 'PAID'
