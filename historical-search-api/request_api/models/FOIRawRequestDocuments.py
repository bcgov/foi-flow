from flask.app import Flask
from sqlalchemy.sql.schema import ForeignKey, ForeignKeyConstraint
from .db import  db, ma
from datetime import datetime
from sqlalchemy.orm import relationship,backref
from .default_method_result import DefaultMethodResult
from sqlalchemy.sql.expression import distinct
from sqlalchemy import or_,and_,text
import logging
class FOIRawRequestDocument(db.Model):
    # Name of the table in our database
    __tablename__ = 'FOIRawRequestDocuments'
    __table_args__ = (
        ForeignKeyConstraint(
            ["foirequest_id", "foirequestversion_id"], ["FOIRawRequests.requestid", "FOIRawRequests.version"]
        ),
    )
        
    # Defining the columns
    foidocumentid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    documentpath = db.Column(db.String(1000), unique=False, nullable=False)
    filename = db.Column(db.String(120), unique=False, nullable=True)
    category = db.Column(db.String(120), unique=False, nullable=True)
    version =db.Column(db.Integer, nullable=True)
    isactive = db.Column(db.Boolean, unique=False, nullable=False,default=True)
 
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=True)
    createdby = db.Column(db.String(120), unique=False, nullable=True)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)
    
    #ForeignKey References   
    foirequest_id =db.Column(db.Integer, unique=False, nullable=False)
    foirequestversion_id = db.Column(db.Integer, unique=False, nullable=False)

    @classmethod
    def getdocuments(cls,requestid, requestversion):
        documents = []
        try:
            sql = 'SELECT * FROM (SELECT DISTINCT ON (foidocumentid) raw2.created_at, raw.created_at as current_version_created_at, raw.foidocumentid, raw.filename, raw.documentpath, raw.category, raw.isactive, raw.createdby  FROM "FOIRawRequestDocuments" raw  join "FOIRawRequestDocuments" raw2  on (raw.foirequest_id = raw2.foirequest_id and raw2.version = 1) where raw.foirequest_id = :requestid and raw.foirequestversion_id = :requestversion and raw.isactive = true ORDER BY raw.foidocumentid DESC) AS list ORDER BY created_at DESC'
            rs = db.session.execute(text(sql), {'requestid': requestid, 'requestversion': requestversion})
        
            for row in rs:
                if row["isactive"] == True:
                    documents.append({"foidocumentid": row["foidocumentid"], "filename": row["filename"], "documentpath": row["documentpath"], "category": row["category"], "created_at": row["created_at"].strftime('%Y-%m-%d %H:%M:%S.%f'), "createdby": row["createdby"]})
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return documents 
    
    @classmethod
    def getdocument(cls,foidocumentid):   
        document_schema = FOIRawRequestDocumentSchema()            
        request = db.session.query(FOIRawRequestDocument).filter_by(foidocumentid=foidocumentid).order_by(FOIRawRequestDocument.version.desc()).first()
        return document_schema.dump(request)

    @classmethod
    def createdocuments(cls,requestid,requestversion, documents, userid):
        newdocuments = []
        for document in documents:
            createuserid = document['createdby'] if 'createdby' in document and document['createdby'] is not None else userid
            createdat = document['created_at'] if 'created_at' in document  and document['created_at'] is not None else datetime.now()
            newdocuments.append(FOIRawRequestDocument(documentpath=document["documentpath"], version='1', filename=document["filename"], category=document["category"], isactive=True, foirequest_id=requestid, foirequestversion_id=requestversion, created_at=createdat, createdby=createuserid))
        db.session.add_all(newdocuments)
        db.session.commit()               
        return DefaultMethodResult(True,'Documents created')   
    

    @classmethod
    def createdocumentversion(cls,requestid,requestversion, document, userid):
        newdocument = FOIRawRequestDocument(documentpath=document["documentpath"], foidocumentid=document["foidocumentid"], version=document["version"], filename=document["filename"], category=document["category"], isactive=document["isactive"], foirequest_id=requestid, foirequestversion_id=requestversion, created_at=datetime.now(), createdby=userid)
        db.session.add(newdocument)
        db.session.commit()               
        return DefaultMethodResult(True,'New Document version created', newdocument.foidocumentid)

    @classmethod
    def deActivaterawdocumentsversion(cls, documentid, currentversion, userid)->DefaultMethodResult:
        db.session.query(FOIRawRequestDocument).filter(FOIRawRequestDocument.foidocumentid == documentid, FOIRawRequestDocument.version == currentversion).update({"isactive": False, "updated_at": datetime.now(),"updatedby": userid}, synchronize_session=False)
        db.session.commit()
        return DefaultMethodResult(True,'Raw Request Document Updated',documentid) 
    
    
class FOIRawRequestDocumentSchema(ma.Schema):
    class Meta:
        fields = ('foidocumentid','documentpath', 'filename','category','version','isactive','foirequest_id','foirequestversion_id','created_at','createdby')
    