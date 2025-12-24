from flask import g, request
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
EXCEPTION_MESSAGE_NOTFOUND_REQUEST='Record not found'
CUSTOM_KEYERROR_MESSAGE = "Key error has occured: "

@cors_preflight('GET,OPTIONS')
@API.route('/foirequestinvoice/foicfrfee/<int:foicfrfeeid>', defaults={'usertype':None})
@API.route('/foirequestinvoice/foicfrfee/<int:foicfrfeeid>/<string:usertype>')
class FOIRequestInvoiceById(Resource):
    """Return foirequest invoice based on foicfrfeeid"""
    @staticmethod
    @cross_origin(origins=allowedorigins())
    @TRACER.trace()
    @auth.require
    @auth.ismemberofgroups(",".join(IAOTeamWithKeycloackGroup.list()))
    def get(foicfrfeeid):
        try:
            result = foiinvoiceservice().get_invoice(foicfrfeeid)
            if result.success:
                return {"invoice": result.documentpath, "status": 200}, 200
        except:
            return {"message": "Unable to find invoice with given CFR Fee ID", "status": 404}, 404
        
@cors_preflight('POST, PUT, OPTIONS') 
@API.route('/foirequestinvoice/foicfrfee/<int:foicfrfeeid>', defaults={'usertype':None})
@API.route('/foirequestinvoice/foicfrfee/<int:foicfrfeeid>/<string:usertype>')
class FOIRequestInvoice(Resource):
    """Creates (updates) a new version of foirequest invoice"""
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @auth.ismemberofgroups(",".join(IAOTeamWithKeycloackGroup.list()))
    def post(foicfrfeeid):
        try:
            data = request.get_json() #Passes created by, documentpath, cfrfeedata (has cfr feeid and foiministryreuestid), applicant_name, applicant address
            new_invoice =  FOIRequestInvoiceSchema().load(data),
            cfrdata = data["cfrfee"]
            result = foiinvoiceservice().generate_invoice(new_invoice, cfrdata)
            if result.success:
                return {"message": result.message, "invoice": result.identifier.documentpath, "status": 201}, 201
        except:
            return {"message":"Invoice creation failed", "status": 400}, 400

