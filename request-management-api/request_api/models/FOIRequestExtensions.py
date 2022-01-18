from flask.app import Flask
from sqlalchemy.sql.schema import ForeignKey, ForeignKeyConstraint
from .db import  db, ma
from datetime import datetime
from sqlalchemy.orm import relationship,backref
from .default_method_result import DefaultMethodResult
from sqlalchemy.sql.expression import distinct
from sqlalchemy import or_,and_,text

class FOIRequestExtension(db.Model):
    # Name of the table in our database
    __tablename__ = 'FOIRequestExtensions'   
        
    # Defining the columns
    foirequestextensionid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    extendedduedays =db.Column(db.Integer, nullable=True)
    extendedduedate = db.Column(db.DateTime, nullable=True)
    decisiondate = db.Column(db.DateTime, nullable=True)
    approvednoofdays =db.Column(db.Integer, nullable=True)
    version =db.Column(db.Integer, nullable=True)
    isactive = db.Column(db.Boolean, unique=False, nullable=False,default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=True)
    createdby = db.Column(db.String(120), unique=False, nullable=False)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)
    
    #ForeignKey References   
    foiministryrequest_id =db.Column(db.Integer, ForeignKey('FOIMinistryRequests.foiministryrequestid'))
    foiministryrequestversion_id = db.Column(db.Integer, ForeignKey('FOIMinistryRequests.version'))    

    extensionstatusid =db.Column(db.Integer, unique=False, nullable=False)
    extensionreasonid =db.Column(db.Integer, unique=False, nullable=False)   
    
    @classmethod
    def getextension(cls,foirequestextensionid):   
        document_schema = FOIRequestExtensionSchema()            
        request = db.session.query(FOIRequestExtension).filter_by(foirequestextensionid=foirequestextensionid).order_by(FOIRequestExtension.version.desc()).first()
        return document_schema.dump(request)

    @classmethod
    def saveextension(cls,ministryrequestid,ministryrequestversion, extension, extensionreason, userid):
        
        createuserid = extension['createdby'] if 'createdby' in extension and extension['createdby'] is not None else userid
        createdat = extension['created_at'] if 'created_at' in extension  and extension['created_at'] is not None else datetime.now()
        decisiondate = extension['decisiondate'] if 'decisiondate' in extension else None
        approvednoofdays = extension['approvednoofdays'] if 'approvednoofdays' in extension else None

        if 'extensionstatusid' in extension:
            extensionstatusid = extension['extensionstatusid']
        elif 'extensiontype' in  extensionreason and extensionreason['extensiontype'] == 'Public Body': 
            extensionstatusid = 2
        else:
            extensionstatusid = 1        
      
        newextension = FOIRequestExtension(
        extensionreasonid=extension['extensionreasonid'], 
        extendedduedays=extension['extendedduedays'], 
        extendedduedate=extension['extendedduedate'], 
        decisiondate=decisiondate, 
        approvednoofdays=approvednoofdays, 
        extensionstatusid=extensionstatusid, 
        version=1, 
        isactive=True, 
        foiministryrequest_id=ministryrequestid, 
        foiministryrequestversion_id=ministryrequestversion, 
        created_at=createdat, 
        createdby=createuserid)        
        db.session.add(newextension)
        db.session.commit()
        return DefaultMethodResult(True,'Extension created', newextension.foirequestextensionid)      
    

    @classmethod
    def createextensionversion(cls,ministryrequestid,ministryrequestversion, extension, userid):
        # if 'document' in extension:
        #     newextensiondocument = 
        newextesion = FOIRequestExtension( foirequestextensionid=extension["foirequestextensionid"], extensionreasonid=extension['extensionreasonid'], extensionstatusid=extension['extensionstatusid'], extendedduedays=extension["extendedduedays"], extendedduedate=extension["extendedduedate"], decisiondate=extension["decisiondate"], approvednoofdays=extension["approvednoofdays"], version=extension["version"], isactive=extension["isactive"], foiministryrequest_id=ministryrequestid, foiministryrequestversion_id=ministryrequestversion, created_at=datetime.now(), createdby=userid)
        db.session.add(newextesion)
        db.session.commit()               
        return DefaultMethodResult(True,'New Extension version created', newextesion.foirequestextensionid) 

    @classmethod   
    def getextensions(cls,ministryrequestid,ministryrequestversion):
        sql = 'SELECT * FROM (SELECT DISTINCT ON (foirequestextensionid) foirequestextensionid, fre.extensionreasonid, er.reason, er.extensiontype, fre.extensionstatusid, es.name, extendedduedays, extendedduedate, decisiondate, approvednoofdays, fre.isactive, created_at , createdby, fre.version FROM "FOIRequestExtensions" fre INNER JOIN "ExtensionReasons" er ON fre.extensionreasonid = er.extensionreasonid INNER JOIN "ExtensionStatuses" es ON fre.extensionstatusid = es.extensionstatusid where foiministryrequest_id =:ministryrequestid and foiministryrequestversion_id = :ministryrequestversion ORDER BY foirequestextensionid, version DESC) AS list ORDER BY created_at DESC'
        rs = db.session.execute(text(sql), {'ministryrequestid': ministryrequestid, 'ministryrequestversion':ministryrequestversion})
        extensions = []
        for row in rs:
            if row["isactive"] == True:
                extensions.append(dict(row))
        return extensions    

        

class FOIRequestExtensionSchema(ma.Schema):
    class Meta:
        fields = ('foirequestextensionid', 'extensionreasonid', 'extensionstatusid', 'foiministryrequest_id', 'foiministryrequestversion_id', 'extendedduedays', 'extendedduedate', 'decisiondate', 'approvednoofdays', 'version', 'isactive')
    