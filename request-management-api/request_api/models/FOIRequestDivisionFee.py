from flask.app import Flask
from sqlalchemy.sql.schema import ForeignKey
from .db import  db, ma
from datetime import datetime
from sqlalchemy.orm import relationship,backref
from .default_method_result import DefaultMethodResult
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.sql.expression import distinct
from sqlalchemy import text, and_, func
import logging
import json
class FOIRequestDivisionFee(db.Model):
    # Name of the table in our database
    __tablename__ = 'FOIRequestDivisionFees' 
    # Defining the columns
    divisionfeeid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    version = db.Column(db.Integer, nullable=True)
    divisionid = db.Column(db.Integer,ForeignKey('ProgramAreaDivisions.divisionid'))
    division =  relationship("ProgramAreaDivision",backref=backref("ProgramAreaDivisions"),uselist=False)
    divisionname = db.Column(db.String(120), unique=False, nullable=True)    
    ministryrequest_id =db.Column(db.Integer, db.ForeignKey('FOIMinistryRequests.foiministryrequestid'))
    ministryrequest_version = db.Column(db.Integer, db.ForeignKey('FOIMinistryRequests.version'))    
    feedata = db.Column(JSON, unique=False, nullable=True) 
    estimatedhournotes = db.Column(db.Text, unique=False, nullable=True)
    clarificationnotes = db.Column(db.Text, unique=False, nullable=True)
    isresponsive = db.Column(db.Boolean, unique=False, nullable=False)
    responsivenotes = db.Column(db.Text, unique=False, nullable=True)
    isinternalresponsive = db.Column(db.Boolean, unique=False, nullable=False)
    internalresponsivenotes = db.Column(db.Text, unique=False, nullable=True)
    isexternalresponsive = db.Column(db.Boolean, unique=False, nullable=False)
    externalresponsivenotes = db.Column(db.Text, unique=False, nullable=True)         
    norecordapproval_at = db.Column(db.DateTime, default=datetime.now)
    norecordapprovalby = db.Column(db.String(120), unique=False, nullable=True)
    searchsummary = db.Column(db.Text, unique=False, nullable=True)    
    isharmsassessed = db.Column(db.Boolean, unique=False, nullable=False)
    concernnotes = db.Column(db.Text, unique=False, nullable=True)
    completed_at = db.Column(db.DateTime, default=datetime.now)
    completedby = db.Column(db.String(120), unique=False, nullable=True)    
    created_at = db.Column(db.DateTime, default=datetime.now)
    createdby = db.Column(db.String(120), unique=False, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)

    
            
class FOIRequestDivisionFeeSchema(ma.Schema):
    class Meta:
        fields = ('divisionfeeid', 'version', 'divisionid', 'division','divisionname','ministryrequest_id','ministryrequest_version',
                  'feedata','estimatedhournotes','clarificationnotes','isresponsive','responsivenotes','isinternalresponsive','internalresponsivenotes',
                  'isexternalresponsive','externalresponsivenotes','norecordapproval_at','norecordapprovalby','searchsummary',
                  'isharmsassessed','concernnotes','completed_at','completedby',
                  'created_at','createdby','updated_at','updatedby') 