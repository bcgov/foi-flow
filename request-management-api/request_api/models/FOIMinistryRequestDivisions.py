from flask.app import Flask
from sqlalchemy.sql.schema import ForeignKey, ForeignKeyConstraint
from .db import  db, ma
from datetime import datetime
from sqlalchemy.orm import relationship,backref
from .default_method_result import DefaultMethodResult
from sqlalchemy.sql.expression import distinct
from sqlalchemy import or_,and_


class FOIMinistryRequestDivision(db.Model):
    # Name of the table in our database
    __tablename__ = 'FOIMinistryRequestDivisions'
    __table_args__ = (
        ForeignKeyConstraint(
            ["foiministryrequest_id", "foiministryrequestversion_id"], ["FOIMinistryRequests.foiministryrequestid", "FOIMinistryRequests.version"]
        ),
    )
    
    
    # Defining the columns
    foiministrydivisionid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    
    divisionid = db.Column(db.Integer,ForeignKey('ProgramAreaDivisions.divisionid'))
    division =  relationship("ProgramAreaDivision",backref=backref("ProgramAreaDivisions"),uselist=False)
    
    stageid = db.Column(db.Integer,ForeignKey('ProgramAreaDivisionStages.stageid'))
    stage =  relationship("ProgramAreaDivisionStage",backref=backref("ProgramAreaDivisionStages"),uselist=False)
    
       
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=True)
    createdby = db.Column(db.String(120), unique=False, nullable=True)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)
    
    #ForeignKey References   
    foiministryrequest_id =db.Column(db.Integer, db.ForeignKey('FOIMinistryRequests.foiministryrequestid'))
    foiministryrequestversion_id = db.Column(db.Integer, db.ForeignKey('FOIMinistryRequests.version'))    
    foiministryrequest = relationship("FOIMinistryRequest",foreign_keys="[FOIMinistryRequestDivision.foiministryrequest_id]")
    foiministryrequestversion = relationship("FOIMinistryRequest",foreign_keys="[FOIMinistryRequestDivision.foiministryrequestversion_id]")

    @classmethod
    def getrequest(cls,ministryrequestid):
        request_schema = FOIMinistryRequestDivisionSchema(many=True)
        query = db.session.query(FOIMinistryRequestDivisionSchema).filter_by(foiministryrequest_id=ministryrequestid).all()
        return request_schema.dump(query)  
    
class FOIMinistryRequestDivisionSchema(ma.Schema):
    class Meta:
        fields = ('foiministrydivisionid','division.divisionid','division.name','stage.stageid','stage.name','foiministryrequest_id','foiministryrequestversion_id')
    