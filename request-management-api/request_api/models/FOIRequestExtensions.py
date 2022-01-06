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
    __table_args__ = (
        ForeignKeyConstraint(
            ["foiministryrequest_id", "foiministryrequestversion_id"], ["FOIMinistryRequests.foiministryrequestid", "FOIMinistryRequests.version"]
        ),
        # ForeignKeyConstraint(['extensionreasonid'], ['ExtensionReasons.extensionreasonid'], ),
        # ForeignKeyConstraint(['extensionstatus_id'], ['ExtensionStatuses.extensionstatusid'], ),
    )
        
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
    foiministryrequest = relationship("FOIMinistryRequest",foreign_keys="[FOIRequestExtension.foiministryrequest_id]")
    foiministryrequestversion = relationship("FOIMinistryRequest",foreign_keys="[FOIRequestExtension.foiministryrequestversion_id]")

    extensionstatusid =db.Column(db.Integer, unique=False, nullable=False) #ForeignKey('ExtensionStatuses.extensionstatusid'))    
    # extensionstatus = relationship("ExtensionStatus",foreign_keys="FOIRequestExtension.extensionstatus_id")
    # extensionstatus = relationship("ExtensionStatus",uselist=False)

    extensionreasonid =db.Column(db.Integer, ForeignKey('ExtensionReasons.extensionreasonid'))
    # extensionreason = relationship("ExtensionReason",foreign_keys="FOIRequestExtension.extensionreasonid")
    extensionreason = relationship("ExtensionReason",uselist=False) 
    
    @classmethod
    def getextension(cls,foirequestextensionid):   
        document_schema = FOIRequestExtensionSchema()            
        request = db.session.query(FOIRequestExtension).filter_by(foirequestextensionid=foirequestextensionid).order_by(FOIRequestExtension.version.desc()).first()
        return document_schema.dump(request)

    @classmethod
    def createextension(cls,ministryrequestid,ministryrequestversion, extension, userid):
        createuserid = 'dviswana@idir' #extension['createdby'] if 'createdby' in extension and extension['createdby'] is not None else userid
        createdat = datetime.now() #extension['created_at'] if 'created_at' in extension  and extension['created_at'] is not None else datetime.now()
        decisiondate = None #extension['decisiondate'] if 'decisiondate' in extension else None
        approvednoofdays = None #extension['approvednoofdays'] if 'approvednoofdays' in extension else None
        # extensionstatusid = extension['extensionstatusid'] if 'extensionstatusid' in extension else 1
        extensionreasonid=1
        extendedduedays=None
        extendedduedate=None
        newextension = FOIRequestExtension(extensionreasonid=extensionreasonid, 
        extendedduedays=extendedduedays, extendedduedate=extendedduedate, 
        decisiondate=decisiondate, approvednoofdays=approvednoofdays, 
        extensionstatusid=1, version=1, isactive=True, 
        foiministryrequest_id=1, foiministryrequestversion_id=1, 
        created_at=createdat, createdby=createuserid, updated_at=createdat, updatedby=createuserid)

        db.session.add(newextension)
        db.session.commit()
        return DefaultMethodResult(True,'Extension created')   
    

    @classmethod
    def createextensionversion(cls,ministryrequestid,ministryrequestversion, extension, userid):
        newextesion = FOIRequestExtension( foirequestextensionid=extension["foirequestextensionid"], extendedduedays=extension["extendedduedays"], extendedduedate=extension["extendedduedate"], decisiondate=extension["decisiondate"], approvednoofdays=extension["approvednoofdays"], version=extension["version"], isactive=extension["isactive"], foiministryrequest_id=ministryrequestid, foiministryrequestversion_id=ministryrequestversion, created_at=datetime.now(), createdby=userid)
        db.session.add(newextesion)
        db.session.commit()               
        return DefaultMethodResult(True,'New Extension version created', newextesion.foirequestextensionid)   
    
    
class FOIRequestExtensionSchema(ma.Schema):
    class Meta:
        fields = ('foirequestextensionid', 'extensionreason.extensionreasonid', 'extensionstatusid', 'foiministryrequest.foiministryrequest_id', 'foiministryrequestversion.foiministryrequestversion_id', 'extendedduedays', 'extendedduedate', 'decisiondate', 'approvednoofdays', 'version', 'isactive')
    