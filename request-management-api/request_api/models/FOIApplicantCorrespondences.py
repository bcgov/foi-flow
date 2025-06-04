from flask.app import Flask
from sqlalchemy.sql.schema import ForeignKey, ForeignKeyConstraint
from .db import  db, ma
from datetime import datetime
from sqlalchemy.orm import relationship,backref
from .default_method_result import DefaultMethodResult
from sqlalchemy.sql.expression import distinct
from sqlalchemy import or_,and_,text
from .FOIApplicantCorrespondenceAttachments import FOIApplicantCorrespondenceAttachment
from .FOIApplicantCorrespondenceEmails import FOIApplicantCorrespondenceEmail
from sqlalchemy.dialects.postgresql import JSON, UUID
import logging
class FOIApplicantCorrespondence(db.Model):
    # Name of the table in our database
    __tablename__ = 'FOIApplicantCorrespondences'
    __table_args__ = (
        ForeignKeyConstraint(
            ["foiministryrequest_id", "foiministryrequestversion_id"], ["FOIMinistryRequests.foiministryrequestid", "FOIMinistryRequests.version"]
        ),
    )
        
    # Defining the columns
    applicantcorrespondenceid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    version = db.Column(db.Integer, primary_key=True,nullable=False)
    parentapplicantcorrespondenceid = db.Column(db.Integer)
    templateid = db.Column(db.Integer, nullable=True)
    correspondencemessagejson = db.Column(db.Text, unique=False, nullable=True)

    sentcorrespondencemessage = db.Column(JSON, unique=False, nullable=True)
    sent_at = db.Column(db.DateTime, nullable=True)
    sentby = db.Column(db.String(120), unique=False, nullable=True)
   
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=True)
    createdby = db.Column(db.String(120), unique=False, nullable=False)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)
    
    isdraft = db.Column(db.Boolean, default=False, nullable=True)
    isdeleted = db.Column(db.Boolean, default=False, nullable=True)
    isresponse = db.Column(db.Boolean, default=False, nullable=True)
    response_at = db.Column(db.DateTime, nullable=True)

    templatename = db.Column(db.String(255), unique=False, nullable=True)
    templatetype = db.Column(db.String(120), unique=False, nullable=True)
    
    #ForeignKey References       
    foiministryrequest_id =db.Column(db.Integer, db.ForeignKey('FOIMinistryRequests.foiministryrequestid'))
    foiministryrequestversion_id=db.Column(db.Integer, db.ForeignKey('FOIMinistryRequests.version'))

    
    @classmethod
    def getapplicantcorrespondences(cls,ministryrequestid):
        correspondences = []
        try:
            sql = """select distinct on (applicantcorrespondenceid) applicantcorrespondenceid, templateid , correspondencemessagejson , version, 
                        created_at, createdby, sentcorrespondencemessage, parentapplicantcorrespondenceid, sentby, sent_at,
                         isdraft, isdeleted, isresponse, response_at, templatename, templatetype
                         from "FOIApplicantCorrespondences" fpa 
                        where foiministryrequest_id = :ministryrequestid
                    order by applicantcorrespondenceid desc, version desc""" 
            rs = db.session.execute(text(sql), {'ministryrequestid': ministryrequestid})
            for row in rs:
                if row["isdeleted"] == False:
                    correspondences.append({"applicantcorrespondenceid": row["applicantcorrespondenceid"], "templateid": row["templateid"],
                                            "correspondencemessagejson": row["correspondencemessagejson"], "version": row["version"], 
                                            "created_at": row["created_at"], "createdby": row["createdby"], 
                                            "sentcorrespondencemessage": row["sentcorrespondencemessage"], "parentapplicantcorrespondenceid": row["parentapplicantcorrespondenceid"],
                                            "sent_at": row["sent_at"], "sentby": row["sentby"],
                                            "isdraft": row["isdraft"], "isresponse": row["isresponse"], "response_at": row["response_at"],
                                            "templatename": row["templatename"], "templatetype": row["templatetype"]})
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return correspondences
    
    @classmethod
    def getapplicantcorrespondencebyid(cls,applicantcorrespondenceid):
        correspondence_schema = FOIApplicantCorrespondenceSchema()
        query = db.session.query(FOIApplicantCorrespondence).filter(FOIApplicantCorrespondence.applicantcorrespondenceid == applicantcorrespondenceid).order_by(FOIApplicantCorrespondence.version.desc()).first()
        return correspondence_schema.dump(query)
    
    @classmethod
    def getlatestapplicantcorrespondence(cls,ministryrequestid):
        correspondence_schema = FOIApplicantCorrespondenceSchema()
        query = db.session.query(FOIApplicantCorrespondence).filter(FOIApplicantCorrespondence.foiministryrequest_id == ministryrequestid, FOIApplicantCorrespondence.createdby != 'System Generated Email').order_by(FOIApplicantCorrespondence.applicantcorrespondenceid.desc()).first()
        return correspondence_schema.dump(query)

    @classmethod
    def saveapplicantcorrespondence(cls, newapplicantcorrepondencelog, attachments, emails = None, ccemails = None)->DefaultMethodResult: 
        try:
            db.session.add(newapplicantcorrepondencelog)
            db.session.commit()
            if(attachments is not None and len(attachments) > 0):
                correpondenceattachments = []
                for _attachment in attachments:
                    attachment = FOIApplicantCorrespondenceAttachment()
                    if 'applicantcorrespondenceattachmentid' in _attachment:
                        existingattachment = FOIApplicantCorrespondenceAttachment().getapplicantcorrespondenceattachmentbyid(_attachment['applicantcorrespondenceattachmentid'])
                        attachment.applicantcorrespondenceid = newapplicantcorrepondencelog.applicantcorrespondenceid
                        attachment.applicantcorrespondence_version = newapplicantcorrepondencelog.version
                        attachment.attachmentdocumenturipath = existingattachment['attachmentdocumenturipath']
                        attachment.attachmentfilename = existingattachment['attachmentfilename']
                        attachment.createdby = existingattachment['createdby']
                        attachment.version = existingattachment['version'] + 1
                    else:
                        attachment.applicantcorrespondenceid = newapplicantcorrepondencelog.applicantcorrespondenceid
                        attachment.applicantcorrespondence_version = newapplicantcorrepondencelog.version
                        attachment.attachmentdocumenturipath = _attachment['url']
                        attachment.attachmentfilename = _attachment['filename']
                        attachment.createdby = newapplicantcorrepondencelog.createdby
                        attachment.version = 1
                    correpondenceattachments.append(attachment)
                FOIApplicantCorrespondenceAttachment().saveapplicantcorrespondenceattachments(newapplicantcorrepondencelog.foiministryrequest_id , correpondenceattachments)
            correspondenceemails = []
            if(emails is not None and len(emails) > 0):
                for _email in emails:
                    email = FOIApplicantCorrespondenceEmail()
                    email.applicantcorrespondence_id = newapplicantcorrepondencelog.applicantcorrespondenceid
                    email.applicantcorrespondence_version = newapplicantcorrepondencelog.version
                    email.correspondence_to = _email
                    email.createdby = newapplicantcorrepondencelog.createdby
                    email.iscarboncopy = False
                    correspondenceemails.append(email)
            if(ccemails is not None and len(ccemails) > 0):
                for _email in ccemails:
                    email = FOIApplicantCorrespondenceEmail()
                    email.applicantcorrespondence_id = newapplicantcorrepondencelog.applicantcorrespondenceid
                    email.applicantcorrespondence_version = newapplicantcorrepondencelog.version
                    email.correspondence_to = _email
                    email.createdby = newapplicantcorrepondencelog.createdby
                    email.iscarboncopy = True
                    correspondenceemails.append(email)
            if len(correspondenceemails) > 0:
                FOIApplicantCorrespondenceEmail().saveapplicantcorrespondenceemail(newapplicantcorrepondencelog.applicantcorrespondenceid , correspondenceemails)
            return DefaultMethodResult(True,'applicantcorrepondence log added',newapplicantcorrepondencelog.applicantcorrespondenceid)
        except Exception:
            return DefaultMethodResult(False,'applicantcorrepondence log exception while adding attachments',newapplicantcorrepondencelog.applicantcorrespondenceid)
        finally:
            db.session.close()
            

    @classmethod
    def updateapplicantcorrespondence(cls, ministryrequestid, updated_correspondencelog, userid)->DefaultMethodResult: 
        try:
            db.session.add(updated_correspondencelog)
            updatedcorrespondencelogid = updated_correspondencelog.applicantcorrespondenceid
            updatedcorrespondenceversion = updated_correspondencelog.version
            updatedcorrespondenceministryrequestid = updated_correspondencelog.foiministryrequest_id
            db.session.commit()
            
            # Update attachments to match new correspondence version
            attachments = FOIApplicantCorrespondenceAttachment().getapplicantcorrespondenceattachmentsbyapplicantcorrespondenceid(updatedcorrespondencelogid)
            if(attachments is not None and len(attachments) > 0):
                correpondenceattachments = []
                for _attachment in attachments:
                    attachment = FOIApplicantCorrespondenceAttachment()
                    attachment.__dict__.update(_attachment)
                    attachment.applicantcorrespondenceid = updatedcorrespondencelogid
                    attachment.applicantcorrespondence_version = updatedcorrespondenceversion
                    attachment.createdby = userid
                    attachment.version = _attachment['version'] + 1
                    correpondenceattachments.append(attachment)
                FOIApplicantCorrespondenceAttachment().saveapplicantcorrespondenceattachments(updatedcorrespondenceministryrequestid , correpondenceattachments)
            
            # Update emails to match new correspondence version 
            emails = FOIApplicantCorrespondenceEmail().getapplicantcorrespondenceemails(ministryrequestid)
            emailsbycorrespondence = cls.__getemailsincorrespondence(cls, emails, updatedcorrespondencelogid, updatedcorrespondenceversion - 1)
            correspondenceemails = []
            if(emailsbycorrespondence is not None and len(emailsbycorrespondence) > 0):
                for _email in emailsbycorrespondence:
                    email = FOIApplicantCorrespondenceEmail()
                    email.__dict__.update(_email)
                    email.applicantcorrespondence_id = updatedcorrespondencelogid
                    email.applicantcorrespondence_version = updatedcorrespondenceversion
                    correspondenceemails.append(email)
                FOIApplicantCorrespondenceEmail().saveapplicantcorrespondenceemail(updatedcorrespondencelogid , correspondenceemails)
            return DefaultMethodResult(True,'applicantcorrepondence log added',updatedcorrespondencelogid)
        except Exception as e:
            print('EXCEPTION: ')
            print(e)
            return DefaultMethodResult(False,'applicantcorrepondence log exception while updating correspondence',updatedcorrespondencelogid)
        finally:
            db.session.close()


    @classmethod
    def deleteapplicantcorrespondence(cls, ministryid, correspondenceid,userid)->DefaultMethodResult: 
        correspondence = FOIApplicantCorrespondence.getapplicantcorrespondencebyid(correspondenceid)
        try:
            db.session.query(FOIApplicantCorrespondence).filter(FOIApplicantCorrespondence.foiministryrequest_id == ministryid, 
                            FOIApplicantCorrespondence.applicantcorrespondenceid == correspondenceid, FOIApplicantCorrespondence.version == correspondence.get('version')
                            ).update({FOIApplicantCorrespondence.isdeleted: True, FOIApplicantCorrespondence.updatedby: userid,
                            FOIApplicantCorrespondence.updated_at: datetime.now()}, synchronize_session=False)
            db.session.commit()  
            return DefaultMethodResult(True,'Correspondence deleted ', correspondenceid)
        except:
            db.session.rollback()
            raise   
        finally:
            db.session.close()

    @classmethod
    def updatesentcorrespondence(cls, applicantcorrespondenceid, content)->DefaultMethodResult: 
        dbquery = db.session.query(FOIApplicantCorrespondence)
        _correspondence = dbquery.filter_by(applicantcorrespondenceid=applicantcorrespondenceid)
        if(_correspondence.count() > 0) :
            _correspondence.update({FOIApplicantCorrespondence.sentcorrespondencemessage:content, FOIApplicantCorrespondence.sent_at:datetime.now(), FOIApplicantCorrespondence.sentby:"System Generated Email"}, synchronize_session = False)
            db.session.commit()
            return DefaultMethodResult(True,'Applicant correspondence updated for Id',applicantcorrespondenceid)
        else:
            return DefaultMethodResult(False,'Applicant correspondence not exists',-1)        
    
    def __getemailsincorrespondence(cls, emails, correspondenceid, correspondenceversion):
        return [x for x in emails if x['applicantcorrespondence_id'] == correspondenceid and x['applicantcorrespondence_version'] == correspondenceversion]

class FOIApplicantCorrespondenceSchema(ma.Schema):
    class Meta:
        fields = ('applicantcorrespondenceid', 'version', 'parentapplicantcorrespondenceid', 'templateid','correspondencemessagejson','foiministryrequest_id','foiministryrequestversion_id','created_at','createdby','attachments','sentcorrespondencemessage','sent_at','sentby', 'isdraft', 'isdeleted', 'isresponse', 'response_at', 'templatename', 'templatetype')