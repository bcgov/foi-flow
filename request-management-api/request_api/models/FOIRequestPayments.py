from flask.app import Flask
from sqlalchemy.sql.schema import ForeignKey
from .db import  db, ma
from datetime import datetime
from sqlalchemy.orm import relationship,backref
from .default_method_result import DefaultMethodResult
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.sql.expression import distinct
from sqlalchemy import text, and_, func
import logging
import json
class FOIRequestPayment(db.Model):
    # Name of the table in our database
    __tablename__ = 'FOIRequestPayments' 
    # Defining the columns
    paymentid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    version =db.Column(db.Integer,primary_key=True,nullable=False)
    foirequestid =db.Column(db.Integer,  nullable=False)
    ministryrequestid =db.Column(db.Integer, db.ForeignKey('FOIMinistryRequests.foiministryrequestid'))
    ministryrequestversion=db.Column(db.Integer, db.ForeignKey('FOIMinistryRequests.version'))
    paymenturl = db.Column(db.Text, unique=False, nullable=True) 
    paymentexpirydate = db.Column(db.DateTime, nullable=True)
    paidamount = db.Column(db.Numeric(10,2), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    createdby = db.Column(db.String(120), unique=False, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)

    @classmethod
    def savepayment(cls, newpayment)->DefaultMethodResult:                
        db.session.add(newpayment)
        db.session.commit()               
        return DefaultMethodResult(True,'Payment added')   

    @classmethod
    def getpayment(cls, foirequestid, ministryrequestid)->DefaultMethodResult:                
        payment_schema = FOIRequestPaymentSchema()            
        payment = db.session.query(FOIRequestPayment).filter(FOIRequestPayment.foirequestid == foirequestid, FOIRequestPayment.ministryrequestid == ministryrequestid).order_by(FOIRequestPayment.paymentid.desc(), FOIRequestPayment.version.desc()).first()
        return payment_schema.dump(payment)
 

      
class FOIRequestPaymentSchema(ma.Schema):
    class Meta:
        fields = ('paymentid', 'version', 'foirequestid', 'ministryrequestid', 'paymenturl','created_at','createdby','updated_at','updatedby', 'paymentexpirydate', 'paidamount') 