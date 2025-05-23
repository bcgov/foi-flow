from sqlalchemy.sql.schema import ForeignKeyConstraint
from .db import  db, ma
from datetime import datetime
from .default_method_result import DefaultMethodResult
from sqlalchemy import text
from .FOIApplicantCorrespondenceAttachmentsRawRequests import FOIApplicantCorrespondenceAttachmentRawRequest
from .FOIApplicantCorrespondenceEmailsRawRequests import FOIApplicantCorrespondenceEmailRawRequest
from sqlalchemy.dialects.postgresql import JSON
import logging
class FOIApplicantCorrespondenceRawRequest(db.Model):
    # Name of the table in our database
    __tablename__ = 'FOIApplicantCorrespondencesRawRequests'
    __table_args__ = (
        ForeignKeyConstraint(
            ["foirawrequest_id", "foirawrequestversion_id"], ["FOIRawRequests.requestid", "FOIRawRequests.version"]
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
    
    #ForeignKey References       
    foirawrequest_id =db.Column(db.Integer, db.ForeignKey('FOIRawRequests.requestid'))
    foirawrequestversion_id=db.Column(db.Integer, db.ForeignKey('FOIRawRequests.version'))
    
    @classmethod
    def getapplicantcorrespondencesrawrequests(cls, requestid):
        correspondences = []
        try:
            sql = """select distinct on (applicantcorrespondenceid) applicantcorrespondenceid, templateid , correspondencemessagejson , version, 
                        created_at, createdby, sentcorrespondencemessage, parentapplicantcorrespondenceid, sentby, sent_at,
                         isdraft, isdeleted, isresponse, response_at, israwrequest
                         from "FOIApplicantCorrespondencesRawRequests" rawcorr 
                        where 
                            foirawrequest_id = :requestid
                    order by applicantcorrespondenceid desc, version desc""" 
            rs = db.session.execute(text(sql), {'requestid': requestid})
            for row in rs:
                if row["isdeleted"] == False:
                    correspondences.append({"applicantcorrespondenceid": row["applicantcorrespondenceid"], "templateid": row["templateid"],
                                            "correspondencemessagejson": row["correspondencemessagejson"], "version": row["version"], 
                                            "created_at": row["created_at"], "createdby": row["createdby"], 
                                            "sentcorrespondencemessage": row["sentcorrespondencemessage"], "parentapplicantcorrespondenceid": row["parentapplicantcorrespondenceid"],
                                            "sent_at": row["sent_at"], "sentby": row["sentby"],
                                            "isdraft": row["isdraft"], "isresponse": row["isresponse"], "response_at": row["response_at"], "israwrequest": row["israwrequest"]})
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return correspondences
    
    @classmethod
    def getapplicantcorrespondencebyid(cls,applicantcorrespondenceid):
        correspondence_schema = FOIApplicantCorrespondenceRawRequestSchema()
        query = db.session.query(FOIApplicantCorrespondenceRawRequest).filter(FOIApplicantCorrespondenceRawRequest.applicantcorrespondenceid == applicantcorrespondenceid).order_by(FOIApplicantCorrespondenceRawRequest.version.desc()).first()
        return correspondence_schema.dump(query)

    @classmethod
    def saveapplicantcorrespondence(cls, newapplicantcorrepondencelog, attachments, emails)->DefaultMethodResult: 
        try:
            db.session.add(newapplicantcorrepondencelog)
            db.session.commit()
            if(attachments is not None and len(attachments) > 0):
                correpondenceattachments = []
                for _attachment in attachments:
                    attachment = FOIApplicantCorrespondenceAttachmentRawRequest()
                    attachment.applicantcorrespondenceid = newapplicantcorrepondencelog.applicantcorrespondenceid
                    attachment.applicantcorrespondence_version = newapplicantcorrepondencelog.version
                    attachment.attachmentdocumenturipath = _attachment['url']
                    attachment.attachmentfilename = _attachment['filename']
                    attachment.createdby = newapplicantcorrepondencelog.createdby
                    attachment.version = 1
                    correpondenceattachments.append(attachment)
                FOIApplicantCorrespondenceAttachmentRawRequest().saveapplicantcorrespondenceattachments(newapplicantcorrepondencelog.foirawrequest_id , correpondenceattachments)
            if(emails is not None and len(emails) > 0):
                correspondenceemails = []
                for _email in emails:
                    email = FOIApplicantCorrespondenceEmailRawRequest()
                    email.applicantcorrespondence_id = newapplicantcorrepondencelog.applicantcorrespondenceid
                    email.applicantcorrespondence_version = newapplicantcorrepondencelog.version
                    email.correspondence_to = _email
                    email.createdby = newapplicantcorrepondencelog.createdby
                    correspondenceemails.append(email)
                FOIApplicantCorrespondenceEmailRawRequest().saveapplicantcorrespondenceemail(newapplicantcorrepondencelog.applicantcorrespondenceid , correspondenceemails)
            return DefaultMethodResult(True,'applicantcorrepondence log added',newapplicantcorrepondencelog.applicantcorrespondenceid)
        except Exception as e:
            print('EXCEPTION: ')
            print(e)
            return DefaultMethodResult(False,'applicantcorrepondence log exception while adding attachments',newapplicantcorrepondencelog.applicantcorrespondenceid)
        finally:
            db.session.close()
            


    @classmethod
    def deleteapplicantcorrespondence(cls, rawrequestid, correspondenceid,userid)->DefaultMethodResult: 
        correspondence = FOIApplicantCorrespondenceRawRequest.getapplicantcorrespondencebyid(correspondenceid)
        try:
            db.session.query(FOIApplicantCorrespondenceRawRequest).filter(FOIApplicantCorrespondenceRawRequest.foirawrequest_id == rawrequestid, 
                            FOIApplicantCorrespondenceRawRequest.applicantcorrespondenceid == correspondenceid, FOIApplicantCorrespondenceRawRequest.version == correspondence.get('version')
                            ).update({FOIApplicantCorrespondenceRawRequest.isdeleted: True, FOIApplicantCorrespondenceRawRequest.updatedby: userid,
                            FOIApplicantCorrespondenceRawRequest.updated_at: datetime.now()}, synchronize_session=False)
            db.session.commit()  
            return DefaultMethodResult(True,'Correspondence deleted ', correspondenceid)
        except:
            db.session.rollback()
            raise   
        finally:
            db.session.close()

#     @classmethod
#     def updatesentcorrespondence(cls, applicantcorrespondenceid, content)->DefaultMethodResult: 
#         dbquery = db.session.query(FOIApplicantCorrespondence)
#         _correspondence = dbquery.filter_by(applicantcorrespondenceid=applicantcorrespondenceid)
#         if(_correspondence.count() > 0) :
#             _correspondence.update({FOIApplicantCorrespondence.sentcorrespondencemessage:content, FOIApplicantCorrespondence.sent_at:datetime.now(), FOIApplicantCorrespondence.sentby:"System Generated Email"}, synchronize_session = False)
#             db.session.commit()
#             return DefaultMethodResult(True,'Applicant correspondence updated for Id',applicantcorrespondenceid)
#         else:
#             return DefaultMethodResult(False,'Applicant correspondence not exists',-1)        

class FOIApplicantCorrespondenceRawRequestSchema(ma.Schema):
    class Meta:
        fields = ('applicantcorrespondenceid', 'version', 'parentapplicantcorrespondenceid', 'templateid','correspondencemessagejson','foirawrequest_id','foirawrequestversion_id','created_at','createdby','attachments','sentcorrespondencemessage','sent_at','sentby', 'isdraft', 'isdeleted', 'isresponse', 'response_at', 'israwrequest')
    