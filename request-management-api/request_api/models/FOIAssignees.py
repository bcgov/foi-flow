from flask.app import Flask
from .db import  db, ma
from .default_method_result import DefaultMethodResult

class FOIAssignee(db.Model):
    # Name of the table in our database
    __tablename__ = 'FOIAssignees' 
    # Defining the columns
    foiassigneeid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    firstname = db.Column(db.String(100), unique=False, nullable=False)
    middlename = db.Column(db.String(100), unique=False, nullable=True)
    lastname = db.Column(db.String(100), unique=False, nullable=False)
    isactive = db.Column(db.Boolean, unique=False, nullable=False, default=True)

    @classmethod
    def saveassignee(cls, foiassignee)->DefaultMethodResult:
        db.session.add(foiassignee)
        db.session.commit()               
        return DefaultMethodResult(True, 'Assignee added', foiassignee.username)
                
class FOIRequestApplicantSchema(ma.Schema):
    class Meta:
        fields = ('foiassigneeid','username','firstname','middlename','lastname','isactive')
    