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
    
    #ForeignKey References       
    foiministryrequest_id =db.Column(db.Integer, db.ForeignKey('FOIMinistryRequests.foiministryrequestid'))
    foiministryrequestversion_id=db.Column(db.Integer, db.ForeignKey('FOIMinistryRequests.version'))

    attachments = relationship('FOIApplicantCorrespondenceAttachment', backref=backref("FOIApplicantCorrespondenceAttachments"))
    
    @classmethod
    def getapplicantcorrespondences(cls,ministryrequestid):
        comment_schema = FOIApplicantCorrespondenceSchema(many=True)
        query = db.session.query(FOIApplicantCorrespondence).filter(FOIApplicantCorrespondence.foiministryrequest_id == ministryrequestid).order_by(FOIApplicantCorrespondence.applicantcorrespondenceid.desc()).all()
        return comment_schema.dump(query)
    
    @classmethod
    def getapplicantcorrespondencebyid(cls,applicantcorrespondenceid):
        correspondence_schema = FOIApplicantCorrespondenceSchema()
        query = db.session.query(FOIApplicantCorrespondence).filter(FOIApplicantCorrespondence.applicantcorrespondenceid == applicantcorrespondenceid).first()
        return correspondence_schema.dump(query)
    
    @classmethod
    def getlatestapplicantcorrespondence(cls,ministryrequestid):
        correspondence_schema = FOIApplicantCorrespondenceSchema()
        query = db.session.query(FOIApplicantCorrespondence).filter(FOIApplicantCorrespondence.foiministryrequest_id == ministryrequestid, FOIApplicantCorrespondence.createdby != 'System Generated Email').order_by(FOIApplicantCorrespondence.applicantcorrespondenceid.desc()).first()
        return correspondence_schema.dump(query)

    @classmethod
    def saveapplicantcorrespondence(cls, newapplicantcorrepondencelog,attachments,emails)->DefaultMethodResult: 
        db.session.add(newapplicantcorrepondencelog)
        db.session.commit()
        try:
            if(attachments is not None and len(attachments) > 0):
                for _attachment in attachments:
                    attachment = FOIApplicantCorrespondenceAttachment()
                    attachment.applicantcorrespondenceid = newapplicantcorrepondencelog.applicantcorrespondenceid
                    attachment.attachmentdocumenturipath = _attachment['url']
                    attachment.attachmentfilename = _attachment['filename']
                    attachment.createdby = newapplicantcorrepondencelog.createdby
                    FOIApplicantCorrespondenceAttachment().saveapplicantcorrespondenceattachment(attachment)
            if(emails is not None and len(emails) > 0):
                correspondenceemails = []
                for _email in emails:
                    print(_email)
                    email = FOIApplicantCorrespondenceEmail()
                    email.applicantcorrespondenceid = newapplicantcorrepondencelog.applicantcorrespondenceid
                    email.correspondence_to = _email
                    email.createdby = newapplicantcorrepondencelog.createdby
                    correspondenceemails.append(email)
                print(correspondenceemails)
                FOIApplicantCorrespondenceEmail().saveapplicantcorrespondenceemail(newapplicantcorrepondencelog.applicantcorrespondenceid , correspondenceemails)
            
        except Exception:
            return DefaultMethodResult(False,'applicantcorrepondence log exception while adding attachments',newapplicantcorrepondencelog.applicantcorrespondenceid)

        return DefaultMethodResult(True,'applicantcorrepondence log added',newapplicantcorrepondencelog.applicantcorrespondenceid)    


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

class FOIApplicantCorrespondenceSchema(ma.Schema):
    class Meta:
        fields = ('applicantcorrespondenceid','parentapplicantcorrespondenceid', 'templateid','correspondencemessagejson','foiministryrequest_id','foiministryrequestversion_id','created_at','createdby','attachments','sentcorrespondencemessage','sent_at','sentby')
    