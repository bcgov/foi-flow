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

class CFRFormReason(db.Model):
    __tablename__ = 'CFRFormReasons' 
    # Defining the columns
    cfrformreasonid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(25), unique=False, nullable=False)
    description = db.Column(db.String(100), unique=False, nullable=False)    
    isactive = db.Column(db.Boolean, unique=False, nullable=False)    
    
    @classmethod
    def getallcfrformreasons(cls):
        cfrformreason_schema = CFRFormReasonSchema(many=True)
        query = db.session.query(CFRFormReason).filter_by(isactive=True).order_by(CFRFormReason.cfrformreasonid.asc()).all()
        return cfrformreason_schema.dump(query)

    @classmethod
    def getcfrformreason(cls,cfrformreasonid):
        cfrformreason_schema = CFRFormReasonSchema(many=False)
        query = db.session.query(CFRFormReason).filter_by(cfrformreasonid=cfrformreasonid).first()
        return cfrformreason_schema.dump(query)
    
    @classmethod
    def getcfrformreasonid(cls,cfrformreason):
        cfrformreason_schema = CFRFormReasonSchema(many=False)
        query = db.session.query(CFRFormReason).filter(func.lower(CFRFormReason.name) == func.lower(cfrformreason)).first()
        return cfrformreason_schema.dump(query)
    
class CFRFormReasonSchema(ma.Schema):
    class Meta:
        fields = ('cfrformreasonid','name','description','isactive')