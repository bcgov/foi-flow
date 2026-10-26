"""Exercise the real receipt endpoint and its storage boundary with synthetic data."""

from io import BytesIO
import json
import re

from pypdf import PdfReader
import pytest
import requests

from request_api.models.FOIRawRequests import FOIRawRequest
from request_api.models.FOIRawRequestDocuments import FOIRawRequestDocument
from request_api.models.DocumentPathMapper import DocumentPathMapper
from request_api.services.cdogs_api_service import CdogsApiService


def create_request(session):
    mapper = session.query(DocumentPathMapper).filter_by(category='Attachments', isactive=True).one()
    mapper.attributes = '{}'
    session.flush()
    result = FOIRawRequest.saverawrequest(
        {'requestType': 'general'}, 'online', False, 'upgrade-intake', None,
        False, None, None, [],
    )
    assert result.success
    return result.identifier


def test_receipt_endpoint_renders_and_uploads_identical_pdf_bytes(session, client, external_http):
    requestid = create_request(session)
    uploads = {}

    def put_object(request, context):
        if request.body:
            uploads[request.url] = request.body
        return b''

    external_http.put(re.compile(r'^https://storage:8333/'), content=put_object)
    response = client.post('/api/foirawrequest/requestreceipt', json={
        'requestId': requestid,
        'requestHTML': '<style>@page { size: A4; } body {font-family: "DejaVu Sans";}</style><h1>Synthetic FOI receipt</h1>',
    })
    assert response.status_code == 200, response.data
    assert response.mimetype == 'application/pdf'
    assert response.data.startswith(b'%PDF-')
    pdf = PdfReader(BytesIO(response.data))
    assert len(pdf.pages) == 1
    assert 'Synthetic FOI receipt' in pdf.pages[0].extract_text()
    assert float(pdf.pages[0].mediabox.width) == pytest.approx(595.28, abs=1)
    assert float(pdf.pages[0].mediabox.height) == pytest.approx(841.89, abs=1)
    assert len(uploads) == 1
    key, content = next(iter(uploads.items()))
    assert f'/Misc/{requestid}/applicant/' in key
    assert key.endswith('.pdf')
    assert content == response.data
    assert session.query(FOIRawRequestDocument).filter_by(foirequest_id=requestid).count() == 1


def test_receipt_storage_failure_does_not_persist_document(session, client, external_http):
    requestid = create_request(session)
    external_http.put(re.compile(r'^https://storage:8333/'), exc=requests.ConnectionError('synthetic outage'))
    with pytest.raises(requests.ConnectionError):
        client.post('/api/foirawrequest/requestreceipt', json={
            'requestId': requestid, 'requestHTML': '<h1>Synthetic FOI receipt</h1>',
        })
    assert session.query(FOIRawRequestDocument).filter_by(foirequest_id=requestid).count() == 0


def test_cdogs_receipt_request_and_returned_bytes(app, external_http):
    def token(request, context):
        assert request.text == 'grant_type=client_credentials'
        assert request.headers['Authorization'] == 'Basic dGVzdDp0ZXN0'
        return {'access_token': 'synthetic-cdogs-token'}

    def render(request, context):
        assert request.headers['Authorization'] == 'Bearer synthetic-cdogs-token'
        assert json.loads(request.text) == {
            'options': {'cachereport': False, 'convertTo': 'pdf', 'overwrite': True, 'reportName': 'Receipt'},
            'data': {'receiptNumber': 'UPGRADE-001'},
        }
        return b'%PDF-synthetic-cdogs-output'

    external_http.post('http://cdogs:8080/token', json=token)
    external_http.post('http://cdogs:8080/api/v2/template/synthetic-template/render', content=render)
    saved = {key: app.config.get(key) for key in ('CDOGS_BASE_URL', 'CDOGS_TOKEN_URL', 'CDOGS_SERVICE_CLIENT', 'CDOGS_SERVICE_CLIENT_SECRET')}
    app.config.update(CDOGS_BASE_URL='http://cdogs:8080', CDOGS_TOKEN_URL='http://cdogs:8080/token',
                      CDOGS_SERVICE_CLIENT='test', CDOGS_SERVICE_CLIENT_SECRET='test')
    try:
        with app.app_context():
            response = CdogsApiService().generate_receipt('synthetic-template', {'receiptNumber': 'UPGRADE-001'})
        assert response.status_code == 200
        assert response.content == b'%PDF-synthetic-cdogs-output'
    finally:
        app.config.update(saved)
