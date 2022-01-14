from flask.app import Flask
from sqlalchemy.sql.schema import ForeignKey, ForeignKeyConstraint
from .db import  db, ma
from datetime import datetime
from sqlalchemy.orm import relationship,backref
from .default_method_result import DefaultMethodResult
from sqlalchemy.sql.expression import distinct
from sqlalchemy import or_,and_,text

class FOIRequestExtensionDocumentMapping(db.Model):
    # Name of the table in our database
    __tablename__ = 'FOIRequestExtensionDocumentMapping'   
        
    # Defining the columns
    foirequestextensiondocumentid = db.Column(db.Integer, primary_key=True,autoincrement=True)
        
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=True)
    createdby = db.Column(db.String(120), unique=False, nullable=False)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)
    
    #ForeignKey References   
    foirequestextensionid =db.Column(db.Integer, ForeignKey('FOIRequestExtensions.foirequestextensionid'))
    extensionversion = db.Column(db.Integer, ForeignKey('FOIRequestExtensions.version'))
    foiministrydocumentid =db.Column(db.Integer, ForeignKey('FOIMinistryRequestDocuments.foiministrydocumentid'))
    foiministryrequest_id =db.Column(db.Integer, ForeignKey('FOIMinistryRequests.foiministryrequestid'))

    @classmethod
    def getextensiondocument(cls,foirequestextensiondocumentid):   
        document_schema = FOIRequestExtensionDocumentMappingSchema()            
        request = db.session.query(FOIRequestExtensionDocumentMapping).filter_by(foirequestextensiondocumentid=foirequestextensiondocumentid)
        return document_schema.dump(request)
    @classmethod
    def saveextensiondocument(cls, ministryrequestid, extensionid, ministrydocumentid, version):
        newextensiondocument = FOIRequestExtensionDocumentMapping(
            foirequestextensionid=extensionid,
            extensionversion=version,
            foiministrydocumentid=ministrydocumentid,
            foiministryrequest_id=ministryrequestid
        )
        db.session.add(newextensiondocument)
        db.session.commit()
        return DefaultMethodResult(True,'Extension Document Mapping created', newextensiondocument.foirequestextensiondocumentid) 

class FOIRequestExtensionDocumentMappingSchema(ma.Schema):
    class Meta:
        fields = ('foirequestextensiondocumentid', 'foirequestextensionid', 'foiministrydocumentid', 'foiministryrequest_id', 'extensionversion')
    