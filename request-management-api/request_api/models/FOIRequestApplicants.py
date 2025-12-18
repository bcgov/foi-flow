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
    def saveapplicant(cls,firstname, lastname, middlename, businessname, alsoknownas, dob, userid):
        dbquery = db.session.query(FOIRequestApplicant)
        dbquery = dbquery.filter_by(firstname=firstname)
        applicant = dbquery.filter_by(lastname=lastname)
        if (applicant.count() > 0):
            _applicant = {
                FOIRequestApplicant.updatedby: userid, 
                FOIRequestApplicant.updated_at: datetime.now(),
                FOIRequestApplicant.middlename: middlename,
                FOIRequestApplicant.businessname: businessname,
                FOIRequestApplicant.alsoknownas: alsoknownas
            }
            if dob is not None and dob != "":
                _applicant[FOIRequestApplicant.dob] = dob
            else:
                _applicant[FOIRequestApplicant.dob] = None
            applicant.update(_applicant)
            return DefaultMethodResult(True,'Applicant updated',applicant.first().foirequestapplicantid)
        else:
            applicant = FOIRequestApplicant()
            applicant.createdby = userid
            applicant.firstname = firstname
            applicant.lastname = lastname
            applicant.middlename = middlename
            applicant.businessname = businessname
            applicant.alsoknownas = alsoknownas
            if dob is not None and dob != "":
                applicant.dob = dob
            else:
                applicant.dob = None
            db.session.add(applicant)
            db.session.commit()               
            return DefaultMethodResult(True,'Applicant added',applicant.foirequestapplicantid)
                
class FOIRequestApplicantSchema(ma.Schema):
    class Meta:
        fields = ('foirequestapplicantid','firstname','middlename','lastname','alsoknownas','dob','businessname')
    