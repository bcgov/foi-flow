from flask.app import Flask
from sqlalchemy.sql.schema import ForeignKey, ForeignKeyConstraint
from .db import  db, ma
from datetime import datetime
from sqlalchemy.orm import relationship,backref
from .default_method_result import DefaultMethodResult
from .FOIRequests import FOIRequest

class FOIRequestApplicant(db.Model):
    # Name of the table in our database
    __tablename__ = 'FOIRequestApplicants' 
    # Defining the columns
    foirequestapplicantid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    

    firstname = db.Column(db.String(50), unique=False, nullable=True)
    middlename = db.Column(db.String(50), unique=False, nullable=True)
    lastname = db.Column(db.String(50), unique=False, nullable=True)

    alsoknownas = db.Column(db.String(50), unique=False, nullable=True)
    dob = db.Column(db.DateTime, unique=False, nullable=True)
    businessname = db.Column(db.String(255), unique=False, nullable=True)
                
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=True)
    createdby = db.Column(db.String(120), unique=False, nullable=True)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)

    @classmethod
    def getrequest(cls,foirequestapplicant):
        request_schema = FOIRequestApplicantSchema()
        dbquery = db.session.query(FOIRequestApplicant)
        dbquery = dbquery.filter_by(firstname=foirequestapplicant.firstname)
        if foirequestapplicant.middlename is not None:
            dbquery = dbquery.filter_by(middlename=foirequestapplicant.middlename)
        if foirequestapplicant.lastname is not None:
            dbquery = dbquery.filter_by(lastname=foirequestapplicant.lastname)
        if foirequestapplicant.businessname is not None:
            dbquery = dbquery.filter_by(businessname=foirequestapplicant.businessname)
        if foirequestapplicant.alsoknownas is not None:
            dbquery = dbquery.filter_by(alsoknownas=foirequestapplicant.alsoknownas)
        if foirequestapplicant.dob is not None:
            dbquery = dbquery.filter_by(dob=foirequestapplicant.dob)
        result = dbquery.first()   
        return request_schema.dump(result)

    @classmethod
    def saverequest(cls,foirequestapplicant)->DefaultMethodResult:
        db.session.add(foirequestapplicant)
        db.session.commit()               
        return DefaultMethodResult(True,'Request added',foirequestapplicant.foirequestapplicantid)
                
class FOIRequestApplicantSchema(ma.Schema):
    class Meta:
        fields = ('foirequestapplicantid','firstname','middlename','lastname','alsoknownas','dob','businessname')
    