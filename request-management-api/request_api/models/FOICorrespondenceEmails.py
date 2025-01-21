from flask.app import Flask
from sqlalchemy.sql.schema import ForeignKey, ForeignKeyConstraint
from .db import  db, ma
from datetime import datetime
from sqlalchemy.orm import relationship,backref
from .default_method_result import DefaultMethodResult
from sqlalchemy.sql.expression import distinct
from sqlalchemy import or_,and_,text
from sqlalchemy.dialects.postgresql import JSON, UUID

class FOICorrespondenceEmail(db.Model):
    # Name of the table in our database
    __tablename__ = 'FOICorrespondenceEmails'
    __table_args__ = (
        ForeignKeyConstraint(
            ["foiministryrequest_id", "foiministryrequestversion_id"], ["FOIMinistryRequests.foiministryrequestid", "FOIMinistryRequests.version"]
        ),
    )
        
    # Defining the columns
    correspondenceemailid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    email = db.Column(db.Text, unique=False, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=True)
    createdby = db.Column(db.String(120), unique=False, nullable=False)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)
    
    #ForeignKey References       
    foiministryrequest_id =db.Column(db.Integer, db.ForeignKey('FOIMinistryRequests.foiministryrequestid'))
    foiministryrequestversion_id=db.Column(db.Integer, db.ForeignKey('FOIMinistryRequests.version'))

    
    @classmethod
    def getcorrespondenceemails(cls,ministryrequestid):
        email_schema = FOICorrepondenceEmailSchema(many=True)
        query = db.session.query(FOICorrespondenceEmail.email).filter(FOICorrespondenceEmail.foiministryrequest_id == ministryrequestid).order_by(FOICorrespondenceEmail.email.desc()).all()
        return email_schema.dump(query)
    
    
    
    @classmethod
    def savecorrespondenceemail(cls,correpondenceemail)->DefaultMethodResult: 
        
        try:
            db.session.add(correpondenceemail)
            db.session.commit()
            return DefaultMethodResult(True,'correspondence email added')
        except Exception:
            return DefaultMethodResult(False,'unable to save correspondence email')
        finally:
            db.session.close()
   
class FOICorrepondenceEmailSchema(ma.Schema):
    class Meta:
        fields = ('correspondenceemailid','email','created_at','createdby')
    