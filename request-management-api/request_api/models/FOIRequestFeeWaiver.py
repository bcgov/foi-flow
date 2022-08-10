from flask.app import Flask
from sqlalchemy.sql.schema import ForeignKey
from .db import  db, ma
from datetime import datetime as datetime2
from sqlalchemy.orm import relationship,backref
from .default_method_result import DefaultMethodResult
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.sql.expression import distinct
from sqlalchemy import null, text, insert
import logging

class FOIRequestFeeWaiver(db.Model):
    # Name of the table in our database
    __tablename__ = 'FOIRequestFeeWaiver'
    # Defining the columns
    feewaiverid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    ministryrequestid =db.Column(db.Integer, db.ForeignKey('FOIMinistryRequests.foiministryrequestid'))
    ministryrequestversion=db.Column(db.Integer, db.ForeignKey('FOIMinistryRequests.version'))
    version =db.Column(db.Integer,primary_key=True,nullable=False)
    formdata = db.Column(JSON, unique=False, nullable=True)
    waiverstatusid =db.Column(db.Integer, db.ForeignKey('FeeWaiverStatuses.waiverstatusid'))
    waiverstatus = relationship("FeeWaiverStatus",backref=backref("FeeWaiverStatus"),uselist=False)
    created_at = db.Column(db.DateTime, default=datetime2.now)
    createdby = db.Column(db.String(120), unique=False, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)


    @classmethod
    def createfeewaiver(cls, feewaiver, userid)->DefaultMethodResult:
        feewaiver.created_at=datetime2.now().isoformat(),
        feewaiver.createdby=userid
        db.session.add(feewaiver)
        db.session.commit()
        return DefaultMethodResult(True,'CFR Fee added for ministry request : '+ str(feewaiver.ministryrequestid), feewaiver.feewaiverid)


    @classmethod
    def getfeewaiver(cls, ministryrequestid)->DefaultMethodResult:
        comment_schema = FOIRequestFeeWaiverSchema(many=False)
        query = db.session.query(FOIRequestFeeWaiver).filter_by(ministryrequestid=ministryrequestid).order_by(FOIRequestFeeWaiver.version.desc()).first()
        return comment_schema.dump(query)

    @classmethod
    def getfeewaiverhistory(cls, ministryrequestid)->DefaultMethodResult:
        comment_schema = FOIRequestFeeWaiverSchema(many=True)
        query = db.session.query(FOIRequestFeeWaiver).filter_by(ministryrequestid=ministryrequestid).order_by(FOIRequestFeeWaiver.version.desc()).all()
        return comment_schema.dump(query)

    @classmethod
    def getfeewaiverbyid(cls, feewaiverid) -> DefaultMethodResult:
        comment_schema = FOIRequestFeeWaiverSchema()
        query = db.session.query(FOIRequestFeeWaiver).filter_by(feewaiverid=feewaiverid, isactive=True).first()
        return comment_schema.dump(query)

    @classmethod
    def getstatenavigation(cls, ministryrequestid):
        _session = db.session
        _entries = _session.query(FOIRequestFeeWaiver).filter(FOIRequestFeeWaiver.ministryrequestid == ministryrequestid and FOIRequestFeeWaiver.waiverstatusid is not null).order_by(FOIRequestFeeWaiver.version.desc()).limit(2)
        requeststates = []
        for _entry in _entries:
            requeststates.append(_entry.waiverstatus.description)
        return requeststates

class FOIRequestFeeWaiverSchema(ma.Schema):
    class Meta:
        fields = ('feewaiverid', 'ministryrequestid', 'formdata', 'created_at','createdby','updated_at','updatedby','waiverstatusid', 'waiverstatus.name','waiverstatus.description','version')
