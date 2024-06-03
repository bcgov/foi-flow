from flask.app import Flask
from sqlalchemy.sql.schema import ForeignKey, ForeignKeyConstraint
from .db import  db, ma
from datetime import datetime
from sqlalchemy.orm import relationship,backref
from .default_method_result import DefaultMethodResult
from sqlalchemy.sql.expression import distinct
from sqlalchemy import or_,and_,text

class FOIApplicantCorrespondenceEmail(db.Model):
    # Name of the table in our database
    __tablename__ = 'FOIApplicantCorrespondenceEmails'
    __table_args__ = (
        ForeignKeyConstraint(
            ["applicantcorrespondenceid"], ["FOIApplicantCorrespondences.applicantcorrespondenceid"],
        ),
    )
        
    # Defining the columns
    applicantcorrespondenceemailid = db.Column(db.Integer, primary_key=True,autoincrement=True)      
    correspondence_to = db.Column(db.Text, unique=False, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=True)
    createdby = db.Column(db.String(120), unique=False, nullable=False)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)
                 
    applicantcorrespondenceid =db.Column(db.Integer, db.ForeignKey('FOIApplicantCorrespondences.applicantcorrespondenceid'))
    


    @classmethod
    def saveapplicantcorrespondenceemail(cls, applicantcorrespondenceid, correspondenceemails)->DefaultMethodResult: 
        db.session.add_all(correspondenceemails)
        db.session.commit()            
        return DefaultMethodResult(True,'applicant correpondence emails are added', applicantcorrespondenceid)    

    
class FOIApplicantCorrespondenceEmailSchema(ma.Schema):
    class Meta:
        fields = ('applicantcorrespondenceemailid','applicantcorrespondenceid', 'email','created_at','createdby')
    