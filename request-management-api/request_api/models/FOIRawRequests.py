from .db import  db
#from sqlalchemy.dialects.postgresql import JSON, JSONB
from .default_method_result import DefaultMethodResult
from datetime import datetime

class FOIRawRequest(db.Model):
    # Name of the table in our database
    __tablename__ = 'FOIRawRequests' 
    # Defining the columns
    requestid = db.Column(db.Integer, primary_key=True)
    requestrawdata = db.Column(db.String(120), unique=False, nullable=True)
    status = db.Column(db.String(25), unique=False, nullable=True)
    notes = db.Column(db.String(120), unique=False, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now().isoformat())

    @classmethod
    def saverawrequest(cls,_requestrawdata)->DefaultMethodResult:
        createdat = datetime.now().isoformat()
        newrawrequest = FOIRawRequest(requestrawdata=_requestrawdata, status='submitted',created_at=createdat)
        db.session.add(newrawrequest)
        db.session.commit()
        return DefaultMethodResult(True,'Request added')
