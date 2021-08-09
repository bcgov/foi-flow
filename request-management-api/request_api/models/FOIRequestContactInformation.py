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
    # Defining the columns
    foirequestcontactid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    
    ContactInformation = db.Column(db.String(500), unique=False, nullable=False)
    DataFormat = db.Column(db.String(40), unique=False, nullable=True)
    
                
    created_at = db.Column(db.DateTime, default=datetime.now().isoformat())
    updated_at = db.Column(db.DateTime, nullable=True)
    createdby = db.Column(db.String(120), unique=False, nullable=True)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)

    #ForeignKey References
    
    contacttypeid = db.Column(db.Integer,ForeignKey('ContactTypes.contacttypeid'))
    contacttype =  relationship("ContactType",backref=backref("ContactTypes"),uselist=False)

    foirequestid = db.Column(db.Integer)
    foirequestversion = db.Column(db.Integer)
    foirequest =  (ForeignKeyConstraint([foirequestid,foirequestversion],[FOIRequest.foirequestid,FOIRequest.version]),{})

 
    

    

class FOIRequestContactInformationSchema(ma.Schema):
    class Meta:
        fields = ('foirequestcontactid','ContactInformation','DataFormat','contacttype.contacttypeid','contacttype.name','foirequest.foirequestid','foirequest.version')
    