from .db import  db, ma
from sqlalchemy.dialects.postgresql import JSON, JSONB
from .default_method_result import DefaultMethodResult
from datetime import datetime

class FOIRawRequest(db.Model):
    # Name of the table in our database
    __tablename__ = 'FOIRawRequests' 
    # Defining the columns
    requestid = db.Column(db.Integer, primary_key=True)
    requestrawdata = db.Column(JSON, unique=False, nullable=True)
    status = db.Column(db.String(25), unique=False, nullable=True)
    notes = db.Column(db.String(120), unique=False, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now().isoformat())

    def get_id(self):
        return text_type(self.requestid)

    @classmethod
    def saverawrequest(cls,_requestrawdata)->DefaultMethodResult:        
        createdat = datetime.now().isoformat()
        newrawrequest = FOIRawRequest(requestrawdata=_requestrawdata, status='submitted',created_at=createdat)
        db.session.add(newrawrequest)
        db.session.commit()               
        return DefaultMethodResult(True,'Request added',newrawrequest.requestid)

    @classmethod
    def getrequests(cls):
        request_schema = FOIRawRequestSchema(many=True)
        query = db.session.query(FOIRawRequest).all()
        return request_schema.dump(query)

    @classmethod
    def get_request(cls,requestid):   
       request_schema = FOIRawRequestSchema()
       request = db.session.query(FOIRawRequest).filter_by(requestid=requestid).first()
       return request_schema.dump(request)

class FOIRawRequestSchema(ma.Schema):
    class Meta:
        fields = ('requestid', 'requestrawdata', 'status','notes','created_at')