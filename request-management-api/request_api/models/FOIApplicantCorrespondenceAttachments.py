from flask.app import Flask
from sqlalchemy.sql.schema import ForeignKey, ForeignKeyConstraint
from .db import  db, ma
from datetime import datetime
from sqlalchemy.orm import relationship,backref
from .default_method_result import DefaultMethodResult
from sqlalchemy.sql.expression import distinct
from sqlalchemy import or_,and_,text

class FOIApplicantCorrespondenceAttachment(db.Model):
    # Name of the table in our database
    __tablename__ = 'FOIApplicantCorrespondenceAttachments'
    __table_args__ = (
        ForeignKeyConstraint(
            ["applicantcorrespondenceid"], ["FOIApplicantCorrespondences.applicantcorrespondenceid"]
        ),
    )
        
    # Defining the columns
    applicantcorrespondenceattachmentid = db.Column(db.Integer, primary_key=True,autoincrement=True)      
    attachmentdocumenturipath = db.Column(db.Text, unique=False, nullable=False)
    attachmentfilename = db.Column(db.String(500), unique=False, nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=True)
    createdby = db.Column(db.String(120), unique=False, nullable=False)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)
                 
    applicantcorrespondenceid =db.Column(db.Integer, db.ForeignKey('FOIApplicantCorrespondences.applicantcorrespondenceid'))
    



    @classmethod
    def saveapplicantcorrespondenceattachment(cls, newapplicantcorrepondenceattachment)->DefaultMethodResult: 
        
        db.session.add(newapplicantcorrepondenceattachment)
        db.session.commit()               
        return DefaultMethodResult(True,'applicant correpondence attachment added',newapplicantcorrepondenceattachment.applicantcorrespondenceattachmentid)    

    
class FOIApplicantCorrespondenceAttachmentSchema(ma.Schema):
    class Meta:
        fields = ('applicantcorrespondenceattachmentid','applicantcorrespondenceid', 'attachmentdocumenturipath','attachmentfilename','created_at','createdby')
    