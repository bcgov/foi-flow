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
from sqlalchemy import func

class CFRFeeStatus(db.Model):
    __tablename__ = 'CFRFeeStatuses' 
    # Defining the columns
    cfrfeestatusid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(25), unique=False, nullable=False)
    description = db.Column(db.String(100), unique=False, nullable=False)    
    isactive = db.Column(db.Boolean, unique=False, nullable=False)    
    
    @classmethod
    def getallcfrfeestatuses(cls):
        cfrfeestatus_schema = CFRFeeStatusSchema(many=True)
        query = db.session.query(CFRFeeStatus).filter_by(isactive=True).order_by(CFRFeeStatus.cfrfeestatusid.asc()).all()
        return cfrfeestatus_schema.dump(query)

    @classmethod
    def getcfrfeestatus(cls,cfrfeestatusid):
        cfrfeestatus_schema = CFRFeeStatusSchema(many=False)
        query = db.session.query(CFRFeeStatus).filter_by(cfrfeestatusid=cfrfeestatusid).first()
        return cfrfeestatus_schema.dump(query)
    
    @classmethod
    def getcfrfeestatusid(cls,cfrfeestatus):
        cfrfeestatus_schema = CFRFeeStatusSchema(many=False)
        query = db.session.query(CFRFeeStatus).filter(func.lower(CFRFeeStatus.name) == func.lower(cfrfeestatus)).first()
        return cfrfeestatus_schema.dump(query)
    
class CFRFeeStatusSchema(ma.Schema):
    class Meta:
        fields = ('cfrfeestatusid','name','description','isactive')