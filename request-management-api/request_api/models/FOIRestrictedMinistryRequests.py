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


class FOIRestrictedMinistryRequest(db.Model):
    # Name of the table in our database
    __tablename__ = 'FOIRestrictedMinistryRequests' 
    # Defining the columns
    restrictionid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    ministryrequestid =db.Column(db.Integer, db.ForeignKey('FOIMinistryRequests.foiministryrequestid'))
    version =db.Column(db.Integer, db.ForeignKey('FOIMinistryRequests.version'))
    type = db.Column(db.String(50), unique=False, nullable=False) 
    isrestricted = db.Column(db.Boolean, unique=False, nullable=False)  
    isactive = db.Column(db.Boolean, unique=False, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    createdby = db.Column(db.String(120), unique=False, nullable=False)

    @classmethod
    def saverestrictedrequest(cls, foirestrictedrequest, ministryrequestid ,type,isrestricted,version, userid)->DefaultMethodResult:                
        restrictedrequest = FOIRestrictedMinistryRequest(ministryrequestid=ministryrequestid , version=version, type=type, isrestricted=isrestricted, isactive=True, createdby=userid)
        db.session.add(restrictedrequest)
        db.session.commit()               
        return DefaultMethodResult(True,'Restricted Request added')   

    @classmethod
    def disablerestrictedrequests(cls, ministryrequestid, type, userid):   
        dbquery = db.session.query(FOIRestrictedMinistryRequest)
        prevrestrictedrequestsbytype = dbquery.filter_by(ministryrequestid=ministryrequestid,type=type)
        if(prevrestrictedrequestsbytype.count() > 0) :             
            prevrestrictedrequestsbytype.update({FOIRestrictedMinistryRequest.isactive:False}, synchronize_session = False)
            db.session.commit()
            return DefaultMethodResult(True,'Restricted Requests disabled',ministryrequestid)
        else:
            return DefaultMethodResult(True,'No Restricted Requests found',ministryrequestid)

            
class FOIRestrictedMinistryRequestSchema(ma.Schema):
    class Meta:
        fields = ('restrictionid', 'ministryrequestid', 'version', 'type','isrestricted','isactive','created_at','createdby') 