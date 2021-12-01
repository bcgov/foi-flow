from enum import unique


from sqlalchemy.sql.expression import distinct
from .db import  db, ma
from sqlalchemy.dialects.postgresql import JSON, UUID
from .default_method_result import DefaultMethodResult
from datetime import datetime
from sqlalchemy import insert, and_, text
from flask import jsonify

class FOIRawRequest(db.Model):
    # Name of the table in our database
    __tablename__ = 'FOIRawRequests' 
    # Defining the columns
    requestid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    version = db.Column(db.Integer, primary_key=True,nullable=False)
    requestrawdata = db.Column(JSON, unique=False, nullable=True)
    status = db.Column(db.String(25), unique=False, nullable=True)
    notes = db.Column(db.String(120), unique=False, nullable=True)
    wfinstanceid = db.Column(UUID(as_uuid=True), unique=False, nullable=True)
    assignedgroup = db.Column(db.String(250), unique=False, nullable=True) 
    assignedto = db.Column(db.String(120), unique=False, nullable=True)    
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=True)
    createdby = db.Column(db.String(120), unique=False, nullable=True)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)
    sourceofsubmission = db.Column(db.String(120),  nullable=True)
    ispiiredacted = db.Column(db.Boolean, unique=False, nullable=False,default=False)
    requirespayment = db.Column(db.Boolean, unique=False, nullable=True, default=False)
    
    @classmethod
    def saverawrequest(cls,_requestrawdata,sourceofsubmission, ispiiredacted, userId, requirespayment ,assigneegroup= None,assignee= None)->DefaultMethodResult:                
        createdat = datetime.now()        
        version = 1
        newrawrequest = FOIRawRequest(requestrawdata=_requestrawdata, status='Unopened' if sourceofsubmission != "intake" else 'Intake in Progress',created_at=createdat,createdby=userId,version=version,sourceofsubmission=sourceofsubmission,assignedgroup=assigneegroup,assignedto=assignee,ispiiredacted=ispiiredacted, requirespayment=requirespayment)
        db.session.add(newrawrequest)
        db.session.commit()               
        return DefaultMethodResult(True,'Request added',newrawrequest.requestid)

    @classmethod
    def saverawrequest_foipayment(cls,_requestrawdata,notes, requirespayment, ispiiredacted)->DefaultMethodResult:                
        createdat = datetime.now()        
        version = 1
        newrawrequest = FOIRawRequest(requestrawdata=_requestrawdata, status='Unopened',created_at=createdat,createdby=None,version=version,sourceofsubmission="onlineform",assignedgroup=None,assignedto=None,ispiiredacted=ispiiredacted,notes=notes, requirespayment= requirespayment)
        db.session.add(newrawrequest)
        db.session.commit()               
        return DefaultMethodResult(True,'Request added',newrawrequest.requestid)

    @classmethod
    def saverawrequestversion(cls,_requestrawdata,requestid, assigneegroup, assignee,status,ispiiredacted, userId)->DefaultMethodResult:        
        updatedat = datetime.now()
        request = db.session.query(FOIRawRequest).filter_by(requestid=requestid).order_by(FOIRawRequest.version.desc()).first()
        if request is not None:
                
            _version = request.version+1           
            insertstmt =(
                insert(FOIRawRequest).
                values(requestid=request.requestid, requestrawdata=_requestrawdata,version=_version,updatedby=None,status=status,assignedgroup=assigneegroup,assignedto=assignee,wfinstanceid=request.wfinstanceid,sourceofsubmission=request.sourceofsubmission,ispiiredacted=ispiiredacted,createdby=userId)
            )                 
            db.session.execute(insertstmt)               
            db.session.commit()                
            return DefaultMethodResult(True,'Request versioned - {0}'.format(str(_version)),requestid,request.wfinstanceid,assignee)    
        else:
            return DefaultMethodResult(True,'No request foound')
            
    @classmethod
    def updateworkflowinstance(cls,wfinstanceid,requestid, userId)->DefaultMethodResult:
        updatedat = datetime.now()
        dbquery = db.session.query(FOIRawRequest)
        requestraqw = dbquery.filter_by(requestid=requestid,version = 1)
        if(requestraqw.count() > 0) :
            existingrequestswithWFid = dbquery.filter_by(wfinstanceid=wfinstanceid)               
            if(existingrequestswithWFid.count() == 0) :
                requestraqw.update({FOIRawRequest.wfinstanceid:wfinstanceid, FOIRawRequest.updated_at:updatedat,FOIRawRequest.updatedby:userId, FOIRawRequest.notes:"WF Instance created"}, synchronize_session = False)
                db.session.commit()
                return DefaultMethodResult(True,'Request updated with WF Instance Id',requestid)
            else:
                return DefaultMethodResult(False,'WF instance already exists',requestid) 
        else:
            return DefaultMethodResult(False,'Requestid not exists',-1)              

    @classmethod
    def updateworkflowinstancewithstatus(cls,wfinstanceid,requestid,status,notes,userId)-> DefaultMethodResult:
        updatedat = datetime.now()
        dbquery = db.session.query(FOIRawRequest)
        _requestraqw = dbquery.filter_by(requestid=requestid).order_by(FOIRawRequest.version.desc()).first()
        requestraqw = dbquery.filter_by(requestid=requestid,version = _requestraqw.version)        
        if(requestraqw.count() > 0) :            
            request_schema = FOIRawRequestSchema()
            request = request_schema.dump(_requestraqw)            
            if(request is not None and (request["status"] == "Redirect" or request["status"] == "Closed")):
                status = request["status"]
                                
            existingrequestswithWFid = dbquery.filter_by(wfinstanceid=wfinstanceid)                    
            requestraqw.update({FOIRawRequest.wfinstanceid:wfinstanceid, FOIRawRequest.updated_at:updatedat,FOIRawRequest.notes:notes,FOIRawRequest.status:status,FOIRawRequest.updatedby:userId}, synchronize_session = False)
            db.session.commit()
            return DefaultMethodResult(True,'Request updated',requestid)       
        else:
            return DefaultMethodResult(False,'Requestid not exists',-1)    

    @classmethod
    def getrequests(cls):
        request_schema = FOIRawRequestSchema(many=True)
        _session = db.session
        _archivedRequestids = _session.query(distinct(FOIRawRequest.requestid)).filter(FOIRawRequest.status =="Archived").all()
        _requestids = _session.query(distinct(FOIRawRequest.requestid)).filter(FOIRawRequest.requestid.notin_(_archivedRequestids)).all()
        requests = []
        for _requestid in _requestids:
           request = _session.query(FOIRawRequest).filter(FOIRawRequest.requestid == _requestid).order_by(FOIRawRequest.version.desc()).first()           
           requests.append(request)

        return requests
    
    @classmethod
    def getDescriptionSummaryById(cls, requestid):
        sql = """select CASE WHEN lower(status) <> 'unopened' then requestrawdata ->> 'description' ELSE requestrawdata -> 'descriptionTimeframe' ->> 'description' END as description ,  
                    CASE WHEN lower(status) <> 'unopened' then requestrawdata ->> 'fromDate' ELSE requestrawdata -> 'descriptionTimeframe' ->> 'fromDate' END as fromdate, 
                    CASE WHEN lower(status) <> 'unopened'then requestrawdata ->> 'toDate' ELSE requestrawdata -> 'descriptionTimeframe' ->> 'toDate' END as todate, 
                    to_char(updated_at, 'YYYY-MM-DD HH24:MI:SS') as createdat, status, ispiiredacted, 
                    CASE WHEN lower(status) <> 'unopened' then createdby else 'Online Form' END  as createdby from "FOIRawRequests" fr 
                    where requestid = :requestid order by version ;"""
        rs = db.session.execute(text(sql), {'requestid': requestid})
        requests = []
        for row in rs:
            requests.append(dict(row))
        return requests

    @classmethod
    def get_request(cls,requestid):   
       request_schema = FOIRawRequestSchema()
       request = db.session.query(FOIRawRequest).filter_by(requestid=requestid).order_by(FOIRawRequest.version.desc()).first()
       return request_schema.dump(request)

class FOIRawRequestSchema(ma.Schema):
    class Meta:
        fields = ('requestid', 'requestrawdata', 'status','notes','created_at','wfinstanceid','version','updated_at','assignedgroup','assignedto','updatedby','createdby','sourceofsubmission','ispiiredacted')