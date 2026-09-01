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
    requesttype = db.Column(db.String(30), unique=False, nullable=False)
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
    wfengine = db.Column(db.String(20), unique=False, nullable=True)
    wfmetadata = db.Column(JSON, unique=False, nullable=True)

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
        if wfinstanceid not in (None, ""):
            currequest = db.session.query(FOIRequest).filter_by(foirequestid=foirequestid).order_by(FOIRequest.version.desc()).first()
            setattr(currequest,'wfinstanceid',wfinstanceid)
            setattr(currequest,'updated_at',datetime.now().isoformat())
            setattr(currequest,'updatedby',userid)
            db.session.commit()
            return DefaultMethodResult(True,'Request updated',foirequestid)
        return DefaultMethodResult(True,'wfinstanceid is None',foirequestid)

    @classmethod
    def updateWFExecutionInfo(cls, foirequestid, executionid, resumepath, userid)->DefaultMethodResult:
        """n8n counterpart to updateWFInstance: stamps wfengine='n8n' and merges
        {executionId, resumePath} into wfmetadata, leaving wfinstanceid untouched.
        resumepath is optional - when absent (status-update payloads), any
        resumePath already in wfmetadata is preserved rather than cleared."""
        if executionid not in (None, ""):
            currequest = db.session.query(FOIRequest).filter_by(foirequestid=foirequestid).order_by(FOIRequest.version.desc()).first()
            if currequest is None:
                return DefaultMethodResult(True,'foirequestid is None',foirequestid)
            wfmetadata = dict(currequest.wfmetadata) if currequest.wfmetadata else {}
            wfmetadata['executionId'] = executionid
            if resumepath not in (None, ""):
                wfmetadata['resumePath'] = resumepath
            setattr(currequest,'wfengine','n8n')
            setattr(currequest,'wfmetadata',wfmetadata)
            setattr(currequest,'updated_at',datetime.now().isoformat())
            setattr(currequest,'updatedby',userid)
            db.session.commit()
            return DefaultMethodResult(True,'Request updated',foirequestid)
        return DefaultMethodResult(True,'executionId is None',foirequestid)

    @classmethod
    def getwfengine(cls, foirequestid):
        currequest = db.session.query(FOIRequest).filter_by(foirequestid=foirequestid).order_by(FOIRequest.version.desc()).first()
        if currequest is None:
            return None
        if currequest.wfengine not in (None, ""):
            return currequest.wfengine
        if currequest.foirawrequestid is not None:
            from request_api.models.FOIRawRequests import FOIRawRequest
            return FOIRawRequest.getwfengine(currequest.foirawrequestid)
        return None

    @classmethod
    def getwfenginebyministryrequestid(cls, ministryrequestid):
        try:
            sql = """select fr3.wfengine, fr3.foirawrequestid from "FOIMinistryRequests" fr2, "FOIRequests" fr3
                        where fr2.foirequest_id = fr3.foirequestid and fr2.foiministryrequestid=:requestid
                        order by fr3."version" desc limit 1"""
            rs = db.session.execute(text(sql), {'requestid': ministryrequestid})
            for row in rs:
                if row["wfengine"] not in (None, ""):
                    return row["wfengine"]
                if row["foirawrequestid"] is not None:
                    from request_api.models.FOIRawRequests import FOIRawRequest
                    return FOIRawRequest.getwfengine(row["foirawrequestid"])
        except Exception as ex:
            logging.error(ex)
        finally:
            db.session.close()
        return None

    @classmethod
    def getwfmetadata(cls, foirequestid):
        currequest = db.session.query(FOIRequest).filter_by(foirequestid=foirequestid).order_by(FOIRequest.version.desc()).first()
        logging.info("FOIRequest.getwfmetadata: foirequestid=%r -> currequest=%r", foirequestid, currequest)
        logging.info("FOIRequest.getwfmetadata: foirequestid=%r -> wfmetadata=%r", foirequestid, currequest.wfmetadata if currequest is not None else None)
        return currequest.wfmetadata if currequest is not None else None

    @classmethod
    def getwfmetadatabyministryrequestid(cls, ministryrequestid):
        try:
            sql = """select fr3.wfmetadata from "FOIMinistryRequests" fr2, "FOIRequests" fr3
                        where fr2.foirequest_id = fr3.foirequestid and fr2.foiministryrequestid=:requestid
                        order by fr3."version" desc limit 1"""
            rs = db.session.execute(text(sql), {'requestid': ministryrequestid})
            for row in rs:
                return row["wfmetadata"]
        except Exception as ex:
            logging.error(ex)
        finally:
            db.session.close()
        return None

    @classmethod
    def updatewfmetadata(cls, foirequestid, wfmetadata, userid)->DefaultMethodResult:
        currequest = db.session.query(FOIRequest).filter_by(foirequestid=foirequestid).order_by(FOIRequest.version.desc()).first()
        if currequest is None:
            return DefaultMethodResult(False,'Request not found',foirequestid)
        merged = dict(currequest.wfmetadata) if currequest.wfmetadata else {}
        merged.update(wfmetadata or {})
        setattr(currequest,'wfmetadata',merged)
        setattr(currequest,'updated_at',datetime.now().isoformat())
        setattr(currequest,'updatedby',userid)
        db.session.commit()
        return DefaultMethodResult(True,'wfmetadata updated',foirequestid)

    @classmethod
    def updatewfmetadatabyministryrequestid(cls, ministryrequestid, wfmetadata, userid)->DefaultMethodResult:
        foirequestid = None
        try:
            sql = """select fr3.foirequestid from "FOIMinistryRequests" fr2, "FOIRequests" fr3
                        where fr2.foirequest_id = fr3.foirequestid and fr2.foiministryrequestid=:requestid
                        order by fr3."version" desc limit 1"""
            rs = db.session.execute(text(sql), {'requestid': ministryrequestid})
            for row in rs:
                foirequestid = row["foirequestid"]
        except Exception as ex:
            logging.error(ex)
        if foirequestid is None:
            return DefaultMethodResult(False,'Ministry request not found',ministryrequestid)
        return cls.updatewfmetadata(foirequestid, wfmetadata, userid)

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
        request_schema = FOIRequestsSchema()
        try:
            sql = """select fr3.wfinstanceid, fr3.foirequestid, fr3.wfengine, fr3.wfmetadata  from "FOIMinistryRequests" fr2, "FOIRequests" fr3
                        where fr2.foirequest_id = fr3.foirequestid and fr2.foiministryrequestid=:requestid
                        order by  fr3."version" desc limit 1"""
            rs = db.session.execute(text(sql), {'requestid': requestid})
            for row in rs:
                request_schema.__dict__.update({"wfinstanceid":row["wfinstanceid"] , "foirequestid": row["foirequestid"], "wfengine": row["wfengine"], "wfmetadata": row["wfmetadata"]})
        except Exception as ex:
            logging.error(ex)
        finally:
            db.session.close()
        return request_schema  
    @classmethod
    def getrawrequestidbyfoirequestid(cls,requestid)->DefaultMethodResult:
        try:
            sql = """select fr.foirawrequestid, fr.foirequestid  from "FOIRequests" fr
                        where fr.foirequestid=:requestid
                        order by  fr."version" desc limit 1"""
            rs = db.session.execute(text(sql), {'requestid': requestid})
            rawrequestid = None
            for row in rs:
                rawrequestid = row["foirawrequestid"]
        except Exception as ex:
            logging.error(ex)
        finally:
            db.session.close()
        return rawrequestid
    
class FOIRequestsSchema(ma.Schema):
    class Meta:
        fields = ('foirequestid','version','foirawrequestid','requesttype','receiveddate','initialdescription',
                'initialrecordSearchFromDate','initialrecordsearchtodate','receivedmode.receivedmodeid',
                'deliverymode.deliverymodeid','receivedmode.name','deliverymode.name',
                'applicantcategory.applicantcategoryid','applicantcategory.name','wfinstanceid','wfengine','wfmetadata','ministryRequests')
    