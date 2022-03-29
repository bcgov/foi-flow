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
        
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=True)
    createdby = db.Column(db.String(120), unique=False, nullable=False)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)
    
    #ForeignKey References   
    foirequestextensionid =db.Column(db.Integer, ForeignKey('FOIRequestExtensions.foirequestextensionid'))
    extensionversion = db.Column(db.Integer, ForeignKey('FOIRequestExtensions.version'))
    foiministrydocumentid =db.Column(db.Integer, ForeignKey('FOIMinistryRequestDocuments.foiministrydocumentid'))

    @classmethod
    def getextensiondocument(cls,foirequestextensiondocumentid):   
        document_schema = FOIRequestExtensionDocumentMappingSchema()            
        request = db.session.query(FOIRequestExtensionDocumentMapping).filter_by(foirequestextensiondocumentid=foirequestextensiondocumentid)
        return document_schema.dump(request)
    
    @classmethod
    def getextensiondocuments(cls,foirequestextensionid, extensionversion):   
        document_schema = FOIRequestExtensionDocumentMappingSchema(many=True)   
        request = db.session.query(FOIRequestExtensionDocumentMapping).filter(FOIRequestExtensionDocumentMapping.foirequestextensionid == foirequestextensionid, FOIRequestExtensionDocumentMapping.extensionversion == extensionversion).all()
        return document_schema.dump(request)
        
    @classmethod
    def saveextensiondocument(cls, extensionid, documents, version, userid):        
        newdocuments = []        
        for document in documents:
            createuserid = document['createdby'] if 'createdby' in document and document['createdby'] is not None else userid
            createdat = document['created_at'] if 'created_at' in document  and document['created_at'] is not None else datetime.now()
            newextensiondocument = FOIRequestExtensionDocumentMapping(
                foirequestextensionid=extensionid,
                extensionversion=version,
                foiministrydocumentid=document["foiministrydocumentid"],
                created_at=createdat, 
                createdby=createuserid
            )
            newdocuments.append(newextensiondocument)
        db.session.add_all(newdocuments)
        db.session.commit()
        return DefaultMethodResult(True,'Extension Document Mapping created') 

class FOIRequestExtensionDocumentMappingSchema(ma.Schema):
    class Meta:
        fields = ('foirequestextensiondocumentid', 'foirequestextensionid', 'foiministrydocumentid', 'extensionversion','created_at','createdby','updated_at','updatedby')
    