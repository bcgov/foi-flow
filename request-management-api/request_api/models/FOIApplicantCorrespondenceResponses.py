from flask.app import Flask
from sqlalchemy.sql.schema import ForeignKey, ForeignKeyConstraint
from .db import  db, ma
from datetime import datetime
from sqlalchemy.orm import relationship,backref
from .default_method_result import DefaultMethodResult
from sqlalchemy.sql.expression import distinct
from sqlalchemy import or_,and_,text

class FOIApplicantCorrespondenceResponse(db.Model):
    # Name of the table in our database
    __tablename__ = 'FOIApplicantCorrespondenceResponses'
    __table_args__ = (
        ForeignKeyConstraint(
            ["applicantcorrespondence_id", "applicantcorrespondenceversion_id"], ["FOIApplicantCorrespondences.applicantcorrespondenceid", "FOIApplicantCorrespondences.version"]
        ),
    )
        
    # Defining the columns
    applicantcorrespondenceresponseid = db.Column(db.Integer, primary_key=True,autoincrement=True)      
    version = db.Column(db.Integer, primary_key=True,nullable=False)
    response_at = db.Column(db.DateTime, default=datetime.now)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=True)
    createdby = db.Column(db.String(120), unique=False, nullable=False)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)

    applicantcorrespondence_id =db.Column(db.Integer, db.ForeignKey('FOIApplicantCorrespondences.applicantcorrespondenceid'))
    applicantcorrespondenceversion_id = db.Column(db.Integer, db.ForeignKey('FOIApplicantCorrespondences.version'))    
                  
    
    @classmethod
    def saveapplicantcorrespondenceresponse(cls, newapplicantcorrepondenceattachment)->DefaultMethodResult: 
        db.session.add(newapplicantcorrepondenceattachment)
        db.session.commit()               
        return DefaultMethodResult(True,'applicant correpondence response added',newapplicantcorrepondenceattachment.applicantcorrespondenceresponseid)    

    @classmethod
    def getapplicantcorrespondenceresponse(cls, correspondenceresponseid)->DefaultMethodResult: 
        response_schema = FOIApplicantCorrespondenceResponseSchema()
        query = db.session.query(FOIApplicantCorrespondenceResponse).filter(FOIApplicantCorrespondenceResponse.applicantcorrespondenceresponseid == correspondenceresponseid).order_by(FOIApplicantCorrespondenceResponse.version.desc()).first()
        return response_schema.dump(query)
    
    
class FOIApplicantCorrespondenceResponseSchema(ma.Schema):
    class Meta:
        fields = ('applicantcorrespondenceresponseid', 'version', 'applicantcorrespondence_id', 'response_at','created_at','createdby')
    