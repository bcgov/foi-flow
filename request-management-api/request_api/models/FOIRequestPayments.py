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
import maya
import os
from dateutil.parser import parse
from pytz import timezone
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
 
    @classmethod
    def getactivepayment(cls, foirequestid, ministryrequestid) -> DefaultMethodResult:
        now_pst = maya.parse(maya.now()).datetime(to_timezone='America/Vancouver', naive=False)
        _psttoday = now_pst.strftime('%Y-%m-%d') 
        try:
            """
            sql = select distinct on (paymentid) paymentid, paymenturl from "FOIRequestPayments" fp where foirequestid = :foirequestid and ministryrequestid  = :ministryrequestid  
                                and TO_DATE(paymentexpirydate::TEXT,'YYYY-MM-DD') >=  TO_DATE(:today,'YYYY-MM-DD') 
                                order by paymentid, version desc
            """
            sql =   """select fp1.paymentid , fp1.paymenturl, fp1.version from "FOIRequestPayments" fp1, (
                                select distinct on (paymentid) paymentid, paymenturl, createdby, version  from "FOIRequestPayments" fp where foirequestid = :foirequestid and ministryrequestid  = :ministryrequestid  
                                order by paymentid, version desc) as fp2 
                                where fp1.paymentid = fp2.paymentid and fp1.version = fp2.version
                                and fp1.createdby <> 'System_Cancel'
                    """
            
            rs = db.session.execute(text(sql), {'foirequestid': foirequestid, 'ministryrequestid' : ministryrequestid, 'today' : _psttoday})
            for row in rs:
                return ({"paymentid": row["paymentid"], "paymenturl": row["paymenturl"]})
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return None        
        
      
class FOIRequestPaymentSchema(ma.Schema):
    class Meta:
        fields = ('paymentid', 'version', 'foirequestid', 'ministryrequestid', 'paymenturl','created_at','createdby','updated_at','updatedby', 'paymentexpirydate', 'paidamount') 