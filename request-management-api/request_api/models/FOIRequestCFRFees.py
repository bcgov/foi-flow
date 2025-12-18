from flask.app import Flask
from sqlalchemy.sql.schema import ForeignKey
from .db import  db, ma
from marshmallow import pre_dump, post_dump
from datetime import datetime as datetime2
from sqlalchemy.orm import relationship,backref
from .default_method_result import DefaultMethodResult
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.sql.expression import distinct
from sqlalchemy import null, text, insert
from .CFRFeeStatus import CFRFeeStatus
import logging

class FOIRequestCFRFee(db.Model):
    # Name of the table in our database
    __tablename__ = 'FOIRequestCFRFees' 
    # Defining the columns
    cfrfeeid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    ministryrequestid =db.Column(db.Integer, db.ForeignKey('FOIMinistryRequests.foiministryrequestid'))
    ministryrequestversion=db.Column(db.Integer, db.ForeignKey('FOIMinistryRequests.version'))
    version =db.Column(db.Integer,primary_key=True,nullable=False)
    feedata = db.Column(JSON, unique=False, nullable=True)
    overallsuggestions = db.Column(db.Text, unique=False, nullable=True)
    cfrfeestatusid =db.Column(db.Integer, db.ForeignKey('CFRFeeStatuses.cfrfeestatusid'))
    cfrfeestatus = relationship("CFRFeeStatus",backref=backref("CFRFeeStatus"),uselist=False)
    created_at = db.Column(db.DateTime, default=datetime2.now)
    createdby = db.Column(db.String(120), unique=False, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)
    cfrformreasonid =db.Column(db.Integer, db.ForeignKey('CFRFormReasons.cfrformreasonid'), nullable=True)
    cfrformreason = relationship("CFRFormReason",backref=backref("CFRFormReason"),uselist=False)

    
    @classmethod    
    def createcfrfee(cls, cfrfee, userid)->DefaultMethodResult:   
        cfrfee.created_at=datetime2.now().isoformat(), 
        cfrfee.createdby=userid 
        db.session.add(cfrfee)
        db.session.commit()               
        return DefaultMethodResult(True,'CFR Fee added for ministry request : '+ str(cfrfee.ministryrequestid), cfrfee.cfrfeeid)  


    @classmethod
    def getcfrfee(cls, ministryrequestid)->DefaultMethodResult:   
        comment_schema = FOIRequestCFRFormSchema(many=False)
        query = db.session.query(FOIRequestCFRFee).filter_by(ministryrequestid=ministryrequestid).order_by(FOIRequestCFRFee.cfrfeeid.desc(), FOIRequestCFRFee.version.desc()).first()
        return comment_schema.dump(query)   

    @classmethod
    def getapprovedcfrfee(cls, ministryrequestid)->DefaultMethodResult:   
        comment_schema = FOIRequestCFRFormSchema(many=False)
        query = db.session.query(FOIRequestCFRFee).filter_by(ministryrequestid=ministryrequestid, cfrfeestatusid=2).order_by(FOIRequestCFRFee.cfrfeeid.desc(), FOIRequestCFRFee.version.desc()).first()
        return comment_schema.dump(query)  
    
    @classmethod
    def getcfrfeehistory(cls, ministryrequestid)->DefaultMethodResult:   
        comment_schema = FOIRequestCFRFormSchema(many=False)
        subquery1 = db.session.query(FOIRequestCFRFee.cfrfeeid, db.func.max(FOIRequestCFRFee.version).label('version')).group_by(FOIRequestCFRFee.cfrfeeid).subquery()
        subquery2 = db.session.query(FOIRequestCFRFee.cfrfeeid, FOIRequestCFRFee.created_at.label('version_created_at'), FOIRequestCFRFee.createdby.label('version_createdby')).filter_by(version=1).subquery()
        query = db.session.query(FOIRequestCFRFee, subquery2.c.version_created_at, subquery2.c.version_createdby).filter_by(
            ministryrequestid=ministryrequestid, cfrfeestatusid=2).join(
            subquery1, (FOIRequestCFRFee.cfrfeeid == subquery1.c.cfrfeeid) & (FOIRequestCFRFee.version == subquery1.c.version)
        ).join(subquery2, (FOIRequestCFRFee.cfrfeeid == subquery2.c.cfrfeeid)).order_by(FOIRequestCFRFee.cfrfeeid.desc()).all()
        history = []
        for row in query:
            cfrfee = comment_schema.dump(row[0])
            cfrfee['version_created_at'] = row[1]
            cfrfee['version_createdby'] = row[2]
            history.append(cfrfee)
        return history

    @classmethod
    def getcfrfeebyid(cls, cfrfeeid) -> DefaultMethodResult:
        comment_schema = FOIRequestCFRFormSchema()
        query = db.session.query(FOIRequestCFRFee).filter_by(cfrfeeid=cfrfeeid, isactive=True).first()
        return comment_schema.dump(query)
    
    @classmethod
    def getstatenavigation(cls, ministryrequestid, cfrfeeid):
        _session = db.session
        _entries = _session.query(FOIRequestCFRFee).filter_by(ministryrequestid = ministryrequestid, cfrfeeid = cfrfeeid).order_by(FOIRequestCFRFee.version.desc()).limit(2)
        requeststates = []
        for _entry in _entries:
            if _entry.cfrfeestatusid: 
                requeststates.append(_entry.cfrfeestatus.description)
        return requeststates

    @classmethod
    def getfeedataforamountcomparison(cls, ministryrequestid):
        _session = db.session
        _entries = _session.query(FOIRequestCFRFee).filter(FOIRequestCFRFee.ministryrequestid == ministryrequestid and FOIRequestCFRFee.feedata is not null).order_by(FOIRequestCFRFee.cfrfeeid.desc(), FOIRequestCFRFee.version.desc()).limit(2)
        feedata = []
        for _entry in _entries:
            feedata.append(_entry.feedata)
        return feedata  

    @classmethod
    def updatecfrfeedatabyid(cls, ministryrequestid, feedata)->DefaultMethodResult:
        sq = db.session.query(FOIRequestCFRFee.cfrfeeid, FOIRequestCFRFee.version).filter_by(ministryrequestid=ministryrequestid).order_by(FOIRequestCFRFee.cfrfeeid.desc(), FOIRequestCFRFee.version.desc()).limit(1).subquery()
        cfrfee = db.session.query(FOIRequestCFRFee).filter_by(cfrfeeid=sq.c.cfrfeeid, version=sq.c.version)
        cfrfee.update({FOIRequestCFRFee.feedata: feedata, FOIRequestCFRFee.updatedby: 'Online Payment',
                        FOIRequestCFRFee.updated_at: datetime2.now().isoformat()}, synchronize_session=False)
        db.session.commit()
        return DefaultMethodResult(True,'CFR Fee Data updated for ministry request : '+ str(ministryrequestid), sq.c.cfrfeeid)
       
class FOIRequestCFRFormSchema(ma.Schema):
    class Meta:
        fields = ('cfrfeeid', 'ministryrequestid', 'feedata', 'overallsuggestions', 'created_at','createdby','updated_at','updatedby','cfrfeestatusid', 'cfrfeestatus.name','cfrfeestatus.description','version','cfrformreasonid','cfrformreason.name','cfrformreason.description') 


