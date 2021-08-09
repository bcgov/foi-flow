from flask.app import Flask
from sqlalchemy.sql.schema import ForeignKey, ForeignKeyConstraint
from .db import  db, ma
from datetime import datetime
from sqlalchemy.orm import relationship,backref
from .default_method_result import DefaultMethodResult
from .FOIRequests import FOIRequest

class FOIRequestApplicantMapping(db.Model):
    # Name of the table in our database
    __tablename__ = 'FOIRequestApplicantMappings' 
    # Defining the columns
    
    foirequestapplicantmappingid = db.Column(db.Integer, primary_key=True,autoincrement=True)            
    created_at = db.Column(db.DateTime, default=datetime.now().isoformat())
    updated_at = db.Column(db.DateTime, nullable=True)
    createdby = db.Column(db.String(120), unique=False, nullable=True)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)

    #ForeignKey References
    
    requestortypeid = db.Column(db.Integer,ForeignKey('RequestorTypes.requestortypeid'))
    requestortype =  relationship("RequestorType",backref=backref("RequestorTypes"),uselist=False)

    foirequestapplicantid = db.Column(db.Integer,ForeignKey('FOIRequestApplicants.foirequestapplicantid'))
    foirequestapplicant =  relationship("FOIRequestApplicant",backref=backref("FOIRequestApplicants"),uselist=False)

    foirequestid = db.Column(db.Integer)
    foirequestversion = db.Column(db.Integer)

    foirequest =  (ForeignKeyConstraint([foirequestid,foirequestversion],[FOIRequest.foirequestid,FOIRequest.version]),{})
    
            
class FOIRequestApplicantMappingSchema(ma.Schema):
    class Meta:
        fields = ('foirequestapplicantmappingid','foirequest.foirequestid','foirequest.version','requestortype.requestortypeid','requestortype.name','foirequestapplicant.foirequestapplicantid','foirequestapplicant.firstname','foirequestapplicant.lastname')
    