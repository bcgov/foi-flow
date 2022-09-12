from flask.app import Flask
from sqlalchemy.sql.schema import ForeignKey, ForeignKeyConstraint
from .db import  db, ma
from datetime import datetime
from sqlalchemy.orm import relationship,backref
from .default_method_result import DefaultMethodResult
from sqlalchemy.sql.expression import distinct
from sqlalchemy import or_,and_,text

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
    correspondencemessagejson = db.Column(db.Text, unique=False, nullable=False)
   
 
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=True)
    createdby = db.Column(db.String(120), unique=False, nullable=False)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)
    
    #ForeignKey References       
    foiministryrequest_id =db.Column(db.Integer, db.ForeignKey('FOIMinistryRequests.foiministryrequestid'))
    foiministryrequestversion_id=db.Column(db.Integer, db.ForeignKey('FOIMinistryRequests.version'))

    @classmethod
    def getapplicantcorrespondences(cls,ministryrequestid):
        comment_schema = FOIApplicantCorrespondenceSchema(many=True)
        query = db.session.query(FOIApplicantCorrespondenceSchema).filter_by(foiministryrequest_id=ministryrequestid).order_by(FOIApplicantCorrespondence.applicantcorrespondenceid.desc()).all()
        return comment_schema.dump(query)

    @classmethod
    def saveapplicantcorrespondence(cls, newapplicantcorrepondencelog)->DefaultMethodResult: 
        
        db.session.add(newapplicantcorrepondencelog)
        db.session.commit()               
        return DefaultMethodResult(True,'applicantcorrepondence log added',newapplicantcorrepondencelog.applicantcorrespondenceid)    

    
class FOIApplicantCorrespondenceSchema(ma.Schema):
    class Meta:
        fields = ('applicantcorrespondenceid','parentapplicantcorrespondenceid', 'templateid','correspondencemessagejson','foiministryrequest_id','foiministryrequestversion_id','created_at','createdby')
    