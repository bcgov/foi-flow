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
    # Defining the columns
    foirequestpersonalattributeid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    

    attributevalue = db.Column(db.String(256), unique=False, nullable=False)

                
    created_at = db.Column(db.DateTime, default=datetime.now().isoformat())
    updated_at = db.Column(db.DateTime, nullable=True)
    createdby = db.Column(db.String(120), unique=False, nullable=True)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)

    #ForeignKey References
    
    personalattributeid = db.Column(db.Integer,ForeignKey('PersonalInformationAttributes.attributeid'))
    personalattribute =  relationship("PersonalInformationAttribute",backref=backref("PersonalInformationAttributes"),uselist=False)

    foirequestid = db.Column(db.Integer)
    foirequestversion = db.Column(db.Integer)

    foirequest =  (ForeignKeyConstraint([foirequestid,foirequestversion],[FOIRequest.foirequestid,FOIRequest.version]),{})
    


class FOIRequestPersonalAttributeSchema(ma.Schema):
    class Meta:
        fields = ('foirequestpersonalattributeid','attributevalue','foirequest.foirequestid','personalattribute.name','personalattributeid')
    