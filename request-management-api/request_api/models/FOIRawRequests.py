from .db import  db, ma
from sqlalchemy.dialects.postgresql import JSON, UUID
from .default_method_result import DefaultMethodResult
from datetime import datetime

class FOIRawRequest(db.Model):
    # Name of the table in our database
    __tablename__ = 'FOIRawRequests' 
    # Defining the columns
    requestid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    version = db.Column(db.Integer, primary_key=True)
    requestrawdata = db.Column(JSON, unique=False, nullable=True)
    status = db.Column(db.String(25), unique=False, nullable=True)
    notes = db.Column(db.String(120), unique=False, nullable=True)
    wfinstanceid = db.Column(UUID(as_uuid=True), unique=False, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now().isoformat())
    updated_at = db.Column(db.DateTime, nullable=True)
    
    @classmethod
    def saverawrequest(cls,_requestrawdata)->DefaultMethodResult:        
        createdat = datetime.now().isoformat()
        version = 1
        newrawrequest = FOIRawRequest(requestrawdata=_requestrawdata, status='unopened',created_at=createdat,version=version)
        db.session.add(newrawrequest)
        db.session.commit()               
        return DefaultMethodResult(True,'Request added',newrawrequest.requestid)

    @classmethod
    def updateworkflowinstance(cls,wfinstanceid,requestid)->DefaultMethodResult:
        updatedat = datetime.now().isoformat()
        dbquery = db.session.query(FOIRawRequest)
        existingrequestswithWFid = dbquery.filter_by(wfinstanceid=wfinstanceid)        
        if(existingrequestswithWFid.count() == 0) :
            dbquery.filter_by(requestid=requestid).update({FOIRawRequest.wfinstanceid:wfinstanceid, FOIRawRequest.updated_at:updatedat,FOIRawRequest.notes:"WF Instance created"}, synchronize_session = False)
            db.session.commit()
            return DefaultMethodResult(True,'Request updated with WF Instance Id',requestid)
        else:
             return DefaultMethodResult(False,'WF instance already exists',requestid)   
        

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
        fields = ('requestid', 'requestrawdata', 'status','notes','created_at','wfinstanceid','version','updated_at')