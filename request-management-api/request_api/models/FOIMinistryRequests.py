from flask.app import Flask
from sqlalchemy.sql.schema import ForeignKey, ForeignKeyConstraint
from .db import  db, ma
from datetime import datetime
from sqlalchemy.orm import relationship,backref
from .default_method_result import DefaultMethodResult
from .FOIRequests import FOIRequest, FOIRequestsSchema
from sqlalchemy.sql.expression import distinct

from .FOIRequestApplicantMappings import FOIRequestApplicantMapping

class FOIMinistryRequest(db.Model):
    # Name of the table in our database
    __tablename__ = 'FOIMinistryRequests'
    __table_args__ = (
        ForeignKeyConstraint(
            ["foirequest_id", "foirequestversion_id"], ["FOIRequests.foirequestid", "FOIRequests.version"]
        ),
    )
    
    
    # Defining the columns
    foiministryrequestid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    version = db.Column(db.Integer, primary_key=True,nullable=False)    
    isactive = db.Column(db.Boolean, unique=False, nullable=False,default=True)

    filenumber = db.Column(db.String(50), unique=False, nullable=False)
    description = db.Column(db.String(500), unique=False, nullable=False)
    recordsearchfromdate = db.Column(db.DateTime, nullable=True)
    recordsearchtodate = db.Column(db.DateTime, nullable=True)

    startdate = db.Column(db.DateTime, nullable=False,default=datetime.now())
    duedate = db.Column(db.DateTime, nullable=False)
    assignedgroup = db.Column(db.String(250), unique=False, nullable=True)
    assignedto = db.Column(db.String(120), unique=False, nullable=True)
                
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=True)
    createdby = db.Column(db.String(120), unique=False, nullable=True)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)


    #ForeignKey References
    
    programareaid = db.Column(db.Integer,ForeignKey('ProgramAreas.programareaid'))
    programarea =  relationship("ProgramArea",backref=backref("ProgramAreas"),uselist=False)

    requeststatusid = db.Column(db.Integer,ForeignKey('FOIRequestStatuses.requeststatusid'))
    requeststatus =  relationship("FOIRequestStatus",backref=backref("FOIRequestStatuses"),uselist=False)

    foirequest_id =db.Column(db.Integer, db.ForeignKey('FOIRequests.foirequestid'))
    foirequestversion_id = db.Column(db.Integer, db.ForeignKey('FOIRequests.version'))    
    foirequestkey = relationship("FOIRequest",foreign_keys="[FOIMinistryRequest.foirequest_id]")
    foirequestversion = relationship("FOIRequest",foreign_keys="[FOIMinistryRequest.foirequestversion_id]")

         
    @classmethod
    def getrequest(cls,ministryrequestid):
        request_schema = FOIMinistryRequestSchema(many=True)
        query = db.session.query(FOIMinistryRequest).filter_by(foiministryrequestid=ministryrequestid).order_by(FOIMinistryRequest.version.desc()).first()
        return request_schema.dump(query)

    @classmethod
    def getrequests(cls, group = None):
        _session = db.session
        _ministryrequestids = []        
        if group is None:
            _ministryrequestids = _session.query(distinct(FOIMinistryRequest.foiministryrequestid)).filter(FOIMinistryRequest.isactive == True).all()     
        else:            
            _ministryrequestids = _session.query(distinct(FOIMinistryRequest.foiministryrequestid)).filter(FOIMinistryRequest.isactive == True , FOIMinistryRequest.assignedgroup == group).all()    

        _requests = []
        ministryrequest_schema = FOIMinistryRequestSchema()
        request_schema = FOIRequestsSchema()
        for _requestid in _ministryrequestids:
           _request ={}
           
           ministryrequest =ministryrequest_schema.dump(_session.query(FOIMinistryRequest).filter(FOIMinistryRequest.foiministryrequestid == _requestid).order_by(FOIMinistryRequest.version.desc()).first())           
           parentrequest = _session.query(FOIRequest).filter(FOIRequest.foirequestid == ministryrequest['foirequest_id'] and FOIRequest.version == ministryrequest['foirequestversion_id']).order_by(FOIRequest.version.desc()).first()
           requestapplicants = FOIRequestApplicantMapping.getrequestapplicants(ministryrequest['foirequest_id'],ministryrequest['foirequestversion_id'])
           _receivedDate = parentrequest.receiveddate
           _request["firstName"] = requestapplicants[0]['foirequestapplicant.firstname']
           _request["lastName"] = requestapplicants[0]['foirequestapplicant.lastname']
           _request["requestType"] = parentrequest.requesttype
           _request["idNumber"] = ministryrequest['filenumber']
           _request["currentState"] = ministryrequest["requeststatus.name"]
           _request["receivedDate"] = _receivedDate.strftime('%Y %b, %d')
           _request["receivedDateUF"] =str(_receivedDate)
           _request["assignedGroup"]=ministryrequest["assignedgroup"]
           _request["assignedTo"]=ministryrequest["assignedto"]
           _request["xgov"]='No'
           _request["version"] = ministryrequest['version']
           _request["id"] = parentrequest.foirequestid
           _request["ministryrequestid"] = ministryrequest['foiministryrequestid']
           _requests.append(_request)
        
        return _requests

    @classmethod
    def getrequestbyministryrequestid(cls,ministryrequestid):
        request_schema = FOIMinistryRequestSchema()
        query = db.session.query(FOIMinistryRequest).filter_by(foiministryrequestid=ministryrequestid).order_by(FOIMinistryRequest.version.desc()).first()
        return request_schema.dump(query)    

class FOIMinistryRequestSchema(ma.Schema):
    class Meta:
        fields = ('foiministryrequestid','version','filenumber','description','recordsearchfromdate','recordsearchtodate','startdate','duedate','assignedgroup','assignedto','programarea.programareaid','requeststatus.requeststatusid','foirequest.foirequestid','foirequest.requesttype','foirequest.receiveddate','foirequest.deliverymodeid','foirequest.receivedmodeid','requeststatus.requeststatusid','requeststatus.name','programarea.bcgovcode','programarea.name','foirequest_id','foirequestversion_id')
    