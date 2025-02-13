from .db import  db, ma
from .default_method_result import DefaultMethodResult
from sqlalchemy.orm import relationship,backref
from datetime import datetime
from sqlalchemy import text

class CloseReason(db.Model):
    __tablename__ = 'CloseReasons' 
    # Defining the columns
    closereasonid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(500), unique=False, nullable=False)    
    isactive = db.Column(db.Boolean, unique=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    createdby = db.Column(db.String(120), unique=False, default='System')
    
    @classmethod
    def getallclosereasons(cls):
        closereason_schema = CloseReasonSchema(many=True)
        query = db.session.query(CloseReason).filter_by(isactive=True).order_by(CloseReason.closereasonid.asc()).all()
        return closereason_schema.dump(query)

    @classmethod
    def getclosereason(cls,closereasonid):
        closereason_schema = CloseReasonSchema(many=False)
        query = db.session.query(CloseReason).filter_by(closereasonid=closereasonid).first()
        return closereason_schema.dump(query)
    
             

class CloseReasonSchema(ma.Schema):
    class Meta:
        fields = ('closereasonid','name','isactive')