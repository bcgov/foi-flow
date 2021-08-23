from flask.app import Flask
from sqlalchemy.sql.schema import ForeignKey
from .db import  db, ma
from datetime import datetime
from sqlalchemy.orm import relationship,backref
from .default_method_result import DefaultMethodResult
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.sql.expression import distinct

import json
class FOIRequest(db.Model):
    # Name of the table in our database
    __tablename__ = 'FOIRequests' 
    # Defining the columns
    foirequestid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    version = db.Column(db.Integer, primary_key=True,nullable=False)
    requesttype = db.Column(db.String(15), unique=False, nullable=False)
    receiveddate = db.Column(db.DateTime, default=datetime.now())
    isactive = db.Column(db.Boolean, unique=False, nullable=False,default=True)

    initialdescription = db.Column(db.String(500), unique=False, nullable=True)
    initialrecordsearchfromdate = db.Column(db.DateTime, nullable=True)
    initialrecordsearchtodate = db.Column(db.DateTime, nullable=True)
                
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=True)
    createdby = db.Column(db.String(120), unique=False, nullable=True)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)
    wfinstanceid = db.Column(UUID(as_uuid=True), unique=False, nullable=True)

    #ForeignKey References
    
    applicantcategoryid = db.Column(db.Integer,ForeignKey('ApplicantCategories.applicantcategoryid'))
    applicantcategory =  relationship("ApplicantCategory",backref=backref("ApplicantCategories"),uselist=False)

    deliverymodeid = db.Column(db.Integer,ForeignKey('DeliveryModes.deliverymodeid'))
    deliverymode =  relationship("DeliveryMode",backref=backref("DeliveryModes"),uselist=False)
    
    receivedmodeid = db.Column(db.Integer,ForeignKey('ReceivedModes.receivedmodeid'))
    receivedmode =  relationship("ReceivedMode",backref=backref("ReceivedModes"),uselist=False)

    foirawrequestid = db.Column(db.Integer,unique=False, nullable=True)

    ministryRequests = relationship('FOIMinistryRequest', primaryjoin="and_(FOIRequest.foirequestid==FOIMinistryRequest.foirequest_id, "
                        "FOIRequest.version==FOIMinistryRequest.foirequestversion_id)")
    
    contactInformations = relationship('FOIRequestContactInformation', primaryjoin="and_(FOIRequest.foirequestid==FOIRequestContactInformation.foirequest_id, "
                        "FOIRequest.version==FOIRequestContactInformation.foirequestversion_id)")
    
    personalAttributes = relationship('FOIRequestPersonalAttribute', primaryjoin="and_(FOIRequest.foirequestid==FOIRequestPersonalAttribute.foirequest_id, "
                        "FOIRequest.version==FOIRequestPersonalAttribute.foirequestversion_id)")
    
    requestApplicants = relationship('FOIRequestApplicantMapping', primaryjoin="and_(FOIRequest.foirequestid==FOIRequestApplicantMapping.foirequest_id, "
                        "FOIRequest.version==FOIRequestApplicantMapping.foirequestversion_id)")
    


   
    
    @classmethod
    def getrequest(cls,foirequestid):
        request_schema = FOIRequestsSchema()
        query = db.session.query(FOIRequest).filter_by(foirequestid=foirequestid).order_by(FOIRequest.version.desc()).first()
        return request_schema.dump(query)
   
    @classmethod
    def saverequest(cls,foiRequest)->DefaultMethodResult:
        db.session.add(foiRequest)
        db.session.commit()
        ministryArr = [] 
        for ministry in foiRequest.ministryRequests:
            ministryArr.append({"id": ministry.foiministryrequestid, "filenumber": ministry.filenumber})    
        return DefaultMethodResult(True,'Request added',foiRequest.foirequestid,ministryArr)
                          
    @classmethod
    def updateWFInstance(cls, foirequestid, wfinstanceid)->DefaultMethodResult:
        curRequest = db.session.query(FOIRequest).filter_by(foirequestid=foirequestid).order_by(FOIRequest.version.desc()).first()
        setattr(curRequest,'wfinstanceid',wfinstanceid)
        setattr(curRequest,'updated_at',datetime.now().isoformat())
        db.session.commit()  
        return DefaultMethodResult(True,'Request updated',foirequestid)
    
    @classmethod
    def updateStatus(cls, foirequestid, updatedMinistries)->DefaultMethodResult:
        curRequest = db.session.query(FOIRequest).filter_by(foirequestid=foirequestid).order_by(FOIRequest.version.desc()).first()
        for ministry in curRequest.ministryRequests:
            for data in updatedMinistries:
                if ministry.filenumber == data["filenumber"]:
                    ministry.requeststatusid = data["requeststatusid"]
                    ministry.updated_at = datetime.now().isoformat()
        curRequest.updated_at = datetime.now().isoformat()
        db.session.commit()  
        return DefaultMethodResult(True,'Request updated',foirequestid)
    
class FOIRequestsSchema(ma.Schema):
    class Meta:
        fields = ('foirequestid','version','requesttype','receiveddate','initialdescription','initialrecordSearchFromDate','initialrecordsearchtodate','receivedmode.receivedmodeid','deliverymode.deliverymodeid','receivedmode.name','deliverymode.name','applicantcategory.applicantcategoryid','applicantcategory.name','wfinstanceid','ministryRequests')
    