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
    __table_args__ = (
        ForeignKeyConstraint(
            ["foirequest_id", "foirequestversion_id"], ["FOIRequests.foirequestid", "FOIRequests.version"]
        ),
    )     
    # Defining the columns
    
    foirequestapplicantmappingid = db.Column(db.Integer, primary_key=True,autoincrement=True)            
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=True)
    createdby = db.Column(db.String(120), unique=False, nullable=True)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)

    #ForeignKey References
    
    requestortypeid = db.Column(db.Integer,ForeignKey('RequestorTypes.requestortypeid'))
    requestortype =  relationship("RequestorType",backref=backref("RequestorTypes"),uselist=False)

    foirequestapplicantid = db.Column(db.Integer,ForeignKey('FOIRequestApplicants.foirequestapplicantid'))
    foirequestapplicant =  relationship("FOIRequestApplicant",backref=backref("FOIRequestApplicants"),uselist=False)

    foirequest_id =db.Column(db.Integer, db.ForeignKey('FOIRequests.foirequestid'))
    foirequestversion_id = db.Column(db.Integer, db.ForeignKey('FOIRequests.version'))
    foirequestkey = relationship("FOIRequest",foreign_keys="[FOIRequestApplicantMapping.foirequest_id]")
    foirequestversion = relationship("FOIRequest",foreign_keys="[FOIRequestApplicantMapping.foirequestversion_id]")
    
    @classmethod
    def getrequestapplicants(cls,foirequest_id,foirequestversion):
        requestapplicant_schema = FOIRequestApplicantMappingSchema(many=True)
        _applicantinfos = db.session.query(FOIRequestApplicantMapping).filter(FOIRequestApplicantMapping.foirequest_id == foirequest_id , FOIRequestApplicantMapping.foirequestversion_id == foirequestversion).order_by(FOIRequestApplicantMapping.foirequestapplicantmappingid.asc()).all()
        applicantinfos = requestapplicant_schema.dump(_applicantinfos)       
        return applicantinfos
            
class FOIRequestApplicantMappingSchema(ma.Schema):
    class Meta:
        fields = ('foirequestapplicantmappingid','foirequest.foirequestid','foirequest.version','requestortype.requestortypeid','requestortype.name','foirequestapplicant.foirequestapplicantid','foirequestapplicant.firstname','foirequestapplicant.lastname','foirequestapplicant.middlename','foirequestapplicant.alsoknownas','foirequestapplicant.dob','foirequestapplicant.businessname')
    