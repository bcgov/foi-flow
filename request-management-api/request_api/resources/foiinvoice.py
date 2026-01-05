from flask import g, request, current_app
from flask_restx import Namespace, Resource
from flask_cors import cross_origin
from request_api.auth import auth, AuthHelper
from request_api.services.eventservice import eventservice
from request_api.services.foiinvoiceservice import foiinvoiceservice
from request_api.tracer import Tracer
from request_api.utils.util import  cors_preflight, allowedorigins, getrequiredmemberships
from request_api.exceptions import BusinessException
from request_api.utils.enums import IAOTeamWithKeycloackGroup
from request_api.schemas.foiinvoice import FOIRequestInvoiceSchema
from marshmallow import Schema, fields, validate, ValidationError
import json

API = Namespace('FOIREQUESTINVOICE', description='Endpoints for FOI Request Invoice management')
TRACER = Tracer.get_instance()
        
@cors_preflight('POST, PUT, OPTIONS') 
@API.route('/foirequestinvoice/foicfrfee/<int:foicfrfeeid>')
class FOIRequestInvoice(Resource):
    """Creates a new foirequest invoice"""
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @auth.ismemberofgroups(",".join(IAOTeamWithKeycloackGroup.list()))
    def post(foicfrfeeid):
        try:
            data = request.get_json()
            new_invoice =  FOIRequestInvoiceSchema().load(data)
            result = foiinvoiceservice().generate_invoice(new_invoice, AuthHelper.getuserid())
            if result.success:
                return {"message": result.message, "invoice": result.identifier, "status": 201}, 201
        except Exception:
            current_app.logger.exception(f"Invoice creation failed")
            return {"message":"Invoice creation failed", "status": 400}, 400
