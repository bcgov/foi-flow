from sqlalchemy.sql.schema import ForeignKeyConstraint
from .db import  db, ma
from datetime import datetime
from .default_method_result import DefaultMethodResult
from sqlalchemy import text
import logging

class FOIApplicantCorrespondenceEmailRawRequest(db.Model):
    # Name of the table in our database
    __tablename__ = 'FOIApplicantCorrespondenceEmailsRawRequests'
    __table_args__ = (
        ForeignKeyConstraint(
            ["applicantcorrespondence_id", "applicantcorrespondence_version"], ["FOIApplicantCorrespondencesRawRequests.applicantcorrespondenceid","FOIApplicantCorrespondencesRawRequests.version"],
        ),
    )
        
    # Defining the columns
    applicantcorrespondenceemailid = db.Column(db.Integer, primary_key=True,autoincrement=True)  
    correspondence_to = db.Column(db.Text, unique=False, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=True)
    createdby = db.Column(db.String(120), unique=False, nullable=False)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)
                 
    applicantcorrespondence_id =db.Column(db.Integer, db.ForeignKey('FOIApplicantCorrespondences.applicantcorrespondenceid'))
    applicantcorrespondence_version = db.Column(db.Integer, db.ForeignKey('FOIApplicantCorrespondences.version')) 


    @classmethod
    def saveapplicantcorrespondenceemail(cls, applicantcorrespondenceid, correspondenceemails)->DefaultMethodResult: 
        db.session.add_all(correspondenceemails)
        db.session.commit()            
        return DefaultMethodResult(True,'applicant correpondence emails are added', applicantcorrespondenceid)    

    @classmethod
    def getapplicantcorrespondenceemails(cls,requestid):
        correspondence_emails = []
        try:
            sql = """select correspondence_to, 
                        applicantcorrespondence_id, applicantcorrespondence_version  from "FOIApplicantCorrespondenceEmailsRawRequests" fce join "FOIApplicantCorrespondencesRawRequests" fc 
                        on fce.applicantcorrespondence_id  = fc.applicantcorrespondenceid and fce.applicantcorrespondence_version = fc."version" 
                        where fc.foirawrequest_id = :requestid;""" 
            rs = db.session.execute(text(sql), {'requestid': requestid})
            for row in rs:
                correspondence_emails.append({"correspondence_to": row["correspondence_to"], "applicantcorrespondence_id": row["applicantcorrespondence_id"],
                                            "applicantcorrespondence_version": row["applicantcorrespondence_version"]})
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return correspondence_emails
    
class FOIApplicantCorrespondenceEmailRawRequestSchema(ma.Schema):
    class Meta:
        fields = ('applicantcorrespondenceemailid','applicantcorrespondence_id', 'applicantcorrespondence_version','correspondence_to','created_at','createdby')
    