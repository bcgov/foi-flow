from flask.app import Flask
from sqlalchemy.sql.schema import ForeignKey, ForeignKeyConstraint
from .db import  db, ma
from datetime import datetime
from sqlalchemy.orm import relationship, backref, aliased
from .default_method_result import DefaultMethodResult
from .FOIRequests import FOIRequest, FOIRequestsSchema
from sqlalchemy.sql.expression import distinct
from sqlalchemy import or_, and_, text, func, literal, cast, case, nullslast, nullsfirst, desc, asc
from sqlalchemy.sql.sqltypes import String
from sqlalchemy.dialects.postgresql import JSON

from .FOIRequestApplicantMappings import FOIRequestApplicantMapping
from .FOIRequestApplicants import FOIRequestApplicant
from .FOIRequestStatus import FOIRequestStatus
from .ApplicantCategories import ApplicantCategory
from .FOIRequestWatchers import FOIRequestWatcher
from .FOIRestrictedMinistryRequests import FOIRestrictedMinistryRequest
from .ProgramAreas import ProgramArea
from request_api.utils.enums import ProcessingTeamWithKeycloackGroup, IAOTeamWithKeycloackGroup
from .FOIAssignees import FOIAssignee
from .FOIRequestExtensions import FOIRequestExtension
from request_api.utils.enums import RequestorType
import logging
from sqlalchemy.sql.sqltypes import Date
from dateutil import parser
from request_api.utils.enums import StateName
from .FOIMinistryRequestSubjectCodes import FOIMinistryRequestSubjectCode
from .SubjectCodes import SubjectCode
from .FOIRequestOIPC import FOIRequestOIPC

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

    startdate = db.Column(db.DateTime, nullable=False,default=datetime.now)
    duedate = db.Column(db.DateTime, nullable=False)
    cfrduedate = db.Column(db.DateTime, nullable=True)
    originalldd = db.Column(db.DateTime, nullable=True)
    assignedgroup = db.Column(db.String(250), unique=False, nullable=True)
    assignedto = db.Column(db.String(120), ForeignKey('FOIAssignees.username'), unique=False, nullable=True)
                
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=True)
    createdby = db.Column(db.String(120), unique=False, nullable=True)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)
    assignedministryperson = db.Column(db.String(120), ForeignKey('FOIAssignees.username'), unique=False, nullable=True)
    assignedministrygroup = db.Column(db.String(120), unique=False, nullable=True)
    closedate = db.Column(db.DateTime, nullable=True)

    axissyncdate = db.Column(db.DateTime, nullable=True)    
    axisrequestid = db.Column(db.String(120), nullable=True)
    requestpagecount = db.Column(db.String(20), nullable=True)
    linkedrequests = db.Column(JSON, unique=False, nullable=True)
    identityverified = db.Column(JSON, unique=False, nullable=True)
    ministrysignoffapproval = db.Column(JSON, unique=False, nullable=True)
    

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
    
    oipcreviews = relationship('FOIRequestOIPC', primaryjoin="and_(FOIMinistryRequest.foiministryrequestid==FOIRequestOIPC.foiministryrequest_id, "
                         "FOIMinistryRequest.version==FOIRequestOIPC.foiministryrequestversion_id)")    
    
    assignee = relationship('FOIAssignee', foreign_keys="[FOIMinistryRequest.assignedto]")
    ministryassignee = relationship('FOIAssignee', foreign_keys="[FOIMinistryRequest.assignedministryperson]")

    subjectcode = relationship('FOIMinistryRequestSubjectCode', primaryjoin="and_(FOIMinistryRequest.foiministryrequestid==FOIMinistryRequestSubjectCode.foiministryrequestid, "
                        "FOIMinistryRequest.version==FOIMinistryRequestSubjectCode.foiministryrequestversion)") 
    isofflinepayment = db.Column(db.Boolean, unique=False, nullable=True,default=False)

    isoipcreview = db.Column(db.Boolean, unique=False, nullable=True,default=False)

    @classmethod
    def getrequest(cls,ministryrequestid):
        request_schema = FOIMinistryRequestSchema(many=False)
        query = db.session.query(FOIMinistryRequest).filter_by(foiministryrequestid=ministryrequestid).order_by(FOIMinistryRequest.version.desc()).first()
        return request_schema.dump(query)

    @classmethod
    def getLastStatusUpdateDate(cls,foiministryrequestid,requeststatusid):
        statusdate = None
        try:
            sql = """select created_at from "FOIMinistryRequests" 
                    where foiministryrequestid = :foiministryrequestid and requeststatusid = :requeststatusid
                    order by version desc limit 1;"""
            rs = db.session.execute(text(sql), {'foiministryrequestid': foiministryrequestid, 'requeststatusid': requeststatusid})
            statusdate = [row[0] for row in rs][0]
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return statusdate

 
    
    @classmethod
    def getassignmenttransition(cls,requestid):
        assignments = []
        try:
            sql = """select version, assignedto, assignedministryperson from "FOIMinistryRequests" 
                    where foiministryrequestid = :requestid
                    order by version desc limit 2;"""
            rs = db.session.execute(text(sql), {'requestid': requestid})
            for row in rs:
                assignments.append({"assignedto": row["assignedto"], "assignedministryperson": row["assignedministryperson"], "version": row["version"]})
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return assignments
    
    @classmethod
    def deActivateFileNumberVersion(cls, ministryid, idnumber, userid)->DefaultMethodResult:
        try:
            sql = """update "FOIMinistryRequests" set isactive = false, updatedby = :userid, updated_at = now()  
                        where foiministryrequestid = :ministryid and isactive = true and filenumber = :idnumber 
                        and version != (select version from "FOIMinistryRequests" fr where foiministryrequestid = :ministryid order by "version" desc limit 1)"""
            db.session.execute(text(sql), {'ministryid': ministryid, 'userid':userid, 'idnumber': idnumber})
            db.session.commit()
            return DefaultMethodResult(True,'Request Updated',idnumber)
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()   
    
    @classmethod
    def getrequests(cls, group = None):
        _session = db.session
        _ministryrequestids = []
 
        if group is None:
            _ministryrequestids = _session.query(distinct(FOIMinistryRequest.foiministryrequestid)).filter(FOIMinistryRequest.isactive == True).all()        
        elif (group == IAOTeamWithKeycloackGroup.flex.value):
            _ministryrequestids = _session.query(distinct(FOIMinistryRequest.foiministryrequestid)).filter(and_(FOIMinistryRequest.isactive == True), and_(and_(FOIMinistryRequest.assignedgroup == group),and_(FOIMinistryRequest.requeststatusid.in_([1,2,3,12,13,7,8,9,10,11,14,16,17,18])))).all()
        elif (group in ProcessingTeamWithKeycloackGroup.list()):
            _ministryrequestids = _session.query(distinct(FOIMinistryRequest.foiministryrequestid)).filter(and_(FOIMinistryRequest.isactive == True), and_(and_(FOIMinistryRequest.assignedgroup == group),and_(FOIMinistryRequest.requeststatusid.in_([1,2,3,7,8,9,10,11,14,16,17,18])))).all()           
        else:
            _ministryrequestids = _session.query(distinct(FOIMinistryRequest.foiministryrequestid)).filter(and_(FOIMinistryRequest.isactive == True), or_(and_(FOIMinistryRequest.assignedgroup == group),and_(FOIMinistryRequest.assignedministrygroup == group,or_(FOIMinistryRequest.requeststatusid.in_([2,7,9,8,10,11,12,13,14,16,17,18]))))).all()

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
           _request["axisRequestId"] = ministryrequest['axisrequestid']
           _request["linkedrequests"] = ministryrequest['linkedrequests']
           _request["currentState"] = ministryrequest["requeststatus.name"]
           _request["dueDate"] = ministryrequest["duedate"]
           _request["cfrDueDate"] = ministryrequest["cfrduedate"] 
           _request["originalDueDate"] = ministryrequest["originalldd"] 
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
           _request["identityverified"] = ministryrequest['identityverified']
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
        summary = []
        try:
            sql = 'select foirequest_id, version, requeststatusid, created_at from "FOIMinistryRequests" fr  where foiministryrequestid = :ministryrequestid and requeststatusid != 3 order by version desc;'
            rs = db.session.execute(text(sql), {'ministryrequestid': ministryrequestid})        
            for row in rs:
                summary.append({"requeststatusid": row["requeststatusid"], "created_at": row["created_at"], "foirequest_id": row["foirequest_id"]})
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return summary      

      
    @classmethod
    def getversionforrequest(cls,ministryrequestid):   
        return db.session.query(FOIMinistryRequest.version).filter_by(foiministryrequestid=ministryrequestid).order_by(FOIMinistryRequest.version.desc()).first()

    @classmethod
    def getstatesummary(cls, ministryrequestid):  
        transitions = []
        try:
            """              
            sql =select status, version from (select distinct name as status, version from "FOIMinistryRequests" fm inner join "FOIRequestStatuses" fs2 on fm.requeststatusid = fs2.requeststatusid  
            where foiministryrequestid=:ministryrequestid order by version asc) as fs3 order by version desc;
            """
            sql = """select fm2.version, fs2."name" as status from  "FOIMinistryRequests" fm2  inner join "FOIRequestStatuses" fs2 on fm2.requeststatusid = fs2.requeststatusid 
                        where fm2.foiministryrequestid=:ministryrequestid order by version desc"""
            rs = db.session.execute(text(sql), {'ministryrequestid': ministryrequestid})  
            _tmp_state = None       
            for row in rs:
                if row["status"] != _tmp_state:
                    transitions.append({"status": row["status"], "version": row["version"]})
                    _tmp_state = row["status"]
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return transitions

    @classmethod
    def getlastoffholddate(cls, ministryrequestid):  
        transitions = []
        try:
            sql = """select fm2.version, fs2."name" as status, fm2.created_at from  "FOIMinistryRequests" fm2  inner join "FOIRequestStatuses" fs2 on fm2.requeststatusid = fs2.requeststatusid 
                        where fm2.foiministryrequestid=:ministryrequestid order by version asc"""
            rs = db.session.execute(text(sql), {'ministryrequestid': ministryrequestid})  
            _tmp_state = None       
            for row in rs:
                if row["status"] != _tmp_state:
                    transitions.append({"status": row["status"], "version": row["version"], "created_at": row["created_at"]})
                    _tmp_state = row["status"]
            desc_transitions = transitions[::-1]
            index = 0
            onhold_occurance = 0
            recent_offhold_index = None
            offhold_indicator = False
            for entry in desc_transitions:
                if entry["status"] == StateName.onhold.value:
                    onhold_occurance = onhold_occurance + 1
                    if onhold_occurance > 1:
                        recent_offhold_index = index
                        offhold_indicator = True
                index = index + 1     
            return None if offhold_indicator == False or recent_offhold_index == 0 else desc_transitions[recent_offhold_index-1]["created_at"]
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()

    @classmethod
    def getstatenavigation(cls, ministryrequestid): 
        requeststates = []
        try:
            sql = """select fs2."name" as status, version from "FOIMinistryRequests" fm inner join "FOIRequestStatuses" fs2 on fm.requeststatusid = fs2.requeststatusid  
            where foiministryrequestid=:ministryrequestid  order by version desc limit  2"""
            rs = db.session.execute(text(sql), {'ministryrequestid': ministryrequestid})
            for row in rs:
                requeststates.append(row["status"])
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return requeststates
    
    @classmethod
    def getallstatenavigation(cls, ministryrequestid): 
        requeststates = []    
        try:           
            sql = """select fs2."name" as status, version from "FOIMinistryRequests" fm inner join "FOIRequestStatuses" fs2 on fm.requeststatusid = fs2.requeststatusid  
            where foiministryrequestid=:ministryrequestid  order by version desc""" 
            rs = db.session.execute(text(sql), {'ministryrequestid': ministryrequestid})        
            for row in rs:
                requeststates.append(row["status"])
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return requeststates

    @classmethod
    def getrequestssubquery(cls, groups, filterfields, keyword, additionalfilter, userid, iaoassignee, ministryassignee, requestby='IAO', isiaorestrictedfilemanager=False, isministryrestrictedfilemanager=False):
        #for queue/dashboard

        _session = db.session

        #ministry filter for group/team
        ministryfilter = FOIMinistryRequest.getgroupfilters(groups)

        #subquery for getting latest version & proper group/team for FOIMinistryRequest
        subquery_ministry_maxversion = _session.query(FOIMinistryRequest.foiministryrequestid, func.max(FOIMinistryRequest.version).label('max_version')).group_by(FOIMinistryRequest.foiministryrequestid).subquery()
        joincondition_ministry = [
            subquery_ministry_maxversion.c.foiministryrequestid == FOIMinistryRequest.foiministryrequestid,
            subquery_ministry_maxversion.c.max_version == FOIMinistryRequest.version,
        ]

        #subquery for getting extension count
        subquery_extension_count = _session.query(FOIRequestExtension.foiministryrequest_id, func.count(distinct(FOIRequestExtension.foirequestextensionid)).filter(FOIRequestExtension.isactive == True).label('extensions')).group_by(FOIRequestExtension.foiministryrequest_id).subquery()

        #aliase for onbehalf of applicant info
        onbehalf_applicantmapping = aliased(FOIRequestApplicantMapping)
        onbehalf_applicant = aliased(FOIRequestApplicant)

        #aliase for getting ministry restricted flag from FOIRestrictedMinistryRequest
        ministry_restricted_requests = aliased(FOIRestrictedMinistryRequest)

        #filter/search
        if(len(filterfields) > 0 and keyword is not None):
            filtercondition = []

            if(keyword != "restricted"):
                for field in filterfields:
                    filtercondition.append(FOIMinistryRequest.findfield(field, iaoassignee, ministryassignee).ilike('%'+keyword+'%'))
            else:
                if(requestby == 'IAO'):
                    filtercondition.append(FOIRestrictedMinistryRequest.isrestricted == True)
                else:
                    filtercondition.append(ministry_restricted_requests.isrestricted == True)
            if (keyword.lower() == "oipc"):
                filtercondition.append(FOIMinistryRequest.isoipcreview == True)

        intakesorting = case([
                            (and_(FOIMinistryRequest.assignedto == None, FOIMinistryRequest.assignedgroup == 'Intake Team'), # Unassigned requests first
                             literal(None)),
                           ],
                           else_ = FOIRequest.receiveddate).label('intakeSorting')

        defaultsorting = case([
                            (FOIMinistryRequest.assignedto == None, # Unassigned requests first
                             literal(None)),
                           ],
                           else_ = FOIMinistryRequest.duedate).label('defaultSorting')

        ministrysorting = case([
                            (FOIMinistryRequest.assignedministryperson == None, # Unassigned requests first
                             literal(None)),
                           ],
                           else_ = FOIMinistryRequest.duedate).label('ministrySorting')

        assignedtoformatted = case([
                            (and_(iaoassignee.lastname.isnot(None), iaoassignee.firstname.isnot(None)),
                             func.concat(iaoassignee.lastname, ', ', iaoassignee.firstname)),
                            (and_(iaoassignee.lastname.isnot(None), iaoassignee.firstname.is_(None)),
                             iaoassignee.lastname),
                            (and_(iaoassignee.lastname.is_(None), iaoassignee.firstname.isnot(None)),
                             iaoassignee.firstname),
                           ],
                           else_ = FOIMinistryRequest.assignedgroup).label('assignedToFormatted')

        ministryassignedtoformatted = case([
                            (and_(ministryassignee.lastname.isnot(None), ministryassignee.firstname.isnot(None)),
                             func.concat(ministryassignee.lastname, ', ', ministryassignee.firstname)),
                            (and_(ministryassignee.lastname.isnot(None), ministryassignee.firstname.is_(None)),
                             ministryassignee.lastname),
                            (and_(ministryassignee.lastname.is_(None), ministryassignee.firstname.isnot(None)),
                             ministryassignee.firstname),
                           ],
                           else_ = FOIMinistryRequest.assignedministrygroup).label('ministryAssignedToFormatted')
        
        duedate = case([
                            (FOIMinistryRequest.requeststatusid == 11,  # On Hold
                             literal(None)),
                           ],
                           else_ = cast(FOIMinistryRequest.duedate, String)).label('duedate')
        
        cfrduedate = case([
                            (FOIMinistryRequest.requeststatusid == 11,  # On Hold
                             literal(None)),
                           ],
                           else_ = cast(FOIMinistryRequest.cfrduedate, String)).label('cfrduedate')

        requestpagecount = case([
            (FOIMinistryRequest.requestpagecount.is_(None),
            '0'),
            ],
            else_ = cast(FOIMinistryRequest.requestpagecount, String)).label('requestPageCount')

        onbehalfformatted = case([
                            (and_(onbehalf_applicant.lastname.isnot(None), onbehalf_applicant.firstname.isnot(None)),
                             func.concat(onbehalf_applicant.lastname, ', ', onbehalf_applicant.firstname)),
                            (and_(onbehalf_applicant.lastname.isnot(None), onbehalf_applicant.firstname.is_(None)),
                             onbehalf_applicant.lastname),
                            (and_(onbehalf_applicant.lastname.is_(None), onbehalf_applicant.firstname.isnot(None)),
                             onbehalf_applicant.firstname),
                           ],
                           else_ = 'N/A').label('onBehalfFormatted')
        
        extensions = case([
                            (subquery_extension_count.c.extensions.is_(None),
                             0),
                           ],
                           else_ = subquery_extension_count.c.extensions).label('extensions')


        selectedcolumns = [
            FOIRequest.foirequestid.label('id'),
            FOIMinistryRequest.version,
            literal(None).label('sourceofsubmission'),
            FOIRequestApplicant.firstname.label('firstName'),
            FOIRequestApplicant.lastname.label('lastName'),
            FOIRequest.requesttype.label('requestType'),
            cast(FOIRequest.receiveddate, String).label('receivedDate'),
            cast(FOIRequest.receiveddate, String).label('receivedDateUF'),
            FOIRequestStatus.name.label('currentState'),
            FOIMinistryRequest.assignedgroup.label('assignedGroup'),
            FOIMinistryRequest.assignedto.label('assignedTo'),
            cast(FOIMinistryRequest.filenumber, String).label('idNumber'),
            cast(FOIMinistryRequest.axisrequestid, String).label('axisRequestId'),
            requestpagecount,
            FOIMinistryRequest.foiministryrequestid.label('ministryrequestid'),
            FOIMinistryRequest.assignedministrygroup.label('assignedministrygroup'),
            FOIMinistryRequest.assignedministryperson.label('assignedministryperson'),
            cfrduedate,
            duedate,
            ApplicantCategory.name.label('applicantcategory'),
            FOIRequest.created_at.label('created_at'),
            func.lower(ProgramArea.bcgovcode).label('bcgovcode'),
            iaoassignee.firstname.label('assignedToFirstName'),
            iaoassignee.lastname.label('assignedToLastName'),
            ministryassignee.firstname.label('assignedministrypersonFirstName'),
            ministryassignee.lastname.label('assignedministrypersonLastName'),
            FOIMinistryRequest.description,
            cast(FOIMinistryRequest.recordsearchfromdate, String).label('recordsearchfromdate'),
            cast(FOIMinistryRequest.recordsearchtodate, String).label('recordsearchtodate'),
            onbehalf_applicant.firstname.label('onBehalfFirstName'),
            onbehalf_applicant.lastname.label('onBehalfLastName'),
            defaultsorting,
            intakesorting,
            ministrysorting,
            assignedtoformatted,
            ministryassignedtoformatted,
            FOIMinistryRequest.closedate,
            onbehalfformatted,
            extensions,
            FOIRestrictedMinistryRequest.isrestricted.label('isiaorestricted'),
            ministry_restricted_requests.isrestricted.label('isministryrestricted'),
            SubjectCode.name.label('subjectcode'),
            FOIMinistryRequest.isoipcreview.label('isoipcreview'),
            literal(None).label('oipc_number'),
        ]

        basequery = _session.query(
                                *selectedcolumns
                            ).join(
                                subquery_ministry_maxversion,
                                and_(*joincondition_ministry)
                            ).join(
                                subquery_extension_count,
                                subquery_extension_count.c.foiministryrequest_id == FOIMinistryRequest.foiministryrequestid,
                                isouter=True
                            ).join(
                                FOIRequest,
                                and_(FOIRequest.foirequestid == FOIMinistryRequest.foirequest_id, FOIRequest.version == FOIMinistryRequest.foirequestversion_id)
                            ).join(
                                FOIRequestStatus,
                                FOIRequestStatus.requeststatusid == FOIMinistryRequest.requeststatusid
                            ).join(
                                FOIRequestApplicantMapping,
                                and_(FOIRequestApplicantMapping.foirequest_id == FOIMinistryRequest.foirequest_id, FOIRequestApplicantMapping.foirequestversion_id == FOIMinistryRequest.foirequestversion_id, FOIRequestApplicantMapping.requestortypeid == RequestorType['applicant'].value)
                            ).join(
                                FOIRequestApplicant,
                                FOIRequestApplicant.foirequestapplicantid == FOIRequestApplicantMapping.foirequestapplicantid
                            ).join(
                                onbehalf_applicantmapping,
                                and_(
                                    onbehalf_applicantmapping.foirequest_id == FOIMinistryRequest.foirequest_id, 
                                    onbehalf_applicantmapping.foirequestversion_id == FOIMinistryRequest.foirequestversion_id, 
                                    onbehalf_applicantmapping.requestortypeid == RequestorType['onbehalfof'].value),
                                isouter=True
                            ).join(
                                onbehalf_applicant,
                                onbehalf_applicant.foirequestapplicantid == onbehalf_applicantmapping.foirequestapplicantid,  
                                isouter=True
                            ).join(
                                ApplicantCategory,
                                and_(ApplicantCategory.applicantcategoryid == FOIRequest.applicantcategoryid, ApplicantCategory.isactive == True)
                            ).join(
                                ProgramArea,
                                FOIMinistryRequest.programareaid == ProgramArea.programareaid
                            ).join(
                                iaoassignee,
                                iaoassignee.username == FOIMinistryRequest.assignedto,
                                isouter=True
                            ).join(
                                ministryassignee,
                                ministryassignee.username == FOIMinistryRequest.assignedministryperson,
                                isouter=True
                            ).join(
                                FOIRestrictedMinistryRequest,
                                and_(
                                    FOIRestrictedMinistryRequest.ministryrequestid == FOIMinistryRequest.foiministryrequestid,
                                    FOIRestrictedMinistryRequest.type == 'iao',
                                    FOIRestrictedMinistryRequest.isactive == True),
                                isouter=True
                            ).join(
                                ministry_restricted_requests,
                                and_(
                                    ministry_restricted_requests.ministryrequestid == FOIMinistryRequest.foiministryrequestid,
                                    ministry_restricted_requests.type == 'ministry',
                                    ministry_restricted_requests.isactive == True),
                                isouter=True
                            ).join(
                                FOIMinistryRequestSubjectCode,
                                and_(FOIMinistryRequestSubjectCode.foiministryrequestid == FOIMinistryRequest.foiministryrequestid, FOIMinistryRequestSubjectCode.foiministryrequestversion == FOIMinistryRequest.version),
                                isouter=True
                            ).join(
                                SubjectCode,
                                SubjectCode.subjectcodeid == FOIMinistryRequestSubjectCode.subjectcodeid,
                                isouter=True
                            ).filter(or_(FOIMinistryRequest.requeststatusid != 3, and_(FOIMinistryRequest.isoipcreview == True, FOIMinistryRequest.requeststatusid == 3)))
                            
                        

        if(additionalfilter == 'watchingRequests'):
            #watchby
            activefilter = and_(FOIMinistryRequest.isactive == True, FOIRequestStatus.isactive == True)

            subquery_watchby = FOIRequestWatcher.getrequestidsbyuserid(userid)
            dbquery = basequery.join(subquery_watchby, subquery_watchby.c.ministryrequestid == FOIMinistryRequest.foiministryrequestid).filter(activefilter)
        elif(additionalfilter == 'myRequests'):
            #myrequest
            if(requestby == 'IAO'):
                dbquery = basequery.filter(FOIMinistryRequest.assignedto == userid).filter(ministryfilter)
            else:
                dbquery = basequery.filter(FOIMinistryRequest.assignedministryperson == userid).filter(ministryfilter)
        else:
            if(isiaorestrictedfilemanager == True or isministryrestrictedfilemanager == True):
                dbquery = basequery.filter(ministryfilter)
            else:
                if(requestby == 'IAO'):
                    dbquery = basequery.filter(or_(or_(FOIRestrictedMinistryRequest.isrestricted == False, FOIRestrictedMinistryRequest.isrestricted == None), and_(FOIRestrictedMinistryRequest.isrestricted == True, FOIMinistryRequest.assignedto == userid))).filter(ministryfilter)
                else:
                    dbquery = basequery.filter(or_(or_(ministry_restricted_requests.isrestricted == False, ministry_restricted_requests.isrestricted == None), and_(ministry_restricted_requests.isrestricted == True, FOIMinistryRequest.assignedministryperson == userid))).filter(ministryfilter)


        if(keyword is None):
            return dbquery
        else:
            return dbquery.filter(or_(*filtercondition))

    @classmethod
    def getrequestspagination(cls, group, page, size, sortingitems, sortingorders, filterfields, keyword, additionalfilter, userid, isiaorestrictedfilemanager, isministryrestrictedfilemanager):
        iaoassignee = aliased(FOIAssignee)
        ministryassignee = aliased(FOIAssignee)
        requestby = 'Ministry'

        subquery = FOIMinistryRequest.getrequestssubquery(group, filterfields, keyword, additionalfilter, userid, iaoassignee, ministryassignee, requestby, isiaorestrictedfilemanager, isministryrestrictedfilemanager)

        #sorting
        sortingcondition = FOIMinistryRequest.getsorting(sortingitems, sortingorders, iaoassignee, ministryassignee)

        return subquery.order_by(*sortingcondition).paginate(page=page, per_page=size)
    
    @classmethod
    def getsorting(cls, sortingitems, sortingorders, iaoassignee, ministryassignee):
        #sorting
        sortingcondition = []
        if(len(sortingitems) > 0 and len(sortingorders) > 0 and len(sortingitems) == len(sortingorders)):
            for field in sortingitems:
                order = sortingorders.pop(0)
                sortingcondition.append(FOIMinistryRequest.getfieldforsorting(field, order, iaoassignee, ministryassignee))

        #default sorting
        if(len(sortingcondition) == 0):
            sortingcondition.append(FOIMinistryRequest.findfield('currentState', iaoassignee, ministryassignee).asc())

        #always sort by created_at last to prevent pagination collisions
        sortingcondition.append(asc('created_at'))
        
        return sortingcondition
    
    @classmethod
    def getfieldforsorting(cls, field, order, iaoassignee, ministryassignee):
        #get one field
        customizedfields = ['assignedToFormatted', 'ministryAssignedToFormatted', 'duedate', 'cfrduedate', 'ministrySorting', 'onBehalfFormatted', 'extensions', 'isministryrestricted']
        if(field in customizedfields):
            if(order == 'desc'):
                return nullslast(desc(field))
            else:
                return nullsfirst(asc(field))
        else:
            if(order == 'desc'):
                return nullslast(FOIMinistryRequest.findfield(field, iaoassignee, ministryassignee).desc())
            else:
                return nullsfirst(FOIMinistryRequest.findfield(field, iaoassignee, ministryassignee).asc())

    @classmethod
    def findfield(cls, x, iaoassignee, ministryassignee):
        #add more fields here if need sort/filter/search more columns

        return {
            'firstName': FOIRequestApplicant.firstname,
            'lastName': FOIRequestApplicant.lastname,
            'requestType': FOIRequest.requesttype,
            'idNumber': FOIMinistryRequest.filenumber,
            'axisRequestId': FOIMinistryRequest.axisrequestid,
            'axisrequest_number': FOIMinistryRequest.axisrequestid,
            'rawRequestNumber': FOIMinistryRequest.filenumber,
            'currentState': FOIRequestStatus.name,
            'assignedTo': FOIMinistryRequest.assignedto,
            'receivedDate': FOIRequest.receiveddate,
            'receivedDateUF': FOIRequest.receiveddate,
            'applicantcategory': ApplicantCategory.name,
            'assignedministryperson': FOIMinistryRequest.assignedministryperson,
            'assignedToFirstName': iaoassignee.firstname,
            'assignedToLastName': iaoassignee.lastname,
            'assignedministrypersonFirstName': ministryassignee.firstname,
            'assignedministrypersonLastName': ministryassignee.lastname,
            'description': FOIMinistryRequest.description,
            'requestdescription': FOIMinistryRequest.description,
            'duedate': FOIMinistryRequest.duedate,
            'cfrduedate': FOIMinistryRequest.cfrduedate,
            'DueDateValue': FOIMinistryRequest.duedate,
            'DaysLeftValue': FOIMinistryRequest.duedate,
            'ministry': func.upper(ProgramArea.bcgovcode),
            'requestPageCount': FOIMinistryRequest.requestpagecount,
            'closedate': FOIMinistryRequest.closedate,
            'subjectcode': SubjectCode.name,
            'isoipcreview': FOIMinistryRequest.isoipcreview
        }.get(x, FOIMinistryRequest.axisrequestid)

    @classmethod
    def getgroupfilters(cls, groups):
        #ministry filter for group/team
        if groups is None:
            ministryfilter = FOIMinistryRequest.isactive == True
        else:
            groupfilter = []
            for group in groups:
                if (group == IAOTeamWithKeycloackGroup.flex.value or group in ProcessingTeamWithKeycloackGroup.list()):
                    groupfilter.append(
                        and_(
                            FOIMinistryRequest.assignedgroup == group
                        )
                    )
                elif (group == IAOTeamWithKeycloackGroup.intake.value):
                    groupfilter.append(
                        or_(
                            FOIMinistryRequest.assignedgroup == group,
                            and_(
                                FOIMinistryRequest.assignedgroup == IAOTeamWithKeycloackGroup.flex.value,
                                FOIMinistryRequest.requeststatusid.in_([1])
                            )
                        )
                    )
                else:
                    groupfilter.append(
                        or_(
                            FOIMinistryRequest.assignedgroup == group,
                            and_(
                                FOIMinistryRequest.assignedministrygroup == group,
                                FOIMinistryRequest.requeststatusid.in_([2,7,9,8,10,11,12,13,14,16,17,18])
                            )
                        )
                    )

            ministryfilter = and_(
                                FOIMinistryRequest.isactive == True,
                                FOIRequestStatus.isactive == True,
                                or_(*groupfilter)
                            )
        
        return ministryfilter

    @classmethod
    def getrequestoriginalduedate(cls,ministryrequestid):       
        return db.session.query(FOIMinistryRequest.duedate).filter(FOIMinistryRequest.foiministryrequestid == ministryrequestid, FOIMinistryRequest.requeststatusid == 1).order_by(FOIMinistryRequest.version).first()[0]

    @classmethod
    def getduedate(cls,ministryrequestid):
        return db.session.query(FOIMinistryRequest.duedate).filter(FOIMinistryRequest.foiministryrequestid == ministryrequestid).order_by(FOIMinistryRequest.version.desc()).first()[0]

   
    @classmethod
    def getupcomingcfrduerecords(cls):
        upcomingduerecords = []
        try:
            sql = """select distinct on (filenumber) filenumber, to_char(cfrduedate, 'YYYY-MM-DD') as cfrduedate, foiministryrequestid, version, foirequest_id, created_at, createdby from "FOIMinistryRequests" fpa 
                    where isactive = true and cfrduedate is not null and requeststatusid = 2  
                    and cfrduedate between  NOW() - INTERVAL '7 DAY' AND NOW() + INTERVAL '7 DAY'
                    order by filenumber , version desc;""" 
            rs = db.session.execute(text(sql))            
            for row in rs:
                upcomingduerecords.append({"filenumber": row["filenumber"], "cfrduedate": row["cfrduedate"],"foiministryrequestid": row["foiministryrequestid"], "version": row["version"], "foirequest_id": row["foirequest_id"], "created_at": row["created_at"], "createdby": row["createdby"]})
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return upcomingduerecords    

    @classmethod
    def getupcominglegislativeduerecords(cls):
        upcomingduerecords = []
        try:
            sql = """select distinct on (filenumber) filenumber, to_char(duedate, 'YYYY-MM-DD') as duedate, foiministryrequestid, version, foirequest_id, created_at, createdby from "FOIMinistryRequests" fpa 
                    where isactive = true and duedate is not null and requeststatusid not in (5,6,4,11,3,15)     
                    and duedate between  NOW() - INTERVAL '7 DAY' AND NOW() + INTERVAL '7 DAY'
                    order by filenumber , version desc;""" 
            rs = db.session.execute(text(sql))        
            for row in rs:
                upcomingduerecords.append({"filenumber": row["filenumber"], "duedate": row["duedate"],"foiministryrequestid": row["foiministryrequestid"], "version": row["version"], "foirequest_id": row["foirequest_id"], "created_at": row["created_at"], "createdby": row["createdby"]})
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return upcomingduerecords

    @classmethod
    def getupcomingdivisionduerecords(cls):
        upcomingduerecords = []
        try:
            sql = """select axisrequestid, filenumber, fma.foiministryrequestid , fma.foiministryrequestversion, fma.foirequest_id, 
                        frd.divisionid, frd.stageid, pad2."name" divisionname, pads."name" stagename, 
                        to_char(divisionduedate, 'YYYY-MM-DD') as duedate, frd.created_at, frd.createdby 
                        from "FOIMinistryRequestDivisions" frd 
                        inner join (select distinct on (fpa.foiministryrequestid) foiministryrequestid, version as foiministryrequestversion, axisrequestid, filenumber, foirequest_id, requeststatusid 
                                    from "FOIMinistryRequests" fpa  
                                    order by fpa.foiministryrequestid , fpa.version desc) fma on frd.foiministryrequest_id = fma.foiministryrequestid and frd.foiministryrequestversion_id = fma.foiministryrequestversion and fma.requeststatusid not in (5,6,4,11,3,15) 
                        inner join "ProgramAreaDivisions" pad2 on frd.divisionid  = pad2.divisionid 
                        inner join "ProgramAreaDivisionStages" pads on frd.stageid  = pads.stageid and frd.stageid in (5, 7, 9) 
                        and frd.divisionduedate  between  NOW() - INTERVAL '7 DAY' AND NOW() + INTERVAL '7 DAY' 
                        order by frd.foiministryrequest_id , frd.foiministryrequestversion_id desc;""" 
            rs = db.session.execute(text(sql))        
            for row in rs:
                upcomingduerecords.append({"axisrequestid": row["axisrequestid"], "filenumber": row["filenumber"], 
                                            "foiministryrequestid": row["foiministryrequestid"], "version": row["foiministryrequestversion"], 
                                            "foirequest_id": row["foirequest_id"], "created_at": row["created_at"], "createdby": row["createdby"],
                                            "divisionid": row["divisionid"],"divisionname": row["divisionname"],
                                            "stageid": row["stageid"], "stagename": row["stagename"], 
                                            "duedate": row["duedate"]})
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return upcomingduerecords    
    
    @classmethod
    def getupcomingoipcduerecords(cls):
        upcomingduerecords = []
        try:
            sql = """select axisrequestid, filenumber, fma.foiministryrequestid , fma.foiministryrequestversion, fma.foirequest_id, 
                        frd.oipcid , frd.inquiryattributes ->> 'orderno'as  orderno, 
                        frd.inquiryattributes ->> 'inquirydate' as duedate, frd.created_at, frd.createdby 
                        from "FOIRequestOIPC" frd 
                        inner join (select distinct on (fpa.foiministryrequestid) foiministryrequestid, version as foiministryrequestversion, axisrequestid, filenumber, foirequest_id, requeststatusid 
                                    from "FOIMinistryRequests" fpa  
                                    order by fpa.foiministryrequestid , fpa.version desc) fma on frd.foiministryrequest_id  = fma.foiministryrequestid 
                                    and frd.foiministryrequestversion_id = fma.foiministryrequestversion and fma.requeststatusid not in (5,6,4,11,3,15) 
                        and (frd.inquiryattributes ->> 'inquirydate')::date  between  NOW() - INTERVAL '7 DAY' AND NOW() + INTERVAL '7 DAY' 
                        order by frd.foiministryrequest_id , frd.foiministryrequestversion_id desc;""" 
            rs = db.session.execute(text(sql))        
            for row in rs:
                upcomingduerecords.append({"axisrequestid": row["axisrequestid"], "filenumber": row["filenumber"], 
                                            "foiministryrequestid": row["foiministryrequestid"], "version": row["foiministryrequestversion"], 
                                            "foirequest_id": row["foirequest_id"], "created_at": row["created_at"], "createdby": row["createdby"],
                                            "orderno": row["orderno"],"duedate": row["duedate"]})
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return upcomingduerecords 

    @classmethod
    def updateduedate(cls, ministryrequestid, duedate, userid)->DefaultMethodResult:
        currequest = db.session.query(FOIMinistryRequest).filter_by(foiministryrequestid=ministryrequestid).order_by(FOIMinistryRequest.version.desc()).first()
        setattr(currequest,'duedate',duedate)
        setattr(currequest,'updated_at',datetime.now().isoformat())
        setattr(currequest,'updatedby',userid)
        db.session.commit()  
        return DefaultMethodResult(True,'Request updated',ministryrequestid)
  
    @classmethod   
    def getministriesopenedbyuid(cls, rawrequestid):
        ministries = []
        try:
            """
            sql = select distinct filenumber, axisrequestid, foiministryrequestid, foirequest_id, pa."name" from "FOIMinistryRequests" fpa 
                    inner join  "FOIRequests" frt on fpa.foirequest_id  = frt.foirequestid and fpa.foirequestversion_id = frt."version" 
                    inner join "ProgramAreas" pa on fpa.programareaid  = pa.programareaid 
                    where fpa.isactive = true and frt.isactive =true and frt.foirawrequestid=:rawrequestid;
            """
            sql = """select distinct filenumber, axisrequestid, foiministryrequestid, foirequest_id, pa."name", 
                        assignedministrygroup, assignedministryperson, assignedgroup, assignedto, fs2."name" as status
                        from "FOIMinistryRequests" fpa  
                        inner join  "FOIRequests" frt on fpa.foirequest_id  = frt.foirequestid and frt."version" = fpa.foirequestversion_id and frt."version" = 1 
                        inner join "ProgramAreas" pa on fpa.programareaid  = pa.programareaid 
                        inner join "FOIRequestStatuses" fs2 on fpa.requeststatusid = fs2.requeststatusid 
                        where frt.foirawrequestid=:rawrequestid; """ 
            rs = db.session.execute(text(sql), {'rawrequestid': rawrequestid})           
            for row in rs:
                ministries.append({"filenumber": row["filenumber"], "axisrequestid": row["axisrequestid"], "name": row["name"], "requestid": row["foirequest_id"],"ministryrequestid": row["foiministryrequestid"],
                                    "assignedministrygroup": row["assignedministrygroup"], "assignedministryperson": row["assignedministryperson"], "assignedgroup": row["assignedgroup"], "assignedto": row["assignedto"],
                                    "id": row["foiministryrequestid"], "foirequestid": row["foirequest_id"], "status": row["status"]})
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return ministries


    @classmethod   
    def getactivitybyid(cls, ministryrequestid):
        ministries = []
        try:
            sql = """select fm2.filenumber, fm2.axisrequestid, fm2.foiministryrequestid, fm2.foirequest_id, fm2.version, fs2."name" as status,
                        fm2.assignedministrygroup, fm2.assignedministryperson, fm2.assignedgroup, fm2.assignedto  
                        from  "FOIMinistryRequests" fm2  inner join "FOIRequestStatuses" fs2 on fm2.requeststatusid = fs2.requeststatusid 
                        where fm2.foiministryrequestid=:ministryrequestid order by version desc""" 
            rs = db.session.execute(text(sql), {'ministryrequestid': ministryrequestid})   
            _tmp_state = None        
            for row in rs:
                if row["status"] != _tmp_state:
                    ministries.append({"id": row["foiministryrequestid"], "foirequestid": row["foirequest_id"], "axisrequestid": row["axisrequestid"], "filenumber": row["filenumber"], "status": row["status"], 
                                    "assignedministrygroup": row["assignedministrygroup"], "assignedministryperson": row["assignedministryperson"], 
                                    "assignedgroup": row["assignedgroup"], "assignedto": row["assignedto"], "version": row["version"] 
                                     })
                    _tmp_state = row["status"] 
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return ministries 
    
    @classmethod
    def getclosedaxisids(cls):
        axisids = []                
        try:
            sql = """ select distinct on (foiministryrequestid) foiministryrequestid, version, axisrequestid  
                        from "FOIMinistryRequests" fr 
                        where requeststatusid = 3
                        order by  foiministryrequestid , version desc, axisrequestid"""
            rs = db.session.execute(text(sql))        
            for row in rs:
                axisids.append(row["axisrequestid"])
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return axisids 

    @classmethod
    def getbasequery(cls, iaoassignee, ministryassignee, userid=None, requestby='IAO', isiaorestrictedfilemanager=False, isministryrestrictedfilemanager=False):
        #for advanced search

        _session = db.session

        #ministry filter for group/team
        ministryfilter = and_(FOIMinistryRequest.isactive == True, FOIRequestStatus.isactive == True)

        #subquery for getting latest version & proper group/team for FOIMinistryRequest
        subquery_ministry_maxversion = _session.query(FOIMinistryRequest.foiministryrequestid, func.max(FOIMinistryRequest.version).label('max_version')).group_by(FOIMinistryRequest.foiministryrequestid).subquery()
        joincondition_ministry = [
            subquery_ministry_maxversion.c.foiministryrequestid == FOIMinistryRequest.foiministryrequestid,
            subquery_ministry_maxversion.c.max_version == FOIMinistryRequest.version,
        ]

        #subquery for getting extension count
        subquery_extension_count = _session.query(FOIRequestExtension.foiministryrequest_id , func.count(distinct(FOIRequestExtension.foirequestextensionid)).filter(FOIRequestExtension.isactive == True).label('extensions')).group_by(FOIRequestExtension.foiministryrequest_id).subquery()

        #aliase for onbehalf of applicant info
        onbehalf_applicantmapping = aliased(FOIRequestApplicantMapping)
        onbehalf_applicant = aliased(FOIRequestApplicant)

        #aliase for getting ministry restricted flag from FOIRestrictedMinistryRequest
        ministry_restricted_requests = aliased(FOIRestrictedMinistryRequest)

        intakesorting = case([
                            (FOIMinistryRequest.assignedto == None, # Unassigned requests first
                             literal(None)),
                           ],
                           else_ = FOIRequest.receiveddate).label('intakeSorting')

        defaultsorting = case([
                            (FOIMinistryRequest.assignedto == None, # Unassigned requests first
                             literal(None)),
                           ],
                           else_ = FOIMinistryRequest.duedate).label('defaultSorting')

        ministrysorting = case([
                            (FOIMinistryRequest.assignedministryperson == None, # Unassigned requests first
                             literal(None)),
                           ],
                           else_ = FOIMinistryRequest.duedate).label('ministrySorting')

        assignedtoformatted = case([
                            (and_(iaoassignee.lastname.isnot(None), iaoassignee.firstname.isnot(None)),
                             func.concat(iaoassignee.lastname, ', ', iaoassignee.firstname)),
                            (and_(iaoassignee.lastname.isnot(None), iaoassignee.firstname.is_(None)),
                             iaoassignee.lastname),
                            (and_(iaoassignee.lastname.is_(None), iaoassignee.firstname.isnot(None)),
                             iaoassignee.firstname),
                           ],
                           else_ = FOIMinistryRequest.assignedgroup).label('assignedToFormatted')

        ministryassignedtoformatted = case([
                            (and_(ministryassignee.lastname.isnot(None), ministryassignee.firstname.isnot(None)),
                             func.concat(ministryassignee.lastname, ', ', ministryassignee.firstname)),
                            (and_(ministryassignee.lastname.isnot(None), ministryassignee.firstname.is_(None)),
                             ministryassignee.lastname),
                            (and_(ministryassignee.lastname.is_(None), ministryassignee.firstname.isnot(None)),
                             ministryassignee.firstname),
                           ],
                           else_ = FOIMinistryRequest.assignedministrygroup).label('ministryAssignedToFormatted')
        
        duedate = case([
                            (FOIMinistryRequest.requeststatusid == 11,  # On Hold
                             literal(None)),
                           ],
                           else_ = cast(FOIMinistryRequest.duedate, String)).label('duedate')
        
        cfrduedate = case([
                            (FOIMinistryRequest.requeststatusid == 11,  # On Hold
                             literal(None)),
                           ],
                           else_ = cast(FOIMinistryRequest.cfrduedate, String)).label('cfrduedate')

        requestpagecount = case([
            (FOIMinistryRequest.requestpagecount.is_(None),
            '0'),
            ],
            else_ = cast(FOIMinistryRequest.requestpagecount, String)).label('requestPageCount')

        onbehalfformatted = case([
                            (and_(onbehalf_applicant.lastname.isnot(None), onbehalf_applicant.firstname.isnot(None)),
                             func.concat(onbehalf_applicant.lastname, ', ', onbehalf_applicant.firstname)),
                            (and_(onbehalf_applicant.lastname.isnot(None), onbehalf_applicant.firstname.is_(None)),
                             onbehalf_applicant.lastname),
                            (and_(onbehalf_applicant.lastname.is_(None), onbehalf_applicant.firstname.isnot(None)),
                             onbehalf_applicant.firstname),
                           ],
                           else_ = 'N/A').label('onBehalfFormatted')
        
        extensions = case([
                            (subquery_extension_count.c.extensions.is_(None),
                             0),
                           ],
                           else_ = subquery_extension_count.c.extensions).label('extensions')

        selectedcolumns = [
            FOIRequest.foirequestid.label('id'),
            FOIMinistryRequest.version,
            literal(None).label('sourceofsubmission'),
            FOIRequestApplicant.firstname.label('firstName'),
            FOIRequestApplicant.lastname.label('lastName'),
            FOIRequest.requesttype.label('requestType'),
            cast(FOIRequest.receiveddate, String).label('receivedDate'),
            cast(FOIRequest.receiveddate, String).label('receivedDateUF'),
            FOIRequestStatus.name.label('currentState'),
            FOIMinistryRequest.assignedgroup.label('assignedGroup'),
            FOIMinistryRequest.assignedto.label('assignedTo'),
            cast(FOIMinistryRequest.filenumber, String).label('idNumber'),
            cast(FOIMinistryRequest.axisrequestid, String).label('axisRequestId'),
            requestpagecount,
            FOIMinistryRequest.foiministryrequestid.label('ministryrequestid'),
            FOIMinistryRequest.assignedministrygroup.label('assignedministrygroup'),
            FOIMinistryRequest.assignedministryperson.label('assignedministryperson'),
            cfrduedate,
            duedate,
            ApplicantCategory.name.label('applicantcategory'),
            FOIRequest.created_at.label('created_at'),
            func.lower(ProgramArea.bcgovcode).label('bcgovcode'),
            iaoassignee.firstname.label('assignedToFirstName'),
            iaoassignee.lastname.label('assignedToLastName'),
            ministryassignee.firstname.label('assignedministrypersonFirstName'),
            ministryassignee.lastname.label('assignedministrypersonLastName'),
            FOIMinistryRequest.description,
            cast(FOIMinistryRequest.recordsearchfromdate, String).label('recordsearchfromdate'),
            cast(FOIMinistryRequest.recordsearchtodate, String).label('recordsearchtodate'),
            onbehalf_applicant.firstname.label('onBehalfFirstName'),
            onbehalf_applicant.lastname.label('onBehalfLastName'),
            defaultsorting,
            intakesorting,
            ministrysorting,
            assignedtoformatted,
            ministryassignedtoformatted,
            FOIMinistryRequest.closedate,
            onbehalfformatted,
            extensions,
            FOIRestrictedMinistryRequest.isrestricted.label('isiaorestricted'),
            ministry_restricted_requests.isrestricted.label('isministryrestricted'),
            SubjectCode.name.label('subjectcode'),
            FOIMinistryRequest.isoipcreview.label('isoipcreview'),
            literal(None).label('oipc_number')
        ]

        basequery = _session.query(
                                *selectedcolumns
                            ).join(
                                subquery_ministry_maxversion,
                                and_(*joincondition_ministry)
                            ).join(
                                subquery_extension_count,
                                subquery_extension_count.c.foiministryrequest_id == FOIMinistryRequest.foiministryrequestid,
                                isouter=True
                            ).join(
                                FOIRequest,
                                and_(FOIRequest.foirequestid == FOIMinistryRequest.foirequest_id, FOIRequest.version == FOIMinistryRequest.foirequestversion_id)
                            ).join(
                                FOIRequestStatus,
                                FOIRequestStatus.requeststatusid == FOIMinistryRequest.requeststatusid
                            ).join(
                                FOIRequestApplicantMapping,
                                and_(FOIRequestApplicantMapping.foirequest_id == FOIMinistryRequest.foirequest_id, FOIRequestApplicantMapping.foirequestversion_id == FOIMinistryRequest.foirequestversion_id, FOIRequestApplicantMapping.requestortypeid == RequestorType['applicant'].value)
                            ).join(
                                FOIRequestApplicant,
                                FOIRequestApplicant.foirequestapplicantid == FOIRequestApplicantMapping.foirequestapplicantid
                            ).join(
                                onbehalf_applicantmapping,
                                and_(
                                    onbehalf_applicantmapping.foirequest_id == FOIMinistryRequest.foirequest_id, 
                                    onbehalf_applicantmapping.foirequestversion_id == FOIMinistryRequest.foirequestversion_id, 
                                    onbehalf_applicantmapping.requestortypeid == RequestorType['onbehalfof'].value),
                                isouter=True
                            ).join(
                                onbehalf_applicant,
                                onbehalf_applicant.foirequestapplicantid == onbehalf_applicantmapping.foirequestapplicantid,  
                                isouter=True
                            ).join(
                                ApplicantCategory,
                                and_(ApplicantCategory.applicantcategoryid == FOIRequest.applicantcategoryid, ApplicantCategory.isactive == True)
                            ).join(
                                ProgramArea,
                                FOIMinistryRequest.programareaid == ProgramArea.programareaid
                            ).join(
                                iaoassignee,
                                iaoassignee.username == FOIMinistryRequest.assignedto,
                                isouter=True
                            ).join(
                                ministryassignee,
                                ministryassignee.username == FOIMinistryRequest.assignedministryperson,
                                isouter=True
                            ).join(
                                FOIRestrictedMinistryRequest,
                                and_(
                                    FOIRestrictedMinistryRequest.ministryrequestid == FOIMinistryRequest.foiministryrequestid,
                                    FOIRestrictedMinistryRequest.type == 'iao',
                                    FOIRestrictedMinistryRequest.isactive == True),
                                isouter=True
                            ).join(
                                ministry_restricted_requests,
                                and_(
                                    ministry_restricted_requests.ministryrequestid == FOIMinistryRequest.foiministryrequestid,
                                    ministry_restricted_requests.type == 'ministry',
                                    ministry_restricted_requests.isactive == True),
                                isouter=True
                            ).join(
                                FOIMinistryRequestSubjectCode,
                                and_(FOIMinistryRequestSubjectCode.foiministryrequestid == FOIMinistryRequest.foiministryrequestid, FOIMinistryRequestSubjectCode.foiministryrequestversion == FOIMinistryRequest.version),
                                isouter=True
                            ).join(
                                SubjectCode,
                                SubjectCode.subjectcodeid == FOIMinistryRequestSubjectCode.subjectcodeid,
                                isouter=True
                            )
                            

        if(isiaorestrictedfilemanager == True or isministryrestrictedfilemanager == True):
            dbquery = basequery.filter(ministryfilter)
        else:
            #watchby
            activefilter = and_(FOIMinistryRequest.isactive == True, FOIRequestStatus.isactive == True)

            subquery_watchby = FOIRequestWatcher.getrequestidsbyuserid(userid)
            newbasequery = basequery.join(
                                        subquery_watchby,
                                        subquery_watchby.c.ministryrequestid == FOIMinistryRequest.foiministryrequestid,
                                        isouter=True).filter(activefilter)

            if(requestby == 'IAO'):
                dbquery = newbasequery.filter(
                                            or_(
                                                or_(FOIRestrictedMinistryRequest.isrestricted == False, FOIRestrictedMinistryRequest.isrestricted == None),
                                                and_(FOIRestrictedMinistryRequest.isrestricted == True, FOIMinistryRequest.assignedto == userid),
                                                and_(FOIRestrictedMinistryRequest.isrestricted == True, subquery_watchby.c.watchedby == userid),
                                            )
                                        ).filter(ministryfilter)
            else:
                dbquery = newbasequery.filter(
                                            or_(
                                                or_(ministry_restricted_requests.isrestricted == False, ministry_restricted_requests.isrestricted == None),
                                                and_(ministry_restricted_requests.isrestricted == True, FOIMinistryRequest.assignedministryperson == userid),
                                                and_(ministry_restricted_requests.isrestricted == True, subquery_watchby.c.watchedby == userid),
                                            )
                                        ).filter(ministryfilter)

        return dbquery

    @classmethod
    def advancedsearch(cls, params, userid, isministryrestrictedfilemanager = False):
        #ministry requests
        iaoassignee = aliased(FOIAssignee)
        ministryassignee = aliased(FOIAssignee)

        groupfilter = []
        for group in params['groups']:
            groupfilter.append(FOIMinistryRequest.assignedministrygroup == group)
        
        #ministry advanced search show cfr onwards
        statefilter = FOIMinistryRequest.requeststatusid.in_([2,3,7,9,8,10,11,12,13,14,16,17,18])

        ministry_queue = FOIMinistryRequest.advancedsearchsubquery(params, iaoassignee, ministryassignee, userid, 'Ministry', False, isministryrestrictedfilemanager).filter(and_(or_(*groupfilter), statefilter))

        #sorting
        sortingcondition = FOIMinistryRequest.getsorting(params['sortingitems'], params['sortingorders'], iaoassignee, ministryassignee)

        return ministry_queue.order_by(*sortingcondition).paginate(page=params['page'], per_page=params['size'])

    @classmethod
    def advancedsearchsubquery(cls, params, iaoassignee, ministryassignee, userid, requestby, isiaorestrictedfilemanager, isministryrestrictedfilemanager=False):
        basequery = FOIMinistryRequest.getbasequery(iaoassignee, ministryassignee, userid, requestby, isiaorestrictedfilemanager, isministryrestrictedfilemanager)

        #filter/search
        filtercondition = FOIMinistryRequest.getfilterforadvancedsearch(params, iaoassignee, ministryassignee)
        return basequery.filter(and_(*filtercondition))

    @classmethod
    def getfilterforadvancedsearch(cls, params, iaoassignee, ministryassignee):

        #filter/search
        filtercondition = []
        includeclosed = False

        #request state: unopened, call for records, etc.
        if(len(params['requeststate']) > 0):
            requeststatecondition = FOIMinistryRequest.getfilterforrequeststate(params, includeclosed)
            filtercondition.append(requeststatecondition['condition'])
            includeclosed = requeststatecondition['includeclosed']
        
        #request status: overdue || on time
        if(len(params['requeststatus']) == 1):
            requeststatuscondition = FOIMinistryRequest.getfilterforrequeststatus(params, iaoassignee, ministryassignee)
            filtercondition.append(requeststatuscondition)

            # return all except closed
            if(includeclosed == False):
                filtercondition.append(FOIMinistryRequest.requeststatusid != 3)
        elif(len(params['requeststatus']) > 1 and includeclosed == False):
            # return all except closed
            filtercondition.append(FOIMinistryRequest.requeststatusid != 3)

        #request type: personal, general
        if(len(params['requesttype']) > 0):
            requesttypecondition = FOIMinistryRequest.getfilterforrequesttype(params, iaoassignee, ministryassignee)
            filtercondition.append(requesttypecondition)
        
        #request flags: restricted, oipc, phased
        if(len(params['requestflags']) > 0):
            requestflagscondition = FOIMinistryRequest.getfilterforrequestflags(params, iaoassignee, ministryassignee)
            filtercondition.append(requestflagscondition)

        #public body: EDUC, etc.
        if(len(params['publicbody']) > 0):
            publicbodycondition = FOIMinistryRequest.getfilterforpublicbody(params, iaoassignee, ministryassignee)
            filtercondition.append(publicbodycondition)

        #axis request #, raw request #, applicant name, assignee name, request description, subject code
        if(len(params['keywords']) > 0 and params['search'] is not None):
            searchcondition = FOIMinistryRequest.getfilterforsearch(params, iaoassignee, ministryassignee)
            filtercondition.append(searchcondition)

        if(params['fromdate'] is not None and params['daterangetype'] is not None):
            filtercondition.append(FOIMinistryRequest.findfield(params['daterangetype'], iaoassignee, ministryassignee).cast(Date) >= parser.parse(params['fromdate']))

        if(params['todate'] is not None and params['daterangetype'] is not None):
            filtercondition.append(FOIMinistryRequest.findfield(params['daterangetype'], iaoassignee, ministryassignee).cast(Date) <= parser.parse(params['todate']))
        
        return filtercondition

    @classmethod
    def getfilterforrequeststate(cls, params, includeclosed):
        #request state: unopened, call for records, etc.
        requeststatecondition = []
        for stateid in params['requeststate']:
            requeststatecondition.append(FOIMinistryRequest.requeststatusid == stateid)
            if(stateid == 3):
                includeclosed = True
        return {'condition': or_(*requeststatecondition), 'includeclosed': includeclosed}

    @classmethod
    def getfilterforrequeststatus(cls, params, iaoassignee, ministryassignee):        
        #request status: overdue || on time
        if(params['requeststatus'][0] == 'overdue'):
            #exclude "on hold" for overdue
            stateid = 11
            return and_(FOIMinistryRequest.findfield('duedate', iaoassignee, ministryassignee) < datetime.now().date(), FOIMinistryRequest.requeststatusid != stateid)
        else:
            return FOIMinistryRequest.findfield('duedate', iaoassignee, ministryassignee) >= datetime.now().date()

    @classmethod
    def getfilterforrequesttype(cls, params, iaoassignee, ministryassignee):  
        #request type: personal, general
        requesttypecondition = []
        for type in params['requesttype']:
            requesttypecondition.append(FOIMinistryRequest.findfield('requestType', iaoassignee, ministryassignee) == type)
        return or_(*requesttypecondition)

    @classmethod
    def getfilterforrequestflags(cls, params, iaoassignee, ministryassignee):
        #request flags: restricted, oipc, phased
        requestflagscondition = []
        #alias for getting ministry restricted flag from FOIRestrictedMinistryRequest
        ministry_restricted_requests = aliased(FOIRestrictedMinistryRequest)

        for flag in params['requestflags']:
            if (flag.lower() == 'restricted'):
                if(iaoassignee):
                    requestflagscondition.append(FOIRestrictedMinistryRequest.isrestricted == True)
                elif (ministryassignee):
                    requestflagscondition.append(ministry_restricted_requests.isrestricted == True)
            if (flag.lower() == 'oipc'):
                requestflagscondition.append(FOIMinistryRequest.findfield('isoipcreview', iaoassignee, ministryassignee) == True)
            if (flag.lower() == 'phased'):
                # requestflagscondition.append(FOIMinistryRequest.findfield('isphasedrelease', iaoassignee, ministryassignee) == True)
                continue
        return or_(*requestflagscondition)

    @classmethod
    def getfilterforpublicbody(cls, params, iaoassignee, ministryassignee):
        #public body: EDUC, etc.
        publicbodycondition = []
        for ministry in params['publicbody']:
            publicbodycondition.append(FOIMinistryRequest.findfield('ministry', iaoassignee, ministryassignee) == ministry)
        return or_(*publicbodycondition)

    @classmethod
    def getfilterforsearch(cls, params, iaoassignee, ministryassignee):
        #axis request #, raw request #, applicant name, assignee name, request description, subject code
        if(len(params['keywords']) > 0 and params['search'] is not None):
            if(params['search'] == 'applicantname'):
                searchcondition1 = []
                searchcondition2 = []
                for keyword in params['keywords']:
                    searchcondition1.append(FOIMinistryRequest.findfield('firstName', iaoassignee, ministryassignee).ilike('%'+keyword+'%'))
                    searchcondition2.append(FOIMinistryRequest.findfield('lastName', iaoassignee, ministryassignee).ilike('%'+keyword+'%'))
                return or_(and_(*searchcondition1), and_(*searchcondition2))
            elif(params['search'] == 'assigneename'):
                searchcondition1 = []
                searchcondition2 = []
                searchcondition3 = []
                for keyword in params['keywords']:
                    searchcondition1.append(FOIMinistryRequest.findfield('assignedToFirstName', iaoassignee, ministryassignee).ilike('%'+keyword+'%'))
                    searchcondition2.append(FOIMinistryRequest.findfield('assignedToLastName', iaoassignee, ministryassignee).ilike('%'+keyword+'%'))
                    searchcondition3.append(FOIMinistryRequest.assignedgroup.ilike('%'+keyword+'%'))
                return or_(and_(*searchcondition1), and_(*searchcondition2), and_(*searchcondition3))
            elif(params['search'] == 'ministryassigneename'):
                searchcondition1 = []
                searchcondition2 = []
                for keyword in params['keywords']:
                    searchcondition1.append(FOIMinistryRequest.findfield('assignedministrypersonFirstName', iaoassignee, ministryassignee).ilike('%'+keyword+'%'))
                    searchcondition2.append(FOIMinistryRequest.findfield('assignedministrypersonLastName', iaoassignee, ministryassignee).ilike('%'+keyword+'%'))
                return or_(and_(*searchcondition1), and_(*searchcondition2))
            elif(params['search'] == 'oipc_number'):
                searchcondition1 = []
                searchcondition2 = []
                for keyword in params['keywords']:
                    oipccondition = FOIRequestOIPC.getrequestidsbyoipcno(keyword)
                    searchcondition1.append(oipccondition.c.foiministryrequest_id == FOIMinistryRequest.foiministryrequestid)
                    searchcondition2.append(oipccondition.c.foiministryrequestversion_id == FOIMinistryRequest.version) 
                return and_(and_(*searchcondition1), and_(*searchcondition2))
            else:
                searchcondition = []
                for keyword in params['keywords']:
                    searchcondition.append(FOIMinistryRequest.findfield(params['search'], iaoassignee, ministryassignee).ilike('%'+keyword+'%'))
                return and_(*searchcondition)
    @classmethod
    def getfilenumberforrequest(cls,requestid, ministryrequestid):
        return db.session.query(FOIMinistryRequest.filenumber).filter_by(foiministryrequestid=ministryrequestid, foirequest_id=requestid).first()[0]

    @classmethod
    def getaxisrequestidforrequest(cls,requestid, ministryrequestid):   
        return db.session.query(FOIMinistryRequest.axisrequestid).filter_by(foiministryrequestid=ministryrequestid, foirequest_id=requestid).first()[0]
    
    @classmethod
    def getmetadata(cls,ministryrequestid):
        requestdetails = {}
        try:
            sql = """select fmr.version, assignedto, fa.firstname, fa.lastname, pa.bcgovcode, fmr.programareaid, f.requesttype  
                from "FOIMinistryRequests" fmr join "FOIRequests" f on fmr.foirequest_id = f.foirequestid and fmr.foirequestversion_id = f."version" 
                    FULL OUTER JOIN "FOIAssignees" fa ON fa.username = fmr.assignedto
                    INNER JOIN "ProgramAreas" pa ON pa.programareaid = fmr.programareaid
                    where foiministryrequestid = :ministryrequestid
                    order by fmr.version desc limit 1;"""
            rs = db.session.execute(text(sql), {'ministryrequestid': ministryrequestid})
            for row in rs:
                requestdetails["assignedTo"] = row["assignedto"]
                requestdetails["assignedToFirstName"] = row["firstname"]
                requestdetails["assignedToLastName"] = row["lastname"]
                requestdetails["bcgovcode"] = row["bcgovcode"]
                requestdetails["version"] = row["version"]
                requestdetails["programareaid"] = row["programareaid"]
                requestdetails["requesttype"] = row["requesttype"]
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return requestdetails

    @classmethod
    def getofflinepaymentflag(cls,ministryrequestid):
        try:
            sql = """select isofflinepayment from "FOIMinistryRequests" fci where 
             foiministryrequestid = :ministryrequestid and isofflinepayment = true limit 1;"""
            rs = db.session.execute(text(sql), {'ministryrequestid': ministryrequestid})
            for row in rs:
                if row["isofflinepayment"] == True:
                    return True
            return False
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()

class FOIMinistryRequestSchema(ma.Schema):
    class Meta:
        fields = ('foiministryrequestid','version','filenumber','description','recordsearchfromdate','recordsearchtodate',
                'startdate','duedate','assignedgroup','assignedto','programarea.programareaid','requeststatus.requeststatusid',
                'foirequest.foirequestid','foirequest.requesttype','foirequest.receiveddate','foirequest.deliverymodeid',
                'foirequest.receivedmodeid','requeststatus.requeststatusid','requeststatus.name','programarea.bcgovcode',
                'programarea.name','foirequest_id','foirequestversion_id','created_at','updated_at','createdby','assignedministryperson',
                'assignedministrygroup','cfrduedate','closedate','closereasonid','closereason.name',
                'assignee.firstname','assignee.lastname','ministryassignee.firstname','ministryassignee.lastname', 'axisrequestid', 'axissyncdate', 'requestpagecount', 'linkedrequests', 'ministrysignoffapproval', 'identityverified','originalldd','isoipcreview')
    
