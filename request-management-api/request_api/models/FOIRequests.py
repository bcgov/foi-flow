from flask.app import Flask
from sqlalchemy.sql.schema import ForeignKey
from .db import  db, ma
from datetime import datetime
from sqlalchemy.orm import relationship,backref
from .default_method_result import DefaultMethodResult
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.sql.expression import distinct
from sqlalchemy import text
import logging

import json
class FOIRequest(db.Model):
    # Name of the table in our database
    __tablename__ = 'FOIRequests' 
    # Defining the columns
    foirequestid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    version = db.Column(db.Integer, primary_key=True,nullable=False)
    requesttype = db.Column(db.String(15), unique=False, nullable=False)
    receiveddate = db.Column(db.DateTime, default=datetime.now)
    isactive = db.Column(db.Boolean, unique=False, nullable=False,default=True)

    initialdescription = db.Column(db.String(500), unique=False, nullable=True)
    initialrecordsearchfromdate = db.Column(db.DateTime, nullable=True)
    initialrecordsearchtodate = db.Column(db.DateTime, nullable=True)
                
    created_at = db.Column(db.DateTime, default=datetime.now)
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
    def saverequest(cls,foirequest)->DefaultMethodResult:
        db.session.add(foirequest)
        db.session.commit()
        ministryarr = [] 
        for ministry in foirequest.ministryRequests:
            assignedministrygroup = ministry.assignedministrygroup if ministry.assignedministrygroup is not None else ""                                
            assignedgroup = ministry.assignedgroup if ministry.assignedgroup is not None else ""                                
            ministryarr.append({"id": ministry.foiministryrequestid, "foirequestid": ministry.foirequest_id, "axisrequestid": ministry.axisrequestid, "filenumber": ministry.filenumber, "status": ministry.requeststatus.name, "assignedministrygroup": assignedministrygroup, "assignedgroup": assignedgroup, "version":ministry.version})    
        return DefaultMethodResult(True,'Request added',foirequest.foirequestid,ministryarr,foirequest.wfinstanceid)
                          
    @classmethod
    def updateWFInstance(cls, foirequestid, wfinstanceid, userid)->DefaultMethodResult:
        currequest = db.session.query(FOIRequest).filter_by(foirequestid=foirequestid).order_by(FOIRequest.version.desc()).first()
        setattr(currequest,'wfinstanceid',wfinstanceid)
        setattr(currequest,'updated_at',datetime.now().isoformat())
        setattr(currequest,'updatedby',userid)
        db.session.commit()  
        return DefaultMethodResult(True,'Request updated',foirequestid)
    
    @classmethod
    def updateStatus(cls, foirequestid, updatedministries, userid)->DefaultMethodResult:
        currequest = db.session.query(FOIRequest).filter_by(foirequestid=foirequestid).order_by(FOIRequest.version.desc()).first()
        for ministry in currequest.ministryRequests:
            for data in updatedministries:
                if ministry.filenumber == data["filenumber"]:
                    ministry.requeststatusid = data["requeststatusid"]
                    ministry.updated_at = datetime.now().isoformat()
                    ministry.updatedby = userid
        currequest.updated_at = datetime.now().isoformat()
        currequest.updatedby = userid
        db.session.commit()  
        return DefaultMethodResult(True,'Request updated',foirequestid)


    @classmethod
    def getworkflowinstance(cls,requestid)->DefaultMethodResult:
        instanceid = None
        try:
            sql = """select fr3.wfinstanceid from "FOIMinistryRequests" fr2, "FOIRequests" fr3 
                        where fr2.foirequest_id = fr3.foirequestid and fr2.foiministryrequestid=:requestid 
                        and fr3.wfinstanceid is not null order by  fr2."version" limit 1;"""
            rs = db.session.execute(text(sql), {'requestid': requestid})
            for row in rs:
                instanceid =  row[0]
        except Exception as ex:
            logging.error(ex)
        finally:
            db.session.close()
        return instanceid  
    
class FOIRequestsSchema(ma.Schema):
    class Meta:
        fields = ('foirequestid','version','foirawrequestid','requesttype','receiveddate','initialdescription',
                'initialrecordSearchFromDate','initialrecordsearchtodate','receivedmode.receivedmodeid',
                'deliverymode.deliverymodeid','receivedmode.name','deliverymode.name',
                'applicantcategory.applicantcategoryid','applicantcategory.name','wfinstanceid','ministryRequests')
    