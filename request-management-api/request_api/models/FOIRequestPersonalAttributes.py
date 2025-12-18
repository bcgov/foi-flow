from flask.app import Flask
from sqlalchemy.sql.schema import ForeignKey, ForeignKeyConstraint
from .db import  db, ma
from datetime import datetime
from sqlalchemy.orm import relationship,backref
from .default_method_result import DefaultMethodResult
from .FOIRequests import FOIRequest

class FOIRequestPersonalAttribute(db.Model):
    # Name of the table in our database
    __tablename__ = 'FOIRequestPersonalAttributes' 
    __table_args__ = (
        ForeignKeyConstraint(
            ["foirequest_id", "foirequestversion_id"], ["FOIRequests.foirequestid", "FOIRequests.version"]
        ),
    )  
    # Defining the columns
    foirequestpersonalattributeid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    

    attributevalue = db.Column(db.String(256), unique=False, nullable=False)

                
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=True)
    createdby = db.Column(db.String(120), unique=False, nullable=True)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)

    #ForeignKey References
    
    personalattributeid = db.Column(db.Integer,ForeignKey('PersonalInformationAttributes.attributeid'))
    personalattribute =  relationship("PersonalInformationAttribute",backref=backref("PersonalInformationAttributes"),uselist=False)

    foirequest_id =db.Column(db.Integer, db.ForeignKey('FOIRequests.foirequestid'))
    foirequestversion_id = db.Column(db.Integer, db.ForeignKey('FOIRequests.version'))
    foirequestkey = relationship("FOIRequest",foreign_keys="[FOIRequestPersonalAttribute.foirequest_id]")
    foirequestversion = relationship("FOIRequest",foreign_keys="[FOIRequestPersonalAttribute.foirequestversion_id]")
    
    @classmethod
    def getrequestpersonalattributes(cls,foirequest_id,foirequestversion):
        requestpersonalattribute_schema = FOIRequestPersonalAttributeSchema(many=True)
        _personalattributes = db.session.query(FOIRequestPersonalAttribute).filter(FOIRequestPersonalAttribute.foirequest_id == foirequest_id , FOIRequestPersonalAttribute.foirequestversion_id == foirequestversion).order_by(FOIRequestPersonalAttribute.foirequestpersonalattributeid.asc()).all()
        personalattributes = requestpersonalattribute_schema.dump(_personalattributes)
        return personalattributes


class FOIRequestPersonalAttributeSchema(ma.Schema):
    class Meta:
        fields = ('foirequestpersonalattributeid','attributevalue','foirequest.foirequestid','personalattribute.name','personalattributeid')
    