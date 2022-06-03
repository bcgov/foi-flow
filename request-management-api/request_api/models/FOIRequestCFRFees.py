from flask.app import Flask
from sqlalchemy.sql.schema import ForeignKey
from .db import  db, ma
from datetime import datetime as datetime2
from sqlalchemy.orm import relationship,backref
from .default_method_result import DefaultMethodResult
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.sql.expression import distinct
from sqlalchemy import text, insert
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
        comment_schema = FOIRequestCommentSchema(many=False)
        query = db.session.query(FOIRequestCFRFee).filter_by(ministryrequestid=ministryrequestid).order_by(FOIRequestCFRFee.version.desc()).first()
        return comment_schema.dump(query)   
    
    @classmethod
    def getcfrfeehistory(cls, ministryrequestid)->DefaultMethodResult:   
        comment_schema = FOIRequestCommentSchema(many=True)
        query = db.session.query(FOIRequestCFRFee).filter_by(ministryrequestid=ministryrequestid).order_by(FOIRequestCFRFee.version.desc()).all()
        return comment_schema.dump(query) 

    @classmethod
    def getcfrfeebyid(cls, cfrfeeid) -> DefaultMethodResult:
        comment_schema = FOIRequestCommentSchema()
        query = db.session.query(FOIRequestCFRFee).filter_by(cfrfeeid=cfrfeeid, isactive=True).first()
        return comment_schema.dump(query)
       
class FOIRequestCommentSchema(ma.Schema):
    class Meta:
        fields = ('cfrfeeid', 'ministryrequestid', 'feedata', 'overallsuggestions', 'created_at','createdby','updated_at','updatedby','cfrfeestatusid', 'cfrfeestatus.name','version') 