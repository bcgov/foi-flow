from flask.app import Flask
from sqlalchemy.sql.schema import ForeignKey, ForeignKeyConstraint
from .db import  db, ma
from datetime import datetime
from sqlalchemy.orm import relationship,backref
from .default_method_result import DefaultMethodResult
from sqlalchemy.sql.expression import distinct
from sqlalchemy import or_,and_,text

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
    filename = db.Column(db.String(120), unique=False, nullable=True)
    category = db.Column(db.String(120), unique=False, nullable=True)
    version =db.Column(db.Integer, nullable=True)
    isactive = db.Column(db.Boolean, unique=False, nullable=False,default=True)
 
    created_at = db.Column(db.DateTime, default=datetime.now)
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
        sql = 'SELECT * FROM (SELECT DISTINCT ON (foiministrydocumentid) foiministrydocumentid, filename, documentpath, category, isactive, created_at , createdby, version FROM "FOIMinistryRequestDocuments" where foiministryrequest_id =:ministryrequestid and foiministryrequestversion_id = :ministryrequestversion ORDER BY foiministrydocumentid, version DESC) AS list ORDER BY created_at DESC'
        rs = db.session.execute(text(sql), {'ministryrequestid': ministryrequestid, 'ministryrequestversion':ministryrequestversion})
        documents = []
        for row in rs:
            if row["isactive"] == True:
                documents.append({"foiministrydocumentid": row["foiministrydocumentid"], "filename": row["filename"], "documentpath": row["documentpath"], "category": row["category"], "created_at": row["created_at"].strftime('%Y-%m-%d %H:%M:%S.%f'), "createdby": row["createdby"], "version": row["version"]})
        return documents
    
    @classmethod
    def getactivedocuments(cls,ministryrequestid):
        sql = 'SELECT * FROM (SELECT DISTINCT ON (foiministrydocumentid) foiministrydocumentid, filename, documentpath, category, isactive, created_at , createdby, version FROM "FOIMinistryRequestDocuments" where foiministryrequest_id =:ministryrequestid ORDER BY foiministrydocumentid, version DESC) AS list ORDER BY created_at DESC'
        rs = db.session.execute(text(sql), {'ministryrequestid': ministryrequestid})
        documents = []
        for row in rs:
            if row["isactive"] == True:
                documents.append({"foiministrydocumentid": row["foiministrydocumentid"], "filename": row["filename"], "documentpath": row["documentpath"], "category": row["category"], "created_at": row["created_at"].strftime('%Y-%m-%d %H:%M:%S.%f'), "createdby": row["createdby"], "version": row["version"]})
        return documents

    @classmethod
    def getdocumentsbycategory(cls, ministryrequestid, ministryrequestversion, category):
        sql = 'SELECT * FROM (SELECT DISTINCT ON (foiministrydocumentid) foiministrydocumentid, filename, documentpath, category, isactive, created_at , createdby, version FROM "FOIMinistryRequestDocuments" where foiministryrequest_id =:ministryrequestid and foiministryrequestversion_id = :ministryrequestversion and category = :category ORDER BY foiministrydocumentid, version DESC) AS list ORDER BY created_at DESC'
        rs = db.session.execute(text(sql), {'ministryrequestid': ministryrequestid, 'ministryrequestversion':ministryrequestversion, 'category': category})
        documents = []
        for row in rs:
            if row["isactive"] == True:
                documents.append({"foiministrydocumentid": row["foiministrydocumentid"], "filename": row["filename"], "documentpath": row["documentpath"], "category": row["category"], "created_at": row["created_at"].strftime('%Y-%m-%d %H:%M:%S.%f'), "createdby": row["createdby"]})
        return documents 
    @classmethod
    def getdocument(cls,foiministrydocumentid):   
        document_schema = FOIMinistryRequestDocumentSchema()            
        request = db.session.query(FOIMinistryRequestDocument).filter_by(foiministrydocumentid=foiministrydocumentid).order_by(FOIMinistryRequestDocument.version.desc()).first()
        return document_schema.dump(request)

    @classmethod
    def createdocuments(cls,ministryrequestid,ministryrequestversion, documents, userid):
        newdocuments = []
        for document in documents:
            createuserid = document['createdby'] if 'createdby' in document and document['createdby'] is not None else userid
            createdat = document['created_at'] if 'created_at' in document  and document['created_at'] is not None else datetime.now()
            newdocuments.append(FOIMinistryRequestDocument(documentpath=document["documentpath"], version='1', filename=document["filename"], category=document["category"], isactive=True, foiministryrequest_id=ministryrequestid, foiministryrequestversion_id=ministryrequestversion, created_at=createdat, createdby=createuserid))
        db.session.add_all(newdocuments)
        db.session.commit()               
        return DefaultMethodResult(True,'Documents created')   
    
    @classmethod
    def createdocument(cls,ministryrequestid,ministryrequestversion, document, userid):
        createuserid = document['createdby'] if 'createdby' in document and document['createdby'] is not None else userid
        createdat = document['created_at'] if 'created_at' in document  and document['created_at'] is not None else datetime.now()
        newdocument = FOIMinistryRequestDocument(documentpath=document["documentpath"], version='1', filename=document["filename"], category=document["category"], isactive=True, foiministryrequest_id=ministryrequestid, foiministryrequestversion_id=ministryrequestversion, created_at=createdat, createdby=createuserid)
        db.session.add(newdocument)
        db.session.commit()               
        return DefaultMethodResult(True,'New Document version created', newdocument.foiministrydocumentid) 

    @classmethod
    def createdocumentversion(cls,ministryrequestid,ministryrequestversion, document, userid):
        newdocument = FOIMinistryRequestDocument(documentpath=document["documentpath"], foiministrydocumentid=document["foiministrydocumentid"], version=document["version"], filename=document["filename"], category=document["category"], isactive=document["isactive"], foiministryrequest_id=ministryrequestid, foiministryrequestversion_id=ministryrequestversion, created_at=datetime.now(), createdby=userid)
        db.session.add(newdocument)
        db.session.commit()               
        return DefaultMethodResult(True,'New Document version created', newdocument.foiministrydocumentid)  

    @classmethod

    def getlatestdocumentsforemail(cls, ministryrequestid, ministryrequestversion, category):
        sql = 'SELECT DISTINCT ON (foiministrydocumentid) foiministrydocumentid, filename, documentpath, category, isactive, created_at , createdby, version FROM "FOIMinistryRequestDocuments" where foiministryrequest_id =:ministryrequestid and foiministryrequestversion_id = :ministryrequestversion and lower(category) = lower(:category) ORDER BY foiministrydocumentid DESC'

        rs = db.session.execute(text(sql), {'ministryrequestid': ministryrequestid, 'ministryrequestversion':ministryrequestversion, 'category': category})
        documents = []
        for row in rs:
            if row["isactive"] == True:
                documents.append({"foiministrydocumentid": row["foiministrydocumentid"], "filename": row["filename"], "documentpath": row["documentpath"], "category": row["category"], "created_at": row["created_at"].strftime('%Y-%m-%d %H:%M:%S.%f'), "createdby": row["createdby"]})
        return documents 

    def getlatestreceiptdocumentforemail(cls, ministryrequestid, category):
        sql = 'SELECT DISTINCT ON (foiministrydocumentid) foiministrydocumentid, filename, documentpath, category, isactive, created_at , createdby, version FROM "FOIMinistryRequestDocuments" where foiministryrequest_id =:ministryrequestid and lower(category) = lower(:category) ORDER BY foiministrydocumentid DESC limit 1'

        rs = db.session.execute(text(sql), {'ministryrequestid': ministryrequestid, 'category': category})
        documents = []
        for row in rs:
            if row["isactive"] == True:
                documents.append({"foiministrydocumentid": row["foiministrydocumentid"], "filename": row["filename"], "documentpath": row["documentpath"], "category": row["category"], "created_at": row["created_at"].strftime('%Y-%m-%d %H:%M:%S.%f'), "createdby": row["createdby"]})
        return documents  

    @classmethod
    def deActivateministrydocumentsversion(cls, foiministrydocumentid, currentversion, userid)->DefaultMethodResult:
        db.session.query(FOIMinistryRequestDocument).filter(FOIMinistryRequestDocument.foiministrydocumentid == foiministrydocumentid, FOIMinistryRequestDocument.version == currentversion).update({"isactive": False, "updated_at": datetime.now(),"updatedby": userid}, synchronize_session=False)
        db.session.commit()
        return DefaultMethodResult(True,'Ministry Document Updated',foiministrydocumentid)
    
    @classmethod
    def deActivateministrydocumentsversionbyministry(cls, ministryid, ministryversion, userid)->DefaultMethodResult:
        db.session.query(FOIMinistryRequestDocument).filter(FOIMinistryRequestDocument.foiministryrequest_id == ministryid, FOIMinistryRequestDocument.foiministryrequestversion_id == ministryversion).update({"isactive": False, "updated_at": datetime.now(),"updatedby": userid}, synchronize_session=False)
        db.session.commit()
        return DefaultMethodResult(True,'Documents Updated for the ministry',ministryid) 
    
class FOIMinistryRequestDocumentSchema(ma.Schema):
    class Meta:
        fields = ('foiministrydocumentid','documentpath', 'filename','category','version','isactive','foiministryrequest_id','foiministryrequestversion_id','created_at','createdby')
    
