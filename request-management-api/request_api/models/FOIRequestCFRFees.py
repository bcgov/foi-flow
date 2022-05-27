from flask.app import Flask
from sqlalchemy.sql.schema import ForeignKey
from .db import  db, ma
from datetime import datetime as datetime2
from sqlalchemy.orm import relationship,backref
from .default_method_result import DefaultMethodResult
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.sql.expression import distinct
from sqlalchemy import text
import logging

class FOIRequestCFRFee(db.Model):
    # Name of the table in our database
    __tablename__ = 'FOIRequestCFRFees' 
    # Defining the columns
    cfrfeeid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    ministryrequestid =db.Column(db.Integer, db.ForeignKey('FOIMinistryRequests.foiministryrequestid'))
    ministryrequestversion=db.Column(db.Integer, db.ForeignKey('FOIMinistryRequests.version'))
    version =db.Column(db.Integer,autoincrement=True)
    amountpaid = db.Column(db.Float, nullable=True)
    amountdue = db.Column(db.Float, nullable=True)  
    overallsuggestions = db.Column(db.Text, unique=False, nullable=True)
    status = db.Column(db.String(120), unique=False, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime2.now)
    createdby = db.Column(db.String(120), unique=False, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)

    
    @classmethod
    def createcfrfee(cls, foirequestcfrfee,_createddate,userid)->DefaultMethodResult:        
        newcfrfee = FOIRequestCFRFee(cfrfeeid=foirequestcfrfee["cfrfeeid"], 
        ministryrequestid=foirequestcfrfee["ministryrequestid"], 
        ministryrequestversion=foirequestcfrfee["ministryrequestversion"], 
        version=foirequestcfrfee["version"], 
        amountpaid=foirequestcfrfee["amountpaid"],
        amountdue=foirequestcfrfee["amountdue"],
        overallsuggestions=foirequestcfrfee["overallsuggestions"],
        created_at=_createddate, 
        createdby=userid)
        db.session.add(newcfrfee)
        db.session.commit()               
        return DefaultMethodResult(True,'CFR Fee Form added',newcfrfee.cfrfeeid)  

   
    @classmethod
    def deletecfrfee(cls, cfrfeeid, userid):
        db.session.query(FOIRequestCFRFee).filter(FOIRequestCFRFee.cfrfeeid == cfrfeeid).update({"isactive": False, "updated_at": datetime2.now(),"updatedby": userid}, synchronize_session=False)
        db.session.commit()
        return DefaultMethodResult(True,'Extensions disabled for the ministry',cfrfeeid) 
        
    @classmethod
    def updatecfrfee(cls, userid, foirequestcfrfee):   
        dbquery = db.session.query(FOIRequestCFRFee)
        cfrfee = dbquery.filter_by(cfrfeeid=foirequestcfrfee["cfrfeeid"])
        if(cfrfee.count() > 0) :             
            cfrfee.update({FOIRequestCFRFee.isactive:True, FOIRequestCFRFee.amountpaid:foirequestcfrfee["amountpaid"], 
            FOIRequestCFRFee.amountdue:foirequestcfrfee["amountdue"], 
            FOIRequestCFRFee.overallsuggestions:foirequestcfrfee["overallsuggestions"], 
            FOIRequestCFRFee.updatedby:userid, 
            FOIRequestCFRFee.status:foirequestcfrfee["status"],
            FOIRequestCFRFee.updated_at:datetime2.now()}, synchronize_session = False)
            db.session.commit()
            return DefaultMethodResult(True,'CFR Fee updated',foirequestcfrfee["cfrfeeid"])
        else:
            return DefaultMethodResult(True,'No CFR Fee found',foirequestcfrfee["cfrfeeid"])
            
    @classmethod
    def getcfrfee(cls, ministryrequestid)->DefaultMethodResult:   
        comment_schema = FOIRequestCommentSchema(many=True)
        query = db.session.query(FOIRequestCFRFee).filter_by(ministryrequestid=ministryrequestid, isactive = True).order_by(FOIRequestCFRFee.cfrfeeid.desc()).all()
        return comment_schema.dump(query)   

    @classmethod
    def getcfrfeebyid(cls, cfrfeeid) -> DefaultMethodResult:
        comment_schema = FOIRequestCommentSchema()
        query = db.session.query(FOIRequestCFRFee).filter_by(cfrfeeid=cfrfeeid, isactive=True).first()
        return comment_schema.dump(query)
       
class FOIRequestCommentSchema(ma.Schema):
    class Meta:
        fields = ('cfrfeeid', 'ministryrequestid', 'amountpaid','amountdue', 'overallsuggestions', 'created_at','createdby','updated_at','updatedby') 
