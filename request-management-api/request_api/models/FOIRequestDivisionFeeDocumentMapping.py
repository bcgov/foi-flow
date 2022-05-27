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
class FOIRequestDivisionFeeDocumentMapping(db.Model):
    # Name of the table in our database
    __tablename__ = 'FOIRequestDivisionFeeDocumentMappings' 
    # Defining the columns
    divisionfeedocumentid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    divisionfee_id =db.Column(db.Integer, ForeignKey('FOIRequestDivisionFees.divisionfeeid'))
    divisionfee_version = db.Column(db.Integer, ForeignKey('FOIRequestDivisionFees.version'))
    ministrydocumentid =db.Column(db.Integer, ForeignKey('FOIMinistryRequestDocuments.foiministrydocumentid'))
    created_at = db.Column(db.DateTime, default=datetime.now)
    createdby = db.Column(db.String(120), unique=False, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)

class FOIRequestDivisionFeeDocumentMappingSchema(ma.Schema):
    class Meta:
        fields = ('divisionfeedocumentid', 'divisionfee_id', 'divisionfee_version', 'ministrydocumentid',
                  'created_at','createdby','updated_at','updatedby') 