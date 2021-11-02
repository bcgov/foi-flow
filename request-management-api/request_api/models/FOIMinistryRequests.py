from flask.app import Flask
from sqlalchemy.sql.schema import ForeignKey, ForeignKeyConstraint
from .db import  db, ma
from datetime import datetime
from sqlalchemy.orm import relationship,backref
from .default_method_result import DefaultMethodResult
from .FOIRequests import FOIRequest, FOIRequestsSchema
from sqlalchemy.sql.expression import distinct
from sqlalchemy import or_,and_

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
    cfrduedate = db.Column(db.DateTime, nullable=True)
    assignedgroup = db.Column(db.String(250), unique=False, nullable=True)
    assignedto = db.Column(db.String(120), unique=False, nullable=True)
                
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=True)
    createdby = db.Column(db.String(120), unique=False, nullable=True)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)
    assignedministryperson = db.Column(db.String(120), unique=False, nullable=True)
    assignedministrygroup = db.Column(db.String(120), unique=False, nullable=True)
    closedate = db.Column(db.DateTime, nullable=True) 
    #ForeignKey References
    
    closereasonid = db.Column(db.Integer,ForeignKey('CloseReasons.closereasonid'))
    closereason = relationship("CloseReason",uselist=False)
    
    programareaid = db.Column(db.Integer,ForeignKey('ProgramAreas.programareaid'))
    programarea =  relationship("ProgramArea",backref=backref("ProgramAreas"),uselist=False)

    requeststatusid = db.Column(db.Integer,ForeignKey('FOIRequestStatuses.requeststatusid'))
    requeststatus =  relationship("FOIRequestStatus",backref=backref("FOIRequestStatuses"),uselist=False)

    foirequest_id =db.Column(db.Integer, db.ForeignKey('FOIRequests.foirequestid'))
    foirequestversion_id = db.Column(db.Integer, db.ForeignKey('FOIRequests.version'))    
    foirequestkey = relationship("FOIRequest",foreign_keys="[FOIMinistryRequest.foirequest_id]")
    foirequestversion = relationship("FOIRequest",foreign_keys="[FOIMinistryRequest.foirequestversion_id]")

    divisions = relationship('FOIMinistryRequestDivision', primaryjoin="and_(FOIMinistryRequest.foiministryrequestid==FOIMinistryRequestDivision.foiministryrequest_id, "
                        "FOIMinistryRequest.version==FOIMinistryRequestDivision.foiministryrequestversion_id)") 
    @classmethod
    def getrequest(cls,ministryrequestid):
        request_schema = FOIMinistryRequestSchema(many=True)
        query = db.session.query(FOIMinistryRequest).filter_by(foiministryrequestid=ministryrequestid).order_by(FOIMinistryRequest.version.desc()).first()
        return request_schema.dump(query)
    
    @classmethod
    def deActivateFileNumberVersion(cls, ministryId, idnumber, currentVersion, userId)->DefaultMethodResult:
        db.session.query(FOIMinistryRequest).filter(FOIMinistryRequest.foiministryrequestid == ministryId, FOIMinistryRequest.filenumber == idnumber, FOIMinistryRequest.version != currentVersion).update({"isactive": False, "updated_at": datetime.now(),"updatedby": userId}, synchronize_session=False)
        return DefaultMethodResult(True,'Request Updated',idnumber)
    
    @classmethod
    def getrequests(cls, group = None):
        _session = db.session
        _ministryrequestids = [] 
        if group is None:
            _ministryrequestids = _session.query(distinct(FOIMinistryRequest.foiministryrequestid)).filter(FOIMinistryRequest.isactive == True and FOIMinistryRequest.requeststatusid != 3).all()
        else:  
            _ministryrequestids = _session.query(distinct(FOIMinistryRequest.foiministryrequestid)).filter(and_(FOIMinistryRequest.requeststatusid != 3,FOIMinistryRequest.isactive == True), or_(and_(FOIMinistryRequest.requeststatusid != 3, FOIMinistryRequest.assignedgroup == group),and_(FOIMinistryRequest.assignedministrygroup == group,or_(FOIMinistryRequest.requeststatusid.in_([2,7,9,8,10]))))).all()

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
           _request["dueDate"] = ministryrequest["duedate"]
           _request["cfrDueDate"] = ministryrequest["cfrduedate"]
           _request["receivedDate"] = _receivedDate.strftime('%Y %b, %d')
           _request["receivedDateUF"] =str(_receivedDate)
           _request["assignedGroup"]=ministryrequest["assignedgroup"]
           _request["assignedTo"]=ministryrequest["assignedto"]
           _request["assignedministrygroup"]=ministryrequest["assignedministrygroup"]
           _request["assignedministryperson"]=ministryrequest["assignedministryperson"]
           _request["xgov"]='No'
           _request["version"] = ministryrequest['version']
           _request["id"] = parentrequest.foirequestid
           _request["ministryrequestid"] = ministryrequest['foiministryrequestid']
           _request["applicantcategory"]=parentrequest.applicantcategory.name
           _requests.append(_request)
        
        return _requests

    @classmethod
    def getrequestbyministryrequestid(cls,ministryrequestid):
        request_schema = FOIMinistryRequestSchema()
        query = db.session.query(FOIMinistryRequest).filter_by(foiministryrequestid=ministryrequestid).order_by(FOIMinistryRequest.version.desc()).first()
        return request_schema.dump(query) 
    
    @classmethod
    def getrequestbyfilenumberandversion(cls,filenumber, version):
        request_schema = FOIMinistryRequestSchema()
        query = db.session.query(FOIMinistryRequest).filter_by(filenumber=filenumber, version = version).order_by(FOIMinistryRequest.version.desc()).first()
        return request_schema.dump(query)   
    
    @classmethod
    def getrequestById(cls,ministryrequestid):
        request_schema = FOIMinistryRequestSchema(many=True)
        query = db.session.query(FOIMinistryRequest).filter_by(foiministryrequestid=ministryrequestid).order_by(FOIMinistryRequest.version.asc())
        return request_schema.dump(query)   
    
    @classmethod
    def getversionforrequest(cls,ministryrequestid):   
       return db.session.query(FOIMinistryRequest.version).filter_by(foiministryrequestid=ministryrequestid).order_by(FOIMinistryRequest.version.desc()).first()

class FOIMinistryRequestSchema(ma.Schema):
    class Meta:
        fields = ('foiministryrequestid','version','filenumber','description','recordsearchfromdate','recordsearchtodate','startdate','duedate','assignedgroup','assignedto','programarea.programareaid','requeststatus.requeststatusid','foirequest.foirequestid','foirequest.requesttype','foirequest.receiveddate','foirequest.deliverymodeid','foirequest.receivedmodeid','requeststatus.requeststatusid','requeststatus.name','programarea.bcgovcode','programarea.name','foirequest_id','foirequestversion_id','created_at','updated_at','createdby','assignedministryperson','assignedministrygroup','cfrduedate','closedate','closereasonid','closereason.name')
    