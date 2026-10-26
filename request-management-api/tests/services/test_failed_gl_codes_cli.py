"""Run the existing reconciliation CLI logic without sending financial writes."""

from decimal import Decimal
import importlib
import json
from types import SimpleNamespace


def test_cli_posts_expected_revenue_payload(app, monkeypatch, external_http, capsys):
    cli = importlib.import_module('update_failed_gl_codes_cli')
    payment = SimpleNamespace(request_id=7, payment_id=8, fee_code_id=9, total=Decimal('10.50'))
    monkeypatch.setattr(cli.Payment, 'find_paid_transaction', lambda number: payment)
    fee = SimpleNamespace(code='FOI0001', revenue_account_id=10)
    monkeypatch.setattr(cli.FeeCode, 'find_by_id', lambda value: fee)
    monkeypatch.setattr(cli.FeeCode, 'get_fee', lambda **kwargs: fee)
    account = SimpleNamespace(client='001', responsibility_centre='002', service_line='003', stob='004', project_code='005')
    monkeypatch.setattr(cli.RevenueAccount, 'find_by_id', lambda value: account)

    class FeeService:
        def __init__(self, **kwargs):
            assert kwargs == {'request_id': 7, 'payment_id': 8}

        def get_paybc_transaction_details(self):
            return {'paymentstatus': 'PAID', 'revenue': [{'glstatus': 'RJCT'}]}

        def get_paybc_token(self):
            return SimpleNamespace(json=lambda: {'access_token': 'synthetic-paybc-token'})

    monkeypatch.setattr(cli, 'FeeService', FeeService)

    def post(request, context):
        assert request.headers['Authorization'] == 'Bearer synthetic-paybc-token'
        assert json.loads(request.text) == {'revenue': [{
            'lineNumber': '1', 'revenueAccount': '001.002.003.004.005.000000.0000', 'revenueAmount': '10.50',
        }]}
        return {'updated': True}

    external_http.post('http://paybc:8080/paybc/payment/test-ref/TXN-1', json=post)
    with app.app_context():
        saved = app.config.get('PAYBC_API_BASE_URL'), app.config.get('PAYBC_REF_NUMBER')
        app.config.update(PAYBC_API_BASE_URL='http://paybc:8080', PAYBC_REF_NUMBER='test-ref')
        try:
            cli.update_failed_gl_codes(['TXN-1'])
        finally:
            app.config.update(PAYBC_API_BASE_URL=saved[0], PAYBC_REF_NUMBER=saved[1])
    assert 'Successfully updated for transaction TXN-1' in capsys.readouterr().out
