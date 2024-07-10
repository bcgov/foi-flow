from flask.app import Flask
from sqlalchemy.sql.schema import ForeignKey, ForeignKeyConstraint
from .db import  db, ma
from datetime import datetime
from sqlalchemy.orm import relationship,backref
from sqlalchemy import and_, or_, func
from .RequestorType import RequestorType

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

    foirequest_id =db.Column(db.Integer, ForeignKey('FOIRequests.foirequestid'))
    foirequestversion_id = db.Column(db.Integer, ForeignKey('FOIRequests.version'))
    foirequestkey = relationship("FOIRequest",foreign_keys="[FOIRequestApplicantMapping.foirequest_id]")
    foirequestversion = relationship("FOIRequest",foreign_keys="[FOIRequestApplicantMapping.foirequestversion_id]")
    
    @classmethod
    def getrequestapplicants(cls,foirequest_id,foirequestversion):
        requestapplicant_schema = FOIRequestApplicantMappingSchema(many=True)
        _applicantinfos = db.session.query(FOIRequestApplicantMapping).filter(
                                            FOIRequestApplicantMapping.foirequest_id == foirequest_id,
                                            FOIRequestApplicantMapping.foirequestversion_id == foirequestversion
                                        ).order_by(FOIRequestApplicantMapping.foirequestapplicantmappingid.asc()).all()
        applicantinfos = requestapplicant_schema.dump(_applicantinfos)
        return applicantinfos
    
    @classmethod
    def getrequestapplicantinfos(cls,foirequest_id,foirequestversion):
        from .FOIRequestApplicants import FOIRequestApplicant
        _applicantinfos = db.session.query(*[
                                            FOIRequestApplicantMapping.foirequestapplicantmappingid,
                                            FOIRequestApplicantMapping.foirequest_id.label('foirequestid'),
                                            FOIRequestApplicantMapping.foirequestversion_id.label('version'),
                                            FOIRequestApplicantMapping.requestortypeid.label('requestortypeid'),
                                            RequestorType.name.label('requestortype'),
                                            FOIRequestApplicant.foirequestapplicantid.label('foirequestapplicantid'),
                                            FOIRequestApplicant.firstname.label('firstname'),
                                            FOIRequestApplicant.lastname.label('lastname'),
                                            FOIRequestApplicant.middlename.label('middlename'),
                                            FOIRequestApplicant.alsoknownas.label('alsoknownas'),
                                            FOIRequestApplicant.dob.label('dob'),
                                            FOIRequestApplicant.businessname.label('businessname'),
                                            FOIRequestApplicant.axisapplicantid.label('axisapplicantid'),
                                        ]).join(
                                            FOIRequestApplicant,
                                            FOIRequestApplicant.foirequestapplicantid == FOIRequestApplicantMapping.foirequestapplicantid
                                        ).join(
                                            RequestorType,
                                            RequestorType.requestortypeid == FOIRequestApplicantMapping.requestortypeid
                                        ).filter(
                                            FOIRequestApplicantMapping.foirequest_id == foirequest_id,
                                            FOIRequestApplicantMapping.foirequestversion_id == foirequestversion
                                        ).order_by(FOIRequestApplicantMapping.foirequestapplicantmappingid.asc()).all()
        requestapplicant_schema = FOIRequestApplicantInfoSchema(many=True)
        applicantinfos = requestapplicant_schema.dump(_applicantinfos)
        return applicantinfos

class FOIRequestApplicantMappingSchema(ma.Schema):
    class Meta:
        fields = ('foirequestapplicantmappingid','foirequest.foirequestid','foirequest.version','requestortype.requestortypeid','requestortype.name','foirequestapplicant.foirequestapplicantid','foirequestapplicant.firstname','foirequestapplicant.lastname','foirequestapplicant.middlename','foirequestapplicant.alsoknownas','foirequestapplicant.dob','foirequestapplicant.businessname')

class FOIRequestApplicantInfoSchema(ma.Schema):
    class Meta:
        fields = ('foirequestapplicantmappingid','foirequestid','version','requestortypeid','requestortype','foirequestapplicantid','firstname','lastname','middlename','alsoknownas','dob','businessname','axisapplicantid')
    