import json

import pytest

from request_api.services.hash_service import HashService


@pytest.mark.parametrize('fee_code, expected_status_code', [('FOI0001', 200), ('TEST', 404)])
def test_get_fee(app, client, fee_code, expected_status_code):
    response = client.get(f'/api/fees/{fee_code}', content_type='application/json')
    assert response.status_code == expected_status_code

with open('tests/samplerequestjson/rawrequest.json') as x:
  rawrequestjson = json.load(x)
def test_create_payment(app, client):
    foi_req = client.post(f'/api/foirawrequests', data=json.dumps(rawrequestjson), content_type='application/json')
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

with open('tests/samplerequestjson/rawrequest.json') as x:
  rawrequestjson = json.load(x)
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

        monkeypatch.setattr('request_api.services.fee_service.FeeService.get_paybc_transaction_details',
                            mock_paybc_response)

        foi_req = client.post(f'/api/foirawrequests', data=json.dumps(rawrequestjson),
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

class TestResponse:
    def __init__(self, status_code, content = None, headers = {}):
        self.status_code = status_code
        self.content = content
        self.headers = headers

with open('tests/samplerequestjson/rawrequest.json') as x:
  rawrequestjson = json.load(x)        
def test_generate_receipt(app, client, monkeypatch):
    with app.app_context():
        
        foi_req = client.post(f'/api/foirawrequests', data=json.dumps(rawrequestjson), content_type='application/json')
        
        request_id = foi_req.json.get('id')
        fee_code = 'FOI0001'
        pay_response = client.post(f'/api/foirawrequests/{request_id}/payments', data=json.dumps({
            'fee_code': fee_code,
            'quantity': 5
        }), content_type='application/json')
        payment_id = pay_response.json.get('payment_id')        
        
        def moch_check_paid(self):
            return True

        monkeypatch.setattr('request_api.services.fee_service.FeeService.check_if_paid',
                            moch_check_paid)
        
        def mock_get_token(self):
            return 'token'
        
        monkeypatch.setattr('request_api.services.cdogs_api_service.CdogsApiService._get_access_token',
                            mock_get_token)
        
        def mock_check_hashed(self, template_hash_code):
            return False
         
        monkeypatch.setattr('request_api.services.cdogs_api_service.CdogsApiService.check_template_cached',
                            mock_check_hashed)
        
        def mock_upload_template(self,  headers, url, template):
            return TestResponse(
                status_code= 200,
                headers= {'X-Template-Hash': "58G94G"}
            );
            
        monkeypatch.setattr('request_api.services.cdogs_api_service.CdogsApiService._post_upload_template',
                            mock_upload_template)
        
        def mock_generate_receipt(self, json_request_body, headers, ur):
            return TestResponse(
                content= bytearray([2, 3, 5, 7]),
                status_code= 200,
            );
            
        monkeypatch.setattr('request_api.services.cdogs_api_service.CdogsApiService._post_generate_receipt',
                            mock_generate_receipt)
        receipt_response = client.post(f'/api/foirawrequests/{request_id}/payments/{payment_id}/receipt', data=json.dumps({
            'requestData': {}
        }), content_type='application/json')
        assert receipt_response.status_code == 200