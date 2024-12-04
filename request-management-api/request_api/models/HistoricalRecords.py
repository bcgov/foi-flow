from flask.app import Flask
from sqlalchemy.sql.schema import ForeignKey, ForeignKeyConstraint
from .db import  db, ma
from datetime import datetime
from sqlalchemy.orm import relationship,backref
from .default_method_result import DefaultMethodResult
from sqlalchemy.sql.expression import distinct
from sqlalchemy import or_,and_,text

class HistoricalRecords(db.Model):
    # Name of the table in our database
    __tablename__ = 'HistoricalRecords'
        
    # Defining the columns
    historicalrecordid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    recordfilename = db.Column(db.String(500), unique=False, nullable=False)
    description = db.Column(db.String(500), unique=False, nullable=True)
    axisrequestid = db.Column(db.String(120), unique=False, nullable=False)
    s3uripath = db.Column(db.Text, unique=False, nullable=False)
    attributes = db.Column(db.Text, unique=False, nullable=True)
    iscorresponcedocument = db.Column(db.Boolean, unique=False, nullable=False)
    displayfilename = db.Column(db.String(500), unique=False, nullable=True)
 
    created_at = db.Column(db.DateTime, default=datetime.now)
    createdby = db.Column(db.String(120), unique=False, nullable=True)

    @classmethod
    def getdocuments(cls,axisrequestid):        
        comment_schema = HistoricalRecordschema(many=True)
        query = db.session.query(HistoricalRecords).filter_by(axisrequestid=axisrequestid).order_by(HistoricalRecords.attributes.desc(), HistoricalRecords.historicalrecordid.asc()).all()
        return comment_schema.dump(query)   
    
    
    
class HistoricalRecordschema(ma.Schema):
    class Meta:
        fields = ('historicalrecordid', 'recordfilename', 'description', 'axisrequestid', 's3uripath', 'attributes', 'iscorresponcedocument', 'displayfilename', 'created_at', 'createdby') 
    
