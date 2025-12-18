from flask.app import Flask
from sqlalchemy.sql.schema import ForeignKey, ForeignKeyConstraint
from .db import  db, ma
from datetime import datetime
from sqlalchemy.orm import relationship,backref
from .default_method_result import DefaultMethodResult
from .FOIRequests import FOIRequest

class FOIRequestContactInformation(db.Model):
    # Name of the table in our database
    __tablename__ = 'FOIRequestContactInformation' 
    __table_args__ = (
        ForeignKeyConstraint(
            ["foirequest_id", "foirequestversion_id"], ["FOIRequests.foirequestid", "FOIRequests.version"]
        ),
    )   
    # Defining the columns
    foirequestcontactid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    
    contactinformation = db.Column(db.String(500), unique=False, nullable=False)
    dataformat = db.Column(db.String(40), unique=False, nullable=True)
    
                
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=True)
    createdby = db.Column(db.String(120), unique=False, nullable=True)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)

    #ForeignKey References
    
    contacttypeid = db.Column(db.Integer,ForeignKey('ContactTypes.contacttypeid'))
    contacttype =  relationship("ContactType",backref=backref("ContactTypes"),uselist=False)

    foirequest_id =db.Column(db.Integer, db.ForeignKey('FOIRequests.foirequestid'))
    foirequestversion_id = db.Column(db.Integer, db.ForeignKey('FOIRequests.version'))
    foirequestkey = relationship("FOIRequest",foreign_keys="[FOIRequestContactInformation.foirequest_id]")
    foirequestversion = relationship("FOIRequest",foreign_keys="[FOIRequestContactInformation.foirequestversion_id]")

 
    @classmethod
    def getrequestcontactinformation(cls,foirequest_id,foirequestversion):
        requestcontact_schema = FOIRequestContactInformationSchema(many=True)
        _contactinfos = db.session.query(FOIRequestContactInformation).filter(FOIRequestContactInformation.foirequest_id == foirequest_id , FOIRequestContactInformation.foirequestversion_id == foirequestversion).order_by(FOIRequestContactInformation.foirequestcontactid.asc()).all()
        contactinfos = requestcontact_schema.dump(_contactinfos)       
        return contactinfos


class FOIRequestContactInformationSchema(ma.Schema):
    class Meta:
        fields = ('foirequestcontactid','contactinformation','dataformat','contacttype.contacttypeid','contacttype.name','foirequest.foirequestid','foirequest.version')
    