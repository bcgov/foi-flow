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
from sqlalchemy.dialects.postgresql import JSON, insert

class FOIRequestOIPC(db.Model):
    # Name of the table in our database
    __tablename__ = 'FOIRequestOIPC' 
    # Defining the columns
    oipcid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    foiministryrequest_id =db.Column(db.Integer, db.ForeignKey('FOIMinistryRequests.foiministryrequestid'))
    foiministryrequestversion_id =db.Column(db.Integer, db.ForeignKey('FOIMinistryRequests.version'))
    oipcno = db.Column(db.String(120), unique=False, nullable=True)  
    reviewtypeid = db.Column(db.Integer,ForeignKey('OIPCReviewTypes.reviewtypeid'))
    reviewtype =  relationship("OIPCReviewTypes",backref=backref("OIPCReviewTypes"),uselist=False)
    reasonid = db.Column(db.Integer,ForeignKey('OIPCReasons.reasonid'))
    reason =  relationship("OIPCReasons",backref=backref("OIPCReasons"),uselist=False)
    statusid = db.Column(db.Integer,ForeignKey('OIPCStatuses.statusid'))
    status =  relationship("OIPCStatuses",backref=backref("OIPCStatuses"),uselist=False)
    outcomeid = db.Column(db.Integer,ForeignKey('OIPCOutcomes.outcomeid'))
    outcome =  relationship("OIPCOutcomes",backref=backref("OIPCOutcomes"),uselist=False)
    isinquiry = db.Column(db.Boolean, unique=False, nullable=True)
    inquiryattributes = db.Column(JSON, unique=False, nullable=True)
    isjudicialreview = db.Column(db.Boolean, unique=False, nullable=True)
    issubsequentappeal = db.Column(db.Boolean, unique=False, nullable=True)
    investigator = db.Column(db.String(500), unique=False, nullable=True) 
    receiveddate = db.Column(db.Date, nullable=True)
    closeddate = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    createdby = db.Column(db.String(120), unique=False, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=True)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)


    @classmethod
    def getoipc(cls,ministryrequestid,ministryrequestversion):
        oipc_schema = FOIRequestOIPCSchema(many=True)
        _oipclist = db.session.query(FOIRequestOIPC).filter(FOIRequestOIPC.foiministryrequest_id == ministryrequestid , FOIRequestOIPC.foiministryrequestversion_id == ministryrequestversion).order_by(FOIRequestOIPC.oipcid.asc()).all()
        divisioninfos = oipc_schema.dump(_oipclist)       
        return divisioninfos
    
            
class FOIRequestOIPCSchema(ma.Schema):
    class Meta:
        fields = ('oipcid', 'version', 'ministryrequestid', 'investigator','ministryversion','oipcno','reviewtypeid','reasonid','statusid','outcomeid','isinquiry','inquiryattributes','isjudicialreview',
                  'issubsequentappeal','isactive','receiveddate','closeddate','created_at','createdby','updated_at','updatedby',
                  'reviewtype.name', 'reason.name', 'status.name', 'outcome.name') 