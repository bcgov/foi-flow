from .db import  db, ma
from .default_method_result import DefaultMethodResult
from sqlalchemy.orm import relationship,backref
from datetime import datetime
from sqlalchemy import text

class ConsultType(db.Model):
    __tablename__ = 'FOIMinistryRequestConsultTypes' 
    # Defining the columns
    consulttypeid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(100), unique=False, nullable=False)   
    isactive = db.Column(db.Boolean, unique=False, nullable=False)

class ConsultTypesSchema(ma.Schema):
    class Meta:
        fields = ('consulttypeid', 'name', 'isactive')