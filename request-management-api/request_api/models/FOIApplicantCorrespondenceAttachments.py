from flask.app import Flask
from sqlalchemy.sql.schema import ForeignKey, ForeignKeyConstraint
from .db import  db, ma
from datetime import datetime
from sqlalchemy.orm import relationship,backref
from .default_method_result import DefaultMethodResult
from sqlalchemy.sql.expression import distinct
from sqlalchemy import or_,and_,text
import logging

class FOIApplicantCorrespondenceAttachment(db.Model):
    # Name of the table in our database
    __tablename__ = 'FOIApplicantCorrespondenceAttachments'
    __table_args__ = (
        ForeignKeyConstraint(
            ["applicantcorrespondenceid","applicantcorrespondence_version"], ["FOIApplicantCorrespondences.applicantcorrespondenceid", "FOIApplicantCorrespondences.version"],
        ),
    )
        
    # Defining the columns
    applicantcorrespondenceattachmentid = db.Column(db.Integer, primary_key=True,autoincrement=True)      
    version = db.Column(db.Integer, primary_key=True,nullable=False)
    attachmentdocumenturipath = db.Column(db.Text, unique=False, nullable=False)
    attachmentfilename = db.Column(db.String(500), unique=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=True)
    createdby = db.Column(db.String(120), unique=False, nullable=False)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)
                 
    applicantcorrespondenceid =db.Column(db.Integer, db.ForeignKey('FOIApplicantCorrespondences.applicantcorrespondenceid'))
    applicantcorrespondence_version = db.Column(db.Integer, db.ForeignKey('FOIApplicantCorrespondences.version')) 


    @classmethod
    def saveapplicantcorrespondenceattachment(cls, newapplicantcorrepondenceattachment)->DefaultMethodResult: 
        db.session.add(newapplicantcorrepondenceattachment)
        db.session.commit()               
        return DefaultMethodResult(True,'applicant correpondence attachment added',newapplicantcorrepondenceattachment.applicantcorrespondenceattachmentid)    

    @classmethod
    def saveapplicantcorrespondenceattachments(cls, ministryid, newapplicantcorrepondenceattachments)->DefaultMethodResult: 
        db.session.add_all(newapplicantcorrepondenceattachments)
        db.session.commit()               
        return DefaultMethodResult(True,'applicant correpondence attachment added',ministryid)    

    @classmethod
    def getapplicantcorrespondenceattachmentbyid(cls, attachmentid):
        correspondenceattachment_schema = FOIApplicantCorrespondenceAttachmentSchema()
        query = db.session.query(FOIApplicantCorrespondenceAttachment).filter(FOIApplicantCorrespondenceAttachment.applicantcorrespondenceattachmentid == attachmentid).order_by(FOIApplicantCorrespondenceAttachment.version.desc()).first()
        return correspondenceattachment_schema.dump(query)


    @classmethod
    def getapplicantcorrespondenceattachmentsbyapplicantcorrespondenceid(cls,applicantcorrespondenceid):
        correspondenceattachment_schema = FOIApplicantCorrespondenceAttachmentSchema(many=True)
        query = db.session.query(FOIApplicantCorrespondenceAttachment).filter(FOIApplicantCorrespondenceAttachment.applicantcorrespondenceid == applicantcorrespondenceid).order_by(FOIApplicantCorrespondenceAttachment.applicantcorrespondenceattachmentid.asc()).all()
        return correspondenceattachment_schema.dump(query)
    
    @classmethod
    def getcorrespondenceattachmentsbyministryid(cls,ministryrequestid):
        attachments = []
        try:
            # select on the highest version of each attachment
            sql = """
                    WITH RankedCorrespondences AS (
                        SELECT 
                            fca.applicantcorrespondenceid, 
                            fca.applicantcorrespondence_version, 
                            fca.applicantcorrespondenceattachmentid, 
                            attachmentfilename, 
                            attachmentdocumenturipath, 
                            fca.version,
                            ROW_NUMBER() OVER (PARTITION BY fca.applicantcorrespondenceid, fca.applicantcorrespondence_version, fca.applicantcorrespondenceattachmentid ORDER BY fca.version DESC) AS rn
                        FROM 
                            "FOIApplicantCorrespondenceAttachments" fca 
                        JOIN 
                            "FOIApplicantCorrespondences" fpa 
                        ON 
                            fpa.applicantcorrespondenceid = fca.applicantcorrespondenceid  
                            AND fca.applicantcorrespondence_version = fpa."version"
                        WHERE 
                            fpa.foiministryrequest_id = :ministryrequestid
                    )
                    SELECT 
                        applicantcorrespondenceid, 
                        applicantcorrespondence_version, 
                        applicantcorrespondenceattachmentid, 
                        attachmentfilename, 
                        attachmentdocumenturipath, 
                        version
                    FROM 
                        RankedCorrespondences
                    WHERE 
                        rn = 1
                    ORDER BY 
                        applicantcorrespondenceid DESC, 
                        applicantcorrespondence_version DESC;"""
            rs = db.session.execute(text(sql), {'ministryrequestid': ministryrequestid})
            for row in rs:
                attachments.append({"applicantcorrespondenceid": row["applicantcorrespondenceid"], "applicantcorrespondence_version": row["applicantcorrespondence_version"],"applicantcorrespondenceattachmentid": row["applicantcorrespondenceattachmentid"], "attachmentfilename": row["attachmentfilename"], "attachmentdocumenturipath": row["attachmentdocumenturipath"], "version": row["version"]})
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return attachments

    # response attachments require a different query
    @classmethod
    def getcorrespondenceresponseattachmentbyministryid(cls, ministryrequestid):
        attachments = []
        try:
            sql = """SELECT DISTINCT ON (fca.applicantcorrespondenceid) 
                        fca.applicantcorrespondenceid, 
                        fca.applicantcorrespondence_version, 
                        fca.applicantcorrespondenceattachmentid, 
                        fca.attachmentfilename, 
                        fca.attachmentdocumenturipath, 
                        fca.version
                    FROM "FOIApplicantCorrespondenceAttachments" fca 
                    JOIN "FOIApplicantCorrespondences" fpa 
                        ON fpa.applicantcorrespondenceid = fca.applicantcorrespondenceid  
                        AND fca.applicantcorrespondence_version = fpa."version"
                    WHERE fpa.foiministryrequest_id = :ministryrequestid
                    ORDER BY fca.applicantcorrespondenceid, fca.applicantcorrespondence_version DESC, fca.version DESC;
                    """ 
            rs = db.session.execute(text(sql), {'ministryrequestid': ministryrequestid})
            for row in rs:
                attachments.append({"applicantcorrespondenceid": row["applicantcorrespondenceid"], "applicantcorrespondence_version": row["applicantcorrespondence_version"],"applicantcorrespondenceattachmentid": row["applicantcorrespondenceattachmentid"], "attachmentfilename": row["attachmentfilename"], "attachmentdocumenturipath": row["attachmentdocumenturipath"]})
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return attachments

class FOIApplicantCorrespondenceAttachmentSchema(ma.Schema):
    class Meta:
        fields = ('applicantcorrespondenceattachmentid', 'version','applicantcorrespondenceid','attachmentdocumenturipath','attachmentfilename','created_at','createdby', 'applicantcorrespondence_version')
    