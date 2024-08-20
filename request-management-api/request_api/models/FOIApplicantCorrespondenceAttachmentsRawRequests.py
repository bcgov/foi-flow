from sqlalchemy.sql.schema import ForeignKeyConstraint
from .db import  db, ma
from datetime import datetime
from .default_method_result import DefaultMethodResult
from sqlalchemy import text
import logging

class FOIApplicantCorrespondenceAttachmentRawRequest(db.Model):
    # Name of the table in our database
    __tablename__ = 'FOIApplicantCorrespondenceAttachmentsRawRequests'
    __table_args__ = (
        ForeignKeyConstraint(
            ["applicantcorrespondenceid","applicantcorrespondence_version"], ["FOIApplicantCorrespondencesRawRequests.applicantcorrespondenceid", "FOIApplicantCorrespondencesRawRequests.version"],
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
                 
    applicantcorrespondenceid =db.Column(db.Integer, db.ForeignKey('FOIApplicantCorrespondencesRawRequests.applicantcorrespondenceid'))
    applicantcorrespondence_version = db.Column(db.Integer, db.ForeignKey('FOIApplicantCorrespondencesRawRequests.version')) 


    @classmethod
    def saveapplicantcorrespondenceattachment(cls, newapplicantcorrepondenceattachment)->DefaultMethodResult: 
        db.session.add(newapplicantcorrepondenceattachment)
        db.session.commit()               
        return DefaultMethodResult(True,'applicant correpondence attachment added',newapplicantcorrepondenceattachment.applicantcorrespondenceattachmentid)    

    @classmethod
    def saveapplicantcorrespondenceattachments(cls, requestid, newapplicantcorrepondenceattachments)->DefaultMethodResult: 
        db.session.add_all(newapplicantcorrepondenceattachments)
        db.session.commit()               
        return DefaultMethodResult(True,'applicant correpondence attachment added',requestid)    

    @classmethod
    def getapplicantcorrespondenceattachmentbyid(cls, attachmentid):
        correspondenceattachment_schema = FOIApplicantCorrespondenceAttachmentRawRequestSchema()
        query = db.session.query(FOIApplicantCorrespondenceAttachmentRawRequest).filter(FOIApplicantCorrespondenceAttachmentRawRequest.applicantcorrespondenceattachmentid == attachmentid).order_by(FOIApplicantCorrespondenceAttachmentRawRequest.version.desc()).first()
        return correspondenceattachment_schema.dump(query)


    @classmethod
    def getapplicantcorrespondenceattachmentsbyapplicantcorrespondenceid(cls,applicantcorrespondenceid):
        correspondenceattachment_schema = FOIApplicantCorrespondenceAttachmentRawRequestSchema(many=True)
        query = db.session.query(FOIApplicantCorrespondenceAttachmentRawRequest).filter(FOIApplicantCorrespondenceAttachmentRawRequest.applicantcorrespondenceid == applicantcorrespondenceid).order_by(FOIApplicantCorrespondenceAttachmentRawRequest.applicantcorrespondenceattachmentid.asc()).all()
        return correspondenceattachment_schema.dump(query)
    
    @classmethod
    def getcorrespondenceattachmentbyapplicantcorrespondenceid(cls,applicantcorrespondenceid):
        correspondenceattachment_schema = FOIApplicantCorrespondenceAttachmentRawRequestSchema(many=False)
        query = db.session.query(FOIApplicantCorrespondenceAttachmentRawRequest).filter(FOIApplicantCorrespondenceAttachmentRawRequest.applicantcorrespondenceid == applicantcorrespondenceid).order_by(FOIApplicantCorrespondenceAttachmentRawRequest.version.desc()).first()
        return correspondenceattachment_schema.dump(query)
    
    @classmethod
    def getcorrespondenceattachmentsbyrawrequestid(cls,requestid):
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
                            "FOIApplicantCorrespondenceAttachmentsRawRequests" fca 
                        JOIN 
                            "FOIApplicantCorrespondencesRawRequests" fpa 
                        ON 
                            fpa.applicantcorrespondenceid = fca.applicantcorrespondenceid  
                            AND fca.applicantcorrespondence_version = fpa."version"
                        WHERE 
                            fpa.foirawrequest_id = :requestid
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
            rs = db.session.execute(text(sql), {'requestid': requestid})
            for row in rs:
                attachments.append({"applicantcorrespondenceid": row["applicantcorrespondenceid"], "applicantcorrespondence_version": row["applicantcorrespondence_version"],"applicantcorrespondenceattachmentid": row["applicantcorrespondenceattachmentid"], "attachmentfilename": row["attachmentfilename"], "attachmentdocumenturipath": row["attachmentdocumenturipath"], "version": row["version"]})
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return attachments

class FOIApplicantCorrespondenceAttachmentRawRequestSchema(ma.Schema):
    class Meta:
        fields = ('applicantcorrespondenceattachmentid', 'version','applicantcorrespondenceid','attachmentdocumenturipath','attachmentfilename','created_at','createdby', 'applicantcorrespondence_version')
    