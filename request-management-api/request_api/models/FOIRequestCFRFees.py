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
        query = db.session.query(FOIRequestCFRFee).filter_by(ministryrequestid=ministryrequestid).order_by(FOIRequestCFRFee.version.desc()).first()
        return comment_schema.dump(query)   
    
    @classmethod
    def getcfrfeehistory(cls, ministryrequestid)->DefaultMethodResult:   
        comment_schema = FOIRequestCFRFormSchema(many=False)
        subquery1 = db.session.query(FOIRequestCFRFee.cfrfeeid, db.func.max(FOIRequestCFRFee.version).label('version')).group_by(FOIRequestCFRFee.cfrfeeid).subquery()
        subquery2 = db.session.query(FOIRequestCFRFee.cfrfeeid, FOIRequestCFRFee.created_at.label('version_created_at'), FOIRequestCFRFee.createdby.label('version_createdby')).filter_by(version=1).subquery()
        query = db.session.query(FOIRequestCFRFee, subquery2.c.version_created_at, subquery2.c.version_createdby).filter_by(ministryrequestid=ministryrequestid).join(
            subquery1, (FOIRequestCFRFee.cfrfeeid == subquery1.c.cfrfeeid) & (FOIRequestCFRFee.version == subquery1.c.version)
        ).join(subquery2, (FOIRequestCFRFee.cfrfeeid == subquery2.c.cfrfeeid)).order_by(FOIRequestCFRFee.cfrfeeid.desc()).all()
        history = []
        for row in query:
            print(row)
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
    def getstatenavigation(cls, ministryrequestid):
        _session = db.session
        _entries = _session.query(FOIRequestCFRFee).filter(FOIRequestCFRFee.ministryrequestid == ministryrequestid and FOIRequestCFRFee.cfrfeestatusid is not null).order_by(FOIRequestCFRFee.version.desc()).limit(2)
        requeststates = []
        for _entry in _entries:
            requeststates.append(_entry.cfrfeestatus.description)
        return requeststates  
       
class FOIRequestCFRFormSchema(ma.Schema):
    class Meta:
        fields = ('cfrfeeid', 'ministryrequestid', 'feedata', 'overallsuggestions', 'created_at','createdby','updated_at','updatedby','cfrfeestatusid', 'cfrfeestatus.name','cfrfeestatus.description','version') 


