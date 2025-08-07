from flask.app import Flask
from sqlalchemy.sql.schema import ForeignKey, ForeignKeyConstraint
from .db import  db, ma
from datetime import datetime
from sqlalchemy.orm import relationship,backref
from .default_method_result import DefaultMethodResult
from sqlalchemy.sql.expression import distinct
from sqlalchemy import or_,and_,text
import logging

class FOIApplicantCorrespondenceEmail(db.Model):
    # Name of the table in our database
    __tablename__ = 'FOIApplicantCorrespondenceEmails'
    __table_args__ = (
        ForeignKeyConstraint(
            ["applicantcorrespondence_id", "applicantcorrespondence_version"], ["FOIApplicantCorrespondences.applicantcorrespondenceid","FOIApplicantCorrespondences.version"],
        ),
    )
        
    # Defining the columns
    applicantcorrespondenceemailid = db.Column(db.Integer, primary_key=True,autoincrement=True)  
    correspondence_to = db.Column(db.Text, unique=False, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=True)
    createdby = db.Column(db.String(120), unique=False, nullable=False)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)
    iscarboncopy = db.Column(db.Boolean(), unique=False, nullable=True)
                 
    applicantcorrespondence_id =db.Column(db.Integer, db.ForeignKey('FOIApplicantCorrespondences.applicantcorrespondenceid'))
    applicantcorrespondence_version = db.Column(db.Integer, db.ForeignKey('FOIApplicantCorrespondences.version')) 


    @classmethod
    def saveapplicantcorrespondenceemail(cls, applicantcorrespondenceid, correspondenceemails)->DefaultMethodResult: 
        db.session.add_all(correspondenceemails)
        db.session.commit()            
        return DefaultMethodResult(True,'applicant correpondence emails are added', applicantcorrespondenceid)    

    @classmethod
    def getapplicantcorrespondenceemails(cls,ministryrequestid):
        correspondence_emails = []
        try:
            sql = """select correspondence_to, iscarboncopy, 
                        applicantcorrespondence_id, applicantcorrespondence_version  from "FOIApplicantCorrespondenceEmails" fce join "FOIApplicantCorrespondences" fc 
                        on fce.applicantcorrespondence_id  = fc.applicantcorrespondenceid and fce.applicantcorrespondence_version = fc."version" 
                        where fc.foiministryrequest_id = :ministryrequestid;""" 
            rs = db.session.execute(text(sql), {'ministryrequestid': ministryrequestid})
            for row in rs:
                correspondence_emails.append({"correspondence_to": row["correspondence_to"], "iscarboncopy": row["iscarboncopy"], "applicantcorrespondence_id": row["applicantcorrespondence_id"],
                                            "applicantcorrespondence_version": row["applicantcorrespondence_version"]})
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return correspondence_emails
    
class FOIApplicantCorrespondenceEmailSchema(ma.Schema):
    class Meta:
        fields = ('applicantcorrespondenceemailid','applicantcorrespondence_id', 'applicantcorrespondence_version','correspondence_to','created_at','createdby', 'iscarboncopy')
    