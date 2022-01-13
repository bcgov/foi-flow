from flask.app import Flask
from sqlalchemy.sql.schema import ForeignKey, ForeignKeyConstraint
from .db import  db, ma
from datetime import datetime
from sqlalchemy.orm import relationship,backref
from .default_method_result import DefaultMethodResult
from .FOIRequests import FOIRequest, FOIRequestsSchema
from sqlalchemy.sql.expression import distinct
from sqlalchemy import or_, and_, text

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
    description = db.Column(db.Text, unique=False, nullable=False)
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
    
    documents = relationship('FOIMinistryRequestDocument', primaryjoin="and_(FOIMinistryRequest.foiministryrequestid==FOIMinistryRequestDocument.foiministryrequest_id, "
                        "FOIMinistryRequest.version==FOIMinistryRequestDocument.foiministryrequestversion_id)")    
    extensions = relationship('FOIRequestExtension', primaryjoin="and_(FOIMinistryRequest.foiministryrequestid==FOIRequestExtension.foiministryrequest_id, "
                         "FOIMinistryRequest.version==FOIRequestExtension.foiministryrequestversion_id)")    
     
    @classmethod
    def getrequest(cls,ministryrequestid):
        request_schema = FOIMinistryRequestSchema(many=True)
        query = db.session.query(FOIMinistryRequest).filter_by(foiministryrequestid=ministryrequestid).order_by(FOIMinistryRequest.version.desc()).first()
        return request_schema.dump(query)

    @classmethod
    def getLastStatusUpdateDate(cls,foiministryrequestid,requeststatusid):
        sql = """select created_at from "FOIMinistryRequests" 
                    where foiministryrequestid = :foiministryrequestid and requeststatusid = :requeststatusid
                    order by version desc limit 1;"""
        rs = db.session.execute(text(sql), {'foiministryrequestid': foiministryrequestid, 'requeststatusid': requeststatusid})
        return [row[0] for row in rs][0]
    
    @classmethod
    def getassignmenttransition(cls,requestid):
        sql = """select version, assignedto, assignedministryperson from "FOIMinistryRequests" 
                    where foiministryrequestid = :requestid
                    order by version desc limit 2;"""
        rs = db.session.execute(text(sql), {'requestid': requestid})
        assignments = []
        for row in rs:
            assignments.append({"assignedto": row["assignedto"], "assignedministryperson": row["assignedministryperson"], "version": row["version"]})
        return assignments
    
    @classmethod
    def deActivateFileNumberVersion(cls, ministryid, idnumber, currentversion, userid)->DefaultMethodResult:
        db.session.query(FOIMinistryRequest).filter(FOIMinistryRequest.foiministryrequestid == ministryid, FOIMinistryRequest.filenumber == idnumber, FOIMinistryRequest.version != currentversion).update({"isactive": False, "updated_at": datetime.now(),"updatedby": userid}, synchronize_session=False)
        return DefaultMethodResult(True,'Request Updated',idnumber)
    
    @classmethod
    def getrequests(cls, group = None):
        _session = db.session
        _ministryrequestids = []
 
        if group is None:
            _ministryrequestids = _session.query(distinct(FOIMinistryRequest.foiministryrequestid)).filter(FOIMinistryRequest.isactive == True).all()        
        elif (group == 'Flex Team'):
            _ministryrequestids = _session.query(distinct(FOIMinistryRequest.foiministryrequestid)).filter(and_(FOIMinistryRequest.isactive == True), and_(and_(FOIMinistryRequest.assignedgroup == group),and_(FOIMinistryRequest.requeststatusid.in_([1,2,3,12,13,7,8,9,10,11,14])))).all()
        elif (group == 'Processing Team'):
            _ministryrequestids = _session.query(distinct(FOIMinistryRequest.foiministryrequestid)).filter(and_(FOIMinistryRequest.isactive == True), and_(and_(FOIMinistryRequest.assignedgroup == group),and_(FOIMinistryRequest.requeststatusid.in_([1,2,3,7,8,9,10,11,14])))).all()           
        else:
            _ministryrequestids = _session.query(distinct(FOIMinistryRequest.foiministryrequestid)).filter(and_(FOIMinistryRequest.isactive == True), or_(and_(FOIMinistryRequest.assignedgroup == group),and_(FOIMinistryRequest.assignedministrygroup == group,or_(FOIMinistryRequest.requeststatusid.in_([2,7,9,8,10,11,12,13,14]))))).all()

        _requests = []
        ministryrequest_schema = FOIMinistryRequestSchema()
        for _requestid in _ministryrequestids:
           _request ={}
           
           ministryrequest =ministryrequest_schema.dump(_session.query(FOIMinistryRequest).filter(FOIMinistryRequest.foiministryrequestid == _requestid).order_by(FOIMinistryRequest.version.desc()).first())           
           parentrequest = _session.query(FOIRequest).filter(FOIRequest.foirequestid == ministryrequest['foirequest_id'] and FOIRequest.version == ministryrequest['foirequestversion_id']).order_by(FOIRequest.version.desc()).first()
           requestapplicants = FOIRequestApplicantMapping.getrequestapplicants(ministryrequest['foirequest_id'],ministryrequest['foirequestversion_id'])
           _receiveddate = parentrequest.receiveddate
           _request["firstName"] = requestapplicants[0]['foirequestapplicant.firstname']
           _request["lastName"] = requestapplicants[0]['foirequestapplicant.lastname']
           _request["requestType"] = parentrequest.requesttype
           _request["idNumber"] = ministryrequest['filenumber']
           _request["currentState"] = ministryrequest["requeststatus.name"]
           _request["dueDate"] = ministryrequest["duedate"]
           _request["cfrDueDate"] = ministryrequest["cfrduedate"]
           _request["receivedDate"] = _receiveddate.strftime('%Y %b, %d')
           _request["receivedDateUF"] =str(_receiveddate)
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
    def getrequeststatusById(cls,ministryrequestid):
        sql = 'select foirequest_id, version, requeststatusid, created_at from "FOIMinistryRequests" fr  where foiministryrequestid = :ministryrequestid and requeststatusid != 3 order by version desc;'
        rs = db.session.execute(text(sql), {'ministryrequestid': ministryrequestid})
        summary = []
        for row in rs:
            summary.append({"requeststatusid": row["requeststatusid"], "created_at": row["created_at"], "foirequest_id": row["foirequest_id"]})
        return summary      

      
    @classmethod
    def getversionforrequest(cls,ministryrequestid):   
        return db.session.query(FOIMinistryRequest.version).filter_by(foiministryrequestid=ministryrequestid).order_by(FOIMinistryRequest.version.desc()).first()

    @classmethod
    def getstatesummary(cls, ministryrequestid):                
        sql = """select status, version from (select distinct on (fs2."name") name as status, version from "FOIMinistryRequests" fm inner join "FOIRequestStatuses" fs2 on fm.requeststatusid = fs2.requeststatusid  
        where foiministryrequestid=:ministryrequestid order by fs2."name", version asc) as fs3 order by version desc;"""
 
        rs = db.session.execute(text(sql), {'ministryrequestid': ministryrequestid})
        transitions = []
        for row in rs:
            transitions.append({"status": row["status"], "version": row["version"]})
        return transitions

    @classmethod
    def getstatenavigation(cls, ministryrequestid):                
        sql = """select fs2."name" as status, version from "FOIMinistryRequests" fm inner join "FOIRequestStatuses" fs2 on fm.requeststatusid = fs2.requeststatusid  
        where foiministryrequestid=:ministryrequestid  order by version desc limit  2"""
 
        rs = db.session.execute(text(sql), {'ministryrequestid': ministryrequestid})
        requeststates = []
        for row in rs:
            requeststates.append(row["status"])
        return requeststates

    @classmethod
    def getrequestoriginalduedate(cls,ministryrequestid):       
        return db.session.query(FOIMinistryRequest.duedate).filter(and_(FOIMinistryRequest.foiministryrequestid == ministryrequestid), and_(FOIMinistryRequest.requeststatusid == 1)).order_by(FOIMinistryRequest.version).first()[0]
         
    @classmethod
    def getupcomingcfrduerecords(cls):
        sql = """select distinct on (filenumber) filenumber, cfrduedate, foiministryrequestid, version, foirequest_id, created_at, createdby from "FOIMinistryRequests" fpa 
                    where isactive = true and cfrduedate is not null 
                    and cfrduedate between NOW()::DATE-EXTRACT(DOW FROM NOW())::INTEGER-7 AND NOW()::DATE-EXTRACT(DOW from NOW())::INTEGER+7 
                    order by filenumber , version desc;""" 
        rs = db.session.execute(text(sql))
        upcomingduerecords = []
        for row in rs:
            upcomingduerecords.append({"filenumber": row["filenumber"], "cfrduedate": row["cfrduedate"],"foiministryrequestid": row["foiministryrequestid"], "version": row["version"], "foirequest_id": row["foirequest_id"], "created_at": row["created_at"], "createdby": row["createdby"]})
        return upcomingduerecords    

    @classmethod
    def getupcominglegislativeduerecords(cls):
        sql = """select distinct on (filenumber) filenumber, duedate, foiministryrequestid, version, foirequest_id, created_at, createdby from "FOIMinistryRequests" fpa 
                    where isactive = true and duedate is not null 
                    and duedate between NOW()::DATE-EXTRACT(DOW FROM NOW())::INTEGER-7 AND NOW()::DATE-EXTRACT(DOW from NOW())::INTEGER+7 
                    order by filenumber , version desc;""" 
        rs = db.session.execute(text(sql))
        upcomingduerecords = []
        for row in rs:
            upcomingduerecords.append({"filenumber": row["filenumber"], "duedate": row["duedate"],"foiministryrequestid": row["foiministryrequestid"], "version": row["version"], "foirequest_id": row["foirequest_id"], "created_at": row["created_at"], "createdby": row["createdby"]})
        return upcomingduerecords    


class FOIMinistryRequestSchema(ma.Schema):
    class Meta:
        fields = ('foiministryrequestid','version','filenumber','description','recordsearchfromdate','recordsearchtodate','startdate','duedate','assignedgroup','assignedto','programarea.programareaid','requeststatus.requeststatusid','foirequest.foirequestid','foirequest.requesttype','foirequest.receiveddate','foirequest.deliverymodeid','foirequest.receivedmodeid','requeststatus.requeststatusid','requeststatus.name','programarea.bcgovcode','programarea.name','foirequest_id','foirequestversion_id','created_at','updated_at','createdby','assignedministryperson','assignedministrygroup','cfrduedate','closedate','closereasonid','closereason.name')
    