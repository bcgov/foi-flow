from flask.app import Flask
from sqlalchemy.sql.schema import ForeignKey, ForeignKeyConstraint
from .db import  db, ma
from datetime import datetime
from sqlalchemy.orm import relationship,backref
from .default_method_result import DefaultMethodResult
from sqlalchemy.sql.expression import distinct
from sqlalchemy import or_, and_, text


class FOIMinistryRequestSubjectCode(db.Model):
    # Name of the table in our database
    __tablename__ = 'FOIMinistryRequestSubjectCodes'
    __table_args__ = (
        ForeignKeyConstraint(
            ["foiministryrequestid", "foiministryrequestversion"], ["FOIMinistryRequests.foiministryrequestid", "FOIMinistryRequests.version"]
        ),
    )
    
    
    # Defining the columns
    foiministrysubjectcodeid = db.Column(db.Integer, primary_key=True,autoincrement=True)    
    subjectcodeid = db.Column(db.Integer,ForeignKey('SubjectCodes.subjectcodeid'))
    subjectcode =  relationship("SubjectCode",backref=backref("SubjectCodes"),uselist=False)    
       
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=True)
    createdby = db.Column(db.String(120), unique=False, nullable=True)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)
    
    #ForeignKey References   
    foiministryrequestid =db.Column(db.Integer, db.ForeignKey('FOIMinistryRequests.foiministryrequestid'))
    foiministryrequestversion = db.Column(db.Integer, db.ForeignKey('FOIMinistryRequests.version'))    
    ministryrequest = relationship("FOIMinistryRequest",foreign_keys="[FOIMinistryRequestSubjectCode.foiministryrequestid]")
    ministryrequestversion = relationship("FOIMinistryRequest",foreign_keys="[FOIMinistryRequestSubjectCode.foiministryrequestversion]")

    @classmethod
    def getministrysubjectcode(cls, ministryrequestid, ministryrequestversion):
        ministrysubjectcode_schema = FOIMinistryRequestSubjectCodeSchema()
        ministrysubjectcode = db.session.query(FOIMinistryRequestSubjectCode).filter(FOIMinistryRequestSubjectCode.foiministryrequestid == ministryrequestid , FOIMinistryRequestSubjectCode.foiministryrequestversion == ministryrequestversion).first()
        subjectcodeinfos = ministrysubjectcode_schema.dump(ministrysubjectcode)       
        return subjectcodeinfos
    
    @classmethod
    def savesubjectcode(cls, ministryrequestid, ministryrequestversion, subjectcodeid, userid):
        newsubjectcode = FOIMinistryRequestSubjectCode(subjectcodeid=subjectcodeid, foiministryrequestid=ministryrequestid, foiministryrequestversion=ministryrequestversion, created_at=datetime.now(), createdby=userid)
        db.session.add(newsubjectcode)
        db.session.commit()               
        return DefaultMethodResult(True,'New subject code added', newsubjectcode.foiministrysubjectcodeid) 

class FOIMinistryRequestSubjectCodeSchema(ma.Schema):
    class Meta:
        fields = ('foiministrysubjectcodeid','subjectcodeid','subjectcode.name','foiministryrequestid','foiministryrequestversion')
    