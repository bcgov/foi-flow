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
    version =db.Column(db.Integer,primary_key=True,nullable=False,autoincrement=True)
    feedata = db.Column(JSON, unique=False, nullable=True)
    overallsuggestions = db.Column(db.Text, unique=False, nullable=True)
    status = db.Column(db.String(120), unique=False, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime2.now)
    createdby = db.Column(db.String(120), unique=False, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)

    
    @classmethod
    def createcfrfee(cls, foirequestcfrfee,ministryrequestversion,userid,createddate=None)->DefaultMethodResult:    
        _createddate = datetime2.now().isoformat() if createddate is None else createddate      
        newcfrfee = FOIRequestCFRFee(cfrfeeid=foirequestcfrfee["cfrfeeid"], 
        ministryrequestid=foirequestcfrfee["ministryrequestid"], 
        ministryrequestversion=ministryrequestversion, 
        version='1', 
        feedata= foirequestcfrfee["feedata"],
        overallsuggestions=foirequestcfrfee["overallsuggestions"],
        created_at=_createddate, 
        createdby=userid)
        db.session.add(newcfrfee)
        db.session.commit()               
        return DefaultMethodResult(True,'CFR Fee Form added',newcfrfee.cfrfeeid)  

        
    @classmethod
    def updatecfrfee(cls, foirequestcfrfee,userid):   
        dbquery = db.session.query(FOIRequestCFRFee)
        cfrfee = dbquery.filter_by(cfrfeeid=foirequestcfrfee["cfrfeeid"]).order_by(FOIRequestCFRFee.version.desc()).first()
        if cfrfee is not None: 
            status = foirequestcfrfee["status"] if 'status' in foirequestcfrfee  else None         
            _version = cfrfee.version+1, 
            _ministryrequestid= cfrfee.ministryrequestid, 
            _ministryrequestversion= cfrfee.ministryrequestversion          
            insertstmt =(
                insert(FOIRequestCFRFee).
                values(
                    cfrfeeid=foirequestcfrfee["cfrfeeid"],
                    feedata=foirequestcfrfee["feedata"], 
                    overallsuggestions=foirequestcfrfee["overallsuggestions"],
                    updated_at=datetime2.now(),
                    updatedby=userid,
                    status=status,
                    ministryrequestid= _ministryrequestid, 
                    ministryrequestversion= _ministryrequestversion,
                    version=_version
                    )
            ) 
            db.session.execute(insertstmt)
            db.session.commit()
            return DefaultMethodResult(True,'CFR Fee updated',foirequestcfrfee["cfrfeeid"])
        else:
            return DefaultMethodResult(True,'No CFR Fee found',foirequestcfrfee["cfrfeeid"])
            
    @classmethod
    def getcfrfee(cls, ministryrequestid)->DefaultMethodResult:   
        comment_schema = FOIRequestCommentSchema(many=True)
        query = db.session.query(FOIRequestCFRFee).filter_by(ministryrequestid=ministryrequestid).order_by(FOIRequestCFRFee.cfrfeeid.desc()).all()
        return comment_schema.dump(query)   

    @classmethod
    def getcfrfeebyid(cls, cfrfeeid) -> DefaultMethodResult:
        comment_schema = FOIRequestCommentSchema()
        query = db.session.query(FOIRequestCFRFee).filter_by(cfrfeeid=cfrfeeid, isactive=True).first()
        return comment_schema.dump(query)
       
class FOIRequestCommentSchema(ma.Schema):
    class Meta:
        fields = ('cfrfeeid', 'ministryrequestid', 'feedata', 'overallsuggestions', 'created_at','createdby','updated_at','updatedby') 