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
                
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=True)
    createdby = db.Column(db.String(120), unique=False, nullable=True)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)

    @classmethod
    def getrequest(cls,foiRequestApplicant):
        request_schema = FOIRequestApplicantSchema()
        dbquery = db.session.query(FOIRequestApplicant)
        dbquery = dbquery.filter_by(firstname=foiRequestApplicant.firstname)
        if foiRequestApplicant.middlename is not None:
            dbquery = dbquery.filter_by(middlename=foiRequestApplicant.middlename)
        if foiRequestApplicant.lastname is not None:
            dbquery = dbquery.filter_by(lastname=foiRequestApplicant.lastname)
        if foiRequestApplicant.businessname is not None:
            dbquery = dbquery.filter_by(businessname=foiRequestApplicant.businessname)
        if foiRequestApplicant.alsoknownas is not None:
            dbquery = dbquery.filter_by(alsoknownas=foiRequestApplicant.alsoknownas)
        if foiRequestApplicant.dob is not None:
            dbquery = dbquery.filter_by(dob=foiRequestApplicant.dob)
        result = dbquery.first()   
        return request_schema.dump(result)

    @classmethod
    def saverequest(cls,foiRequestApplicant)->DefaultMethodResult:
        db.session.add(foiRequestApplicant)
        db.session.commit()               
        return DefaultMethodResult(True,'Request added',foiRequestApplicant.foirequestapplicantid)
                
class FOIRequestApplicantSchema(ma.Schema):
    class Meta:
        fields = ('foirequestapplicantid','firstname','middlename','lastname','alsoknownas','dob','businessname')
    