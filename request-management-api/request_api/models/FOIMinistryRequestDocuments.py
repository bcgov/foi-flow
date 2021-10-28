from flask.app import Flask
from sqlalchemy.sql.schema import ForeignKey, ForeignKeyConstraint
from .db import  db, ma
from datetime import datetime
from sqlalchemy.orm import relationship,backref
from .default_method_result import DefaultMethodResult
from sqlalchemy.sql.expression import distinct
from sqlalchemy import or_,and_


class FOIMinistryRequestDocument(db.Model):
    # Name of the table in our database
    __tablename__ = 'FOIMinistryRequestDocuments'
    __table_args__ = (
        ForeignKeyConstraint(
            ["foiministryrequest_id", "foiministryrequestversion_id"], ["FOIMinistryRequests.foiministryrequestid", "FOIMinistryRequests.version"]
        ),
    )
        
    # Defining the columns
    foiministrydocumentid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    documentpath = db.Column(db.String(1000), unique=False, nullable=False)
 
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=True)
    createdby = db.Column(db.String(120), unique=False, nullable=True)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)
    
    #ForeignKey References   
    foiministryrequest_id =db.Column(db.Integer, db.ForeignKey('FOIMinistryRequests.foiministryrequestid'))
    foiministryrequestversion_id = db.Column(db.Integer, db.ForeignKey('FOIMinistryRequests.version'))    
    foiministryrequest = relationship("FOIMinistryRequest",foreign_keys="[FOIMinistryRequestDocument.foiministryrequest_id]")
    foiministryrequestversion = relationship("FOIMinistryRequest",foreign_keys="[FOIMinistryRequestDocument.foiministryrequestversion_id]")

    @classmethod
    def getdocuments(cls,ministryrequestid,ministryrequestversion):
        file_schema = FOIMinistryRequestDocumentSchema(many=True)
        _files = db.session.query(FOIMinistryRequestDocument).filter(FOIMinistryRequestDocument.foiministryrequest_id == ministryrequestid , FOIMinistryRequestDocument.foiministryrequestversion_id == ministryrequestversion).order_by(FOIMinistryRequestDocument.foiministrydocumentid.asc()).all()
        files = file_schema.dump(_files)       
        return files
    
class FOIMinistryRequestDocumentSchema(ma.Schema):
    class Meta:
        fields = ('foiministrydocumentid','documentpath','foiministryrequest_id','foiministryrequestversion_id','created_at','createdby')
    