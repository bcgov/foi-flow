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
from .CloseReasons import CloseReason
from request_api.utils.enums import ProcessingTeamWithKeycloackGroup, IAOTeamWithKeycloackGroup
from .FOIAssignees import FOIAssignee
from .FOIRequestExtensions import FOIRequestExtension
from request_api.utils.enums import RequestorType
import logging
from sqlalchemy.sql.sqltypes import Date, Integer
from dateutil import parser
from request_api.utils.enums import StateName
from .FOIMinistryRequestSubjectCodes import FOIMinistryRequestSubjectCode
from .SubjectCodes import SubjectCode
from request_api.utils.enums import StateName
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
    axispagecount = db.Column(db.String(20), nullable=True)
    axislanpagecount = db.Column(db.String(20), nullable=True)
    recordspagecount = db.Column(db.String(20), nullable=True)
    estimatedpagecount = db.Column(db.Integer, nullable=True)
    estimatedtaggedpagecount = db.Column(db.Integer, nullable=True)
    linkedrequests = db.Column(JSON, unique=False, nullable=True)
    identityverified = db.Column(JSON, unique=False, nullable=True)
    ministrysignoffapproval = db.Column(JSON, unique=False, nullable=True)
    requeststatuslabel = db.Column(db.String(50), nullable=False)
    userrecordslockstatus = db.Column(db.Boolean, nullable=True)
    isconsultflag = db.Column(db.Boolean, nullable=True)

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
    isphasedrelease = db.Column(db.Boolean, unique=False, nullable=True,default=False)

    @classmethod
    def getrequest(cls,ministryrequestid):
        request_schema = FOIMinistryRequestSchema(many=False)
        query = db.session.query(FOIMinistryRequest).filter_by(foiministryrequestid=ministryrequestid).order_by(FOIMinistryRequest.version.desc()).first()
        return request_schema.dump(query)

    @classmethod
    def getLastStatusUpdateDate(cls,foiministryrequestid,requeststatuslabel):
        statusdate = None
        try:
            sql = """select created_at from "FOIMinistryRequests" 
                    where foiministryrequestid = :foiministryrequestid and requeststatuslabel = :requeststatuslabel
                    order by version desc limit 1;"""
            rs = db.session.execute(text(sql), {'foiministryrequestid': foiministryrequestid, 'requeststatuslabel': requeststatuslabel})
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
            _ministryrequestids = _session.query(distinct(FOIMinistryRequest.foiministryrequestid)).filter(and_(FOIMinistryRequest.isactive == True), and_(and_(FOIMinistryRequest.assignedgroup == group),and_(FOIMinistryRequest.requeststatuslabel.in_([StateName.open.name,StateName.callforrecords.name,StateName.closed.name,StateName.recordsreview.name,StateName.feeestimate.name,StateName.consult.name,StateName.ministrysignoff.value,StateName.onhold.name,StateName.deduplication.name,StateName.harmsassessment.name,StateName.response.name,StateName.peerreview.name,StateName.tagging.name,StateName.readytoscan.name,StateName.onholdother.name])))).all()
        elif (group in ProcessingTeamWithKeycloackGroup.list()):
            _ministryrequestids = _session.query(distinct(FOIMinistryRequest.foiministryrequestid)).filter(and_(FOIMinistryRequest.isactive == True), and_(and_(FOIMinistryRequest.assignedgroup == group),and_(FOIMinistryRequest.requeststatuslabel.in_([StateName.open.name,StateName.callforrecords.name,StateName.closed.name,StateName.recordsreview.name,StateName.feeestimate.name,StateName.consult.name,StateName.ministrysignoff.value,StateName.onhold.name,StateName.response.name,StateName.peerreview.name,StateName.tagging.name,StateName.readytoscan.name,StateName.onholdother.name])))).all()           
        else:
            _ministryrequestids = _session.query(distinct(FOIMinistryRequest.foiministryrequestid)).filter(and_(FOIMinistryRequest.isactive == True), or_(and_(FOIMinistryRequest.assignedgroup == group),and_(FOIMinistryRequest.assignedministrygroup == group,or_(FOIMinistryRequest.requeststatuslabel.in_([StateName.callforrecords.name,StateName.recordsreview.name,StateName.recordsreadyforreview.name,StateName.feeestimate.name,StateName.consult.name,StateName.ministrysignoff.name,StateName.onhold.name,StateName.deduplication.name,StateName.harmsassessment.name,StateName.response.name,StateName.peerreview.name,StateName.tagging.name,StateName.readytoscan.name,StateName.onholdother.name]))))).all()

        _requests = []
        ministryrequest_schema = FOIMinistryRequestSchema()
        for _requestid in _ministryrequestids:
           _request ={}
           
           ministryrequest =ministryrequest_schema.dump(_session.query(FOIMinistryRequest).filter(FOIMinistryRequest.foiministryrequestid == _requestid).order_by(FOIMinistryRequest.version.desc()).first())           
           parentrequest = _session.query(FOIRequest).filter(FOIRequest.foirequestid == ministryrequest['foirequest_id'] and FOIRequest.version == ministryrequest['foirequestversion_id']).order_by(FOIRequest.version.desc()).first()
           requestapplicants = FOIRequestApplicantMapping.getrequestapplicantinfos(ministryrequest['foirequest_id'],ministryrequest['foirequestversion_id'])
           _receiveddate = parentrequest.receiveddate
           _request["firstName"] = requestapplicants[0]['firstname']
           _request["lastName"] = requestapplicants[0]['lastname']
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
           _request["applicantcategory"]= parentrequest.applicantcategory.name
           _request["identityverified"] = ministryrequest['identityverified']
           _request["axisapplicantid"] = requestapplicants[0]['axisapplicantid']
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
    def getopenrequestsbyrequestId(cls,requestids):
        selectedcolumns = [FOIMinistryRequest.foirequest_id, FOIMinistryRequest.foiministryrequestid]
        query = db.session.query(*selectedcolumns).distinct(FOIMinistryRequest.foiministryrequestid).filter(
            FOIMinistryRequest.foirequest_id.in_(requestids),
            FOIMinistryRequest.requeststatusid != 3
        ).order_by(FOIMinistryRequest.foiministryrequestid.asc(), FOIMinistryRequest.version.asc())
        return [r._asdict() for r in query]
    
    @classmethod
    def getopenrequestsbyapplicantid(cls,applicantid):
        _session = db.session

        selectedcolumns = [FOIMinistryRequest.foirequest_id, FOIMinistryRequest.foiministryrequestid]

        #aliase for getting applicants by profileid
        applicant = aliased(FOIRequestApplicant)

        #subquery for getting latest version & proper group/team for FOIMinistryRequest
        subquery_ministry_maxversion = _session.query(FOIMinistryRequest.foirequest_id, func.max(FOIMinistryRequest.foirequestversion_id).label('max_version')).group_by(FOIMinistryRequest.foirequest_id).subquery()
        joincondition_ministry = [
            subquery_ministry_maxversion.c.foirequest_id == FOIRequestApplicantMapping.foirequest_id,
            subquery_ministry_maxversion.c.max_version == FOIRequestApplicantMapping.foirequestversion_id,
        ]

        query = db.session.query(
                                *selectedcolumns
                            ).distinct(
                                FOIMinistryRequest.foiministryrequestid
                            ).join(
                                applicant,
                                applicant.foirequestapplicantid == applicantid,
                            ).join(
                                FOIRequestApplicant,
                                FOIRequestApplicant.applicantprofileid == applicant.applicantprofileid,
                            ).join(
                                FOIRequestApplicantMapping,
                                and_(
                                    FOIRequestApplicantMapping.foirequestapplicantid == FOIRequestApplicant.foirequestapplicantid,
                                    FOIRequestApplicantMapping.foirequest_id == FOIMinistryRequest.foirequest_id,
                                    FOIRequestApplicantMapping.requestortypeid == RequestorType['applicant'].value)
                            ).join(
                                subquery_ministry_maxversion,
                                and_(*joincondition_ministry)
                            ).filter(
                                # FOIRequestApplicant.foirequestapplicantid == applicantid,
                                FOIMinistryRequest.requeststatusid != 3
                            ).order_by(
                                FOIMinistryRequest.foiministryrequestid.asc(),
                                FOIMinistryRequest.version.asc())
        return [r._asdict() for r in query]

    @classmethod
    def getrequeststatusById(cls,ministryrequestid):
        summary = []
        try:
            sql = 'select foirequest_id, version, requeststatusid, requeststatuslabel, created_at from "FOIMinistryRequests" fr  where foiministryrequestid = :ministryrequestid and requeststatuslabel != :requeststatuslabel order by version desc;'
            
            rs = db.session.execute(text(sql), {'ministryrequestid': ministryrequestid, 'requeststatuslabel': StateName.closed.name})        
            for row in rs:
                summary.append({"requeststatusid": row["requeststatusid"], "requeststatuslabel": row["requeststatuslabel"], "created_at": row["created_at"], "foirequest_id": row["foirequest_id"]})                
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
            sql = """select fm2.version, fs2."name" as status, fm2.created_at from  "FOIMinistryRequests" fm2  inner join "FOIRequestStatuses" fs2 on fm2.requeststatusid = fs2.requeststatusid 
                        where fm2.foiministryrequestid=:ministryrequestid order by version desc"""
            rs = db.session.execute(text(sql), {'ministryrequestid': ministryrequestid})  
            _tmp_state = None       
            for row in rs:
                if row["status"] != _tmp_state:
                    transitions.append({"status": row["status"], "version": row["version"], "created_at": row["created_at"].strftime('%Y-%m-%d %H:%M:%S.%f')})
                    _tmp_state = row["status"]
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return transitions

    @classmethod
    def getlastoffholddate(cls, ministryrequestid, currentstatus):  
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
                if entry["status"] == currentstatus:
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
        
        #subquery for selecting distinct records based on foiministryrequest_id, grouping by foiministryrequestversion_id
        subquery_with_oipc_sql = """
        SELECT DISTINCT ON (foiministryrequest_id) foiministryrequest_id, foiministryrequestversion_id, 
        CASE WHEN EXISTS (SELECT 1 FROM "FOIRequestOIPC" WHERE fo.foiministryrequest_id = foiministryrequest_id AND fo.foiministryrequestversion_id = foiministryrequestversion_id AND outcomeid IS NULL) THEN NULL ELSE MAX(outcomeid) END AS outcomeid 
        FROM "FOIRequestOIPC" fo GROUP BY foiministryrequest_id, foiministryrequestversion_id ORDER BY foiministryrequest_id, foiministryrequestversion_id DESC
        """
        subquery_with_oipc = text(subquery_with_oipc_sql).columns(FOIRequestOIPC.foiministryrequest_id, FOIRequestOIPC.foiministryrequestversion_id, FOIRequestOIPC.outcomeid).alias("oipcnoneoutcomes")
        joincondition_oipc = [
            subquery_with_oipc.c.foiministryrequest_id == FOIMinistryRequest.foiministryrequestid,
            subquery_with_oipc.c.foiministryrequestversion_id == FOIMinistryRequest.version,
        ]

        #aliase for onbehalf of applicant info
        onbehalf_applicantmapping = aliased(FOIRequestApplicantMapping)
        onbehalf_applicant = aliased(FOIRequestApplicant)

        #aliase for getting ministry restricted flag from FOIRestrictedMinistryRequest
        ministry_restricted_requests = aliased(FOIRestrictedMinistryRequest)

        #filter/search
        _keywords = []
        if(keyword is not None):
            _keywords = keyword.lower().replace(",", " ").split()
        if(len(filterfields) > 0 and keyword is not None):
            filtercondition = []
            for _keyword in _keywords:
                onekeywordfiltercondition = []
                if(_keyword != "restricted"):
                    for field in filterfields:
                        onekeywordfiltercondition.append(FOIMinistryRequest.findfield(field, iaoassignee, ministryassignee).ilike('%'+_keyword+'%'))
                else:
                    if(requestby == 'IAO'):
                        onekeywordfiltercondition.append(FOIRestrictedMinistryRequest.isrestricted == True)
                    else:
                        onekeywordfiltercondition.append(ministry_restricted_requests.isrestricted == True)
                if (_keyword == "oipc"):
                    onekeywordfiltercondition.append(FOIMinistryRequest.isoipcreview == True)
                if (_keyword == "phased"):
                    onekeywordfiltercondition.append(FOIMinistryRequest.isphasedrelease == True)
            
                filtercondition.append(or_(*onekeywordfiltercondition))

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
                            (or_(FOIMinistryRequest.requeststatuslabel == StateName.onhold.name, FOIMinistryRequest.requeststatuslabel == StateName.onholdother.name),  # On Hold
                             literal(None)),
                           ],
                           else_ = cast(FOIMinistryRequest.duedate, String)).label('duedate')
        
        cfrduedate = case([
                            (or_(FOIMinistryRequest.requeststatuslabel == StateName.onhold.name, FOIMinistryRequest.requeststatuslabel == StateName.onholdother.name),  # On Hold
                             literal(None)),
                           ],
                           else_ = cast(FOIMinistryRequest.cfrduedate, String)).label('cfrduedate')

        axispagecount = case ([
            (FOIMinistryRequest.axispagecount.isnot(None), FOIMinistryRequest.axispagecount)
            ],
            else_= literal("0").label("axispagecount")
        )
        axislanpagecount = case ([
            (FOIMinistryRequest.axislanpagecount.isnot(None), FOIMinistryRequest.axislanpagecount)
            ],
            else_= literal("0").label("axislanpagecount")
        )
        recordspagecount = case ([
            (FOIMinistryRequest.recordspagecount.isnot(None), FOIMinistryRequest.recordspagecount)
            ],
            else_= literal("0").label("recordspagecount")
        )

        requestpagecount = case([
                (and_(axispagecount.isnot(None), recordspagecount.isnot(None), cast(axispagecount, Integer) > cast(recordspagecount, Integer)),
                    axispagecount),
                (and_(recordspagecount.isnot(None)),
                    recordspagecount),
                (and_(axispagecount.isnot(None)),
                    axispagecount),
                ],
                else_= literal("0"))

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
            cast(requestpagecount, Integer).label('requestpagecount'),
            axispagecount.label("axispagecount"),
            axislanpagecount.label("axislanpagecount"),
            recordspagecount.label("recordspagecount"),
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
            FOIMinistryRequest.isphasedrelease.label('isphasedrelease'),
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
                            ).join(
                                subquery_with_oipc,
                                and_(
                                    *joincondition_oipc
                                    ),
                                isouter=True
                            ).filter(or_(FOIMinistryRequest.requeststatuslabel != StateName.closed.name, 
                                         and_(FOIMinistryRequest.isoipcreview == True, FOIMinistryRequest.requeststatusid == 3,subquery_with_oipc.c.outcomeid == None)))

       

        if(additionalfilter == 'watchingRequests'):
            #watchby
            activefilter = and_(FOIMinistryRequest.isactive == True, FOIRequestStatus.isactive == True)

            subquery_watchby = FOIRequestWatcher.getrequestidsbyuserid(userid)
            if(requestby == 'IAO'):
                dbquery = basequery.join(subquery_watchby, subquery_watchby.c.ministryrequestid == FOIMinistryRequest.foiministryrequestid).filter(activefilter).filter(or_(or_(FOIRestrictedMinistryRequest.isrestricted == False, FOIRestrictedMinistryRequest.isrestricted == None), and_(FOIRestrictedMinistryRequest.isrestricted == True, FOIMinistryRequest.assignedto == userid)))
            else:
                dbquery = basequery.join(subquery_watchby, subquery_watchby.c.ministryrequestid == FOIMinistryRequest.foiministryrequestid).filter(activefilter).filter(or_(or_(ministry_restricted_requests.isrestricted == isministryrestrictedfilemanager, ministry_restricted_requests.isrestricted == None), and_(ministry_restricted_requests.isrestricted == True, FOIMinistryRequest.assignedministryperson == userid)))   
            
        elif(additionalfilter == 'myRequests'):
            #myrequest
            if(requestby == 'IAO'):
                dbquery = basequery.filter(FOIMinistryRequest.assignedto == userid).filter(ministryfilter)
            else:
                dbquery = basequery.filter(FOIMinistryRequest.assignedministryperson == userid).filter(ministryfilter)
        elif(additionalfilter == 'unassignedRequests'):
            if(requestby == 'IAO'):
                dbquery = basequery.filter(FOIMinistryRequest.assignedto == None).filter(ministryfilter)
        elif(additionalfilter.lower() == 'all'):           
            if(requestby == 'IAO'):
                dbquery = basequery.filter(ministryfilter).filter(FOIMinistryRequest.assignedto.isnot(None)).filter(or_(FOIRestrictedMinistryRequest.isrestricted == isiaorestrictedfilemanager, or_(FOIRestrictedMinistryRequest.isrestricted.is_(None), FOIRestrictedMinistryRequest.isrestricted == False)))
            else:               
                dbquery = basequery.filter(ministryfilter).filter(or_(ministry_restricted_requests.isrestricted == isministryrestrictedfilemanager, or_(ministry_restricted_requests.isrestricted.is_(None), ministry_restricted_requests.isrestricted == False)))
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
            return dbquery.filter(and_(*filtercondition))

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
        axispagecount = case ([
            (FOIMinistryRequest.axispagecount.isnot(None), FOIMinistryRequest.axispagecount)
            ],
            else_= literal("0").label("axispagecount")
        )
        axislanpagecount = case ([
            (FOIMinistryRequest.axislanpagecount.isnot(None), FOIMinistryRequest.axislanpagecount)
            ],
            else_= literal("0").label("axislanpagecount")
        )
        recordspagecount = case ([
            (FOIMinistryRequest.recordspagecount.isnot(None), FOIMinistryRequest.recordspagecount)
            ],
            else_= literal("0").label("recordspagecount")
        )
        requestpagecount = case([
                (and_(axispagecount.isnot(None), recordspagecount.isnot(None), cast(axispagecount, Integer) > cast(recordspagecount, Integer)),
                    axispagecount),
                (and_(recordspagecount.isnot(None)),
                    recordspagecount),
                (and_(axispagecount.isnot(None)),
                    axispagecount),
                ],
                else_= literal("0")).label('requestpagecount')

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
            'requestpagecount': requestpagecount,
            'axispagecount': axispagecount,
            'axislanpagecount': axislanpagecount,
            'recordspagecount': recordspagecount,
            'closedate': FOIMinistryRequest.closedate,
            'subjectcode': SubjectCode.name,
            'isoipcreview': FOIMinistryRequest.isoipcreview,
            'isphasedrelease': FOIMinistryRequest.isphasedrelease
        }.get(x, FOIMinistryRequest.axisrequestid)

    @classmethod
    def getgroupfilters(cls, groups):
        #ministry filter for group/team
        if groups is None:
            ministryfilter = FOIMinistryRequest.isactive == True
        else:
            groupfilter = []
            statusfilter = None
            processinggroups = list(set(groups).intersection(ProcessingTeamWithKeycloackGroup.list())) 
            if IAOTeamWithKeycloackGroup.intake.value in groups or len(processinggroups) > 0:
                groupfilter.append(
                            and_(
                                FOIMinistryRequest.assignedgroup.in_(tuple(groups))
                            )
                        )
                statusfilter = FOIMinistryRequest.requeststatuslabel != StateName.closed.name
            else:
                groupfilter.append(
                        or_(
                            FOIMinistryRequest.assignedgroup.in_(tuple(groups)),
                            and_(
                                FOIMinistryRequest.assignedministrygroup.in_(tuple(groups))
                            )
                        )
                    )
                statusfilter = FOIMinistryRequest.requeststatuslabel.in_([StateName.callforrecords.name,StateName.recordsreview.name,StateName.feeestimate.name,StateName.consult.name,StateName.ministrysignoff.name,StateName.onhold.name,StateName.deduplication.name,StateName.harmsassessment.name,StateName.response.name,StateName.peerreview.name,StateName.tagging.name,StateName.readytoscan.name, StateName.recordsreadyforreview.name, StateName.onholdother.name])
            ministryfilter = and_(
                                FOIMinistryRequest.isactive == True,
                                FOIRequestStatus.isactive == True,
                                or_(*groupfilter)
                            )
        ministryfilterwithclosedoipc = and_(ministryfilter, 
                                            or_(statusfilter, 
                                                and_(FOIMinistryRequest.isoipcreview == True, FOIMinistryRequest.requeststatuslabel == StateName.closed.name)
                                                )
                                            )
        return ministryfilterwithclosedoipc

    @classmethod
    def getrequestoriginalduedate(cls,ministryrequestid):       
        return db.session.query(FOIMinistryRequest.duedate).filter(FOIMinistryRequest.foiministryrequestid == ministryrequestid, FOIMinistryRequest.requeststatuslabel == StateName.open.name).order_by(FOIMinistryRequest.version).first()[0]

    @classmethod
    def getduedate(cls,ministryrequestid):
        return db.session.query(FOIMinistryRequest.duedate).filter(FOIMinistryRequest.foiministryrequestid == ministryrequestid).order_by(FOIMinistryRequest.version.desc()).first()[0]

   
    @classmethod
    def getupcomingcfrduerecords(cls):
        upcomingduerecords = []
        try:
            sql = """select distinct on (filenumber) filenumber, to_char(cfrduedate, 'YYYY-MM-DD') as cfrduedate, foiministryrequestid, version, foirequest_id, created_at, createdby from "FOIMinistryRequests" fpa 
                    where isactive = true and cfrduedate is not null and requeststatuslabel = :requeststatuslabel  
                    and cfrduedate between  NOW() - INTERVAL '7 DAY' AND NOW() + INTERVAL '7 DAY'
                    order by filenumber , version desc;""" 
            rs = db.session.execute(text(sql), {'requeststatuslabel': StateName.callforrecords.name})           
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
                    where isactive = true and duedate is not null and requeststatuslabel not in :requeststatuslabel
                    and duedate between  NOW() - INTERVAL '7 DAY' AND NOW() + INTERVAL '7 DAY'
                    order by filenumber , version desc;""" 
            requeststatuslabel =  tuple([StateName.closed.name,StateName.redirect.name,StateName.unopened.name,StateName.intakeinprogress.name,StateName.onhold.name,StateName.archived.name, StateName.onholdother.name])
            rs = db.session.execute(text(sql), {'requeststatuslabel': requeststatuslabel})
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
                        inner join (select distinct on (fpa.foiministryrequestid) foiministryrequestid, version as foiministryrequestversion, axisrequestid, filenumber, foirequest_id, requeststatusid, requeststatuslabel 
                                    from "FOIMinistryRequests" fpa  
                                    order by fpa.foiministryrequestid , fpa.version desc) fma on frd.foiministryrequest_id = fma.foiministryrequestid and frd.foiministryrequestversion_id = fma.foiministryrequestversion and fma.requeststatuslabel not in :requeststatuslabel
                        inner join "ProgramAreaDivisions" pad2 on frd.divisionid  = pad2.divisionid 
                        inner join "ProgramAreaDivisionStages" pads on frd.stageid  = pads.stageid and frd.stageid in (5, 7, 9) 
                        and frd.divisionduedate  between  NOW() - INTERVAL '7 DAY' AND NOW() + INTERVAL '7 DAY' 
                        order by frd.foiministryrequest_id , frd.foiministryrequestversion_id desc;""" 
            requeststatuslabel = tuple([StateName.closed.name,StateName.redirect.name,StateName.unopened.name,StateName.intakeinprogress.name,StateName.onhold.name,StateName.archived.name,StateName.onholdother.name])
            rs = db.session.execute(text(sql), {'requeststatuslabel': requeststatuslabel})
                  
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
                        and inquiryattributes is not null 
                        and frd.inquiryattributes ->> 'inquirydate' not in ('','null') 
                        and (frd.inquiryattributes ->> 'inquirydate')::date  between  NOW() - INTERVAL '7 DAY' AND NOW() + INTERVAL '7 DAY' 
                        and frd.outcomeid  is null
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
                        where requeststatuslabel = :requeststatuslabel
                        order by  foiministryrequestid , version desc, axisrequestid"""
            rs = db.session.execute(text(sql), {'requeststatuslabel': StateName.closed.name})
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
                            (or_(FOIMinistryRequest.requeststatuslabel == StateName.onhold.name, FOIMinistryRequest.requeststatuslabel == StateName.onholdother.name),  # On Hold
                             literal(None)),
                           ],
                           else_ = cast(FOIMinistryRequest.duedate, String)).label('duedate')
        
        cfrduedate = case([
                            (or_(FOIMinistryRequest.requeststatuslabel == StateName.onhold.name, FOIMinistryRequest.requeststatuslabel == StateName.onholdother.name),  # On Hold
                             literal(None)),
                           ],
                           else_ = cast(FOIMinistryRequest.cfrduedate, String)).label('cfrduedate')

        axispagecount = case ([
            (FOIMinistryRequest.axispagecount.isnot(None), FOIMinistryRequest.axispagecount)
            ],
            else_= literal("0").label("axispagecount")
        )
        axislanpagecount = case ([
            (FOIMinistryRequest.axislanpagecount.isnot(None), FOIMinistryRequest.axislanpagecount)
            ],
            else_= literal("0").label("axislanpagecount")
        )
        recordspagecount = case ([
            (FOIMinistryRequest.recordspagecount.isnot(None), FOIMinistryRequest.recordspagecount)
            ],
            else_= literal("0").label("recordspagecount")
        )
        requestpagecount = case([
                (and_(axispagecount.isnot(None), recordspagecount.isnot(None), cast(axispagecount, Integer) > cast(recordspagecount, Integer)),
                    axispagecount),
                (and_(recordspagecount.isnot(None)),
                    recordspagecount),
                (and_(axispagecount.isnot(None)),
                    axispagecount),
                ],
                else_= literal("0"))

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
            cast(requestpagecount, Integer).label('requestpagecount'),
            axispagecount.label('axispagecount'),
            axislanpagecount.label('axislanpagecount'),
            recordspagecount.label('recordspagecount'),     
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
            FOIMinistryRequest.isphasedrelease.label('isphasedrelease'),
            literal(None).label('oipc_number'),
            CloseReason.name.label('closereason')
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
                            ).join(
                                CloseReason,
                                CloseReason.closereasonid == FOIMinistryRequest.closereasonid,
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
                                                or_(FOIRestrictedMinistryRequest.isrestricted == False, FOIRestrictedMinistryRequest.isrestricted.is_(None)),
                                                and_(FOIRestrictedMinistryRequest.isrestricted == True, FOIMinistryRequest.assignedto == userid),
                                                and_(FOIRestrictedMinistryRequest.isrestricted == True, subquery_watchby.c.watchedby == userid),
                                            )
                                        ).filter(ministryfilter)
            else:
                dbquery = newbasequery.filter(
                                            or_(
                                                or_(ministry_restricted_requests.isrestricted == False, ministry_restricted_requests.isrestricted.is_(None)),
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
        statefilter = FOIMinistryRequest.requeststatuslabel.in_([StateName.callforrecords.name,StateName.closed.name,StateName.recordsreview.name,StateName.feeestimate.name,StateName.consult.name,StateName.ministrysignoff.name,StateName.onhold.name,StateName.deduplication.name,StateName.harmsassessment.name,StateName.response.name,StateName.peerreview.name,StateName.tagging.name,StateName.readytoscan.name,StateName.recordsreadyforreview.name,StateName.onholdother.name])

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
                filtercondition.append(FOIMinistryRequest.requeststatuslabel != StateName.closed.name)
        elif(len(params['requeststatus']) > 1 and includeclosed == False):
            # return all except closed
            filtercondition.append(FOIMinistryRequest.requeststatuslabel != StateName.closed.name)

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
        for statelabel in params['requeststate']:
            requeststatecondition.append(FOIMinistryRequest.requeststatuslabel == statelabel)
            if(statelabel == StateName.closed.name):
                includeclosed = True
        return {'condition': or_(*requeststatecondition), 'includeclosed': includeclosed}

    @classmethod
    def getfilterforrequeststatus(cls, params, iaoassignee, ministryassignee):        
        #request status: overdue || on time
        if(params['requeststatus'][0] == 'overdue'):
            #exclude "on hold" for overdue
            # statelabel = StateName.onhold.name
            return and_(FOIMinistryRequest.findfield('duedate', iaoassignee, ministryassignee) < datetime.now().date(), and_(FOIMinistryRequest.requeststatuslabel != StateName.onhold.name, FOIMinistryRequest.requeststatuslabel != StateName.onholdother.name))
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
                requestflagscondition.append(FOIMinistryRequest.findfield('isphasedrelease', iaoassignee, ministryassignee) == True)
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
    def getrequest_by_pgmarea_type(cls,programarea, requesttype):
        requestdetails = []
        try:
            sql = """select fr.axisrequestid, fr.foiministryrequestid, fr."version", fr.axispagecount, fr.axislanpagecount
            from "FOIMinistryRequests" fr join "FOIRequests" f 
            ON fr.foirequest_id = f.foirequestid and fr.foirequestversion_id = f."version" 
            join "FOIRequestStatuses" fs2 on fr.requeststatusid  = fs2.requeststatusid
            where programareaid = :programarea and f.requesttype = :requesttype and fr.isactive = true and lower(fs2.statuslabel) <> 'closed'
            order by fr.created_at ;"""
            rs = db.session.execute(text(sql), {'programarea': programarea, 'requesttype': requesttype})
            for row in rs:
                requestdetails.append({"axisrequestid":row["axisrequestid"], "axispagecount": row["axispagecount"],  "axislanpagecount": row["axislanpagecount"], "foiministryrequestid":row["foiministryrequestid"], "version":row["version"]})
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return requestdetails 
    
    @classmethod
    def bulk_update_axispagecount(cls, requestdetails):
        try:
            db.session.bulk_update_mappings(FOIMinistryRequest, requestdetails)
            db.session.commit()
            return DefaultMethodResult(True,'Request updated', len(requestdetails))
        except Exception as ex:
            logging.error(ex)
            return DefaultMethodResult(False,'Request update failed', len(requestdetails))
        finally:
            db.session.close() 


    @classmethod
    def getmetadata(cls,ministryrequestid):
        requestdetails = {}
        try:
            sql = """select fmr.version, assignedto, fa.firstname, fa.lastname, pa.bcgovcode, fmr.programareaid, f.requesttype, fmr.isoipcreview
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
                requestdetails["isoipcreview"] = row["isoipcreview"]
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
    
    @classmethod
    def updaterecordspagecount(cls, ministryrequestid, pagecount, userid):
        currequest = db.session.query(FOIMinistryRequest).filter_by(foiministryrequestid=ministryrequestid).order_by(FOIMinistryRequest.version.desc()).first()
        setattr(currequest,'recordspagecount',pagecount)
        setattr(currequest,'updated_at',datetime.now().isoformat())
        setattr(currequest,'updatedby',userid)
        db.session.commit()  
        return DefaultMethodResult(True,'Request updated',ministryrequestid)
    
    @classmethod
    def getrequestsdetailsforsearch(cls,requestnumbers):
        requestdetails = []
        try:
            csvrequestnumbers = tuple(requestnumbers)            
            query=f"""SELECT
                    DISTINCT FMR.foiministryrequestid
                     ,FMR.foiministryrequestid
                     ,FMR.foirequest_id
                    ,FMR.axisrequestid
                    ,FMR.requeststatuslabel
                    ,FRA.lastname
                    ,FRA.firstname
                    ,FMR.closedate
                    ,FMR.axispagecount
                    ,FMR.recordspagecount
                    ,FMR.axislanpagecount
                    ,FMR.estimatedpagecount
                    ,FMR.estimatedtaggedpagecount
                    ,FMR.description
                    ,PA.iaocode AS programareacode
                    ,FR.requesttype
                    FROM public."FOIMinistryRequests" FMR INNER JOIN (
                        SELECT 
                        DISTINCT FMR.foiministryrequestid as ministryrequestid
                        ,FMR.foirequest_id as requestid
                        ,max(FMR.version) as latestversion 
                        FROM public."FOIMinistryRequests" FMR 
                        WHERE FMR.axisrequestid in :csvrequestnumbers
                        GROUP BY FMR.foiministryrequestid,FMR.foirequest_id
                    ) MaxRequestVersions ON FMR.foiministryrequestid=MaxRequestVersions.ministryrequestid and FMR.version=MaxRequestVersions.latestversion
                    JOIN public."FOIRequestApplicantMappings" FRAM ON FRAM.foirequest_id=MaxRequestVersions.requestid
                    JOIN public."FOIRequestApplicants" FRA ON FRA.foirequestapplicantid=FRAM.foirequestapplicantid
                    LEFT JOIN public."ProgramAreas" PA	ON FMR.programareaid = PA.programareaid
   	                JOIN public."FOIRequests" FR ON FMR.foirequest_id = FR.foirequestid AND FMR.version = FR.version"""            
            result = db.session.execute(text(query),{"csvrequestnumbers":csvrequestnumbers})        
            rows = result.fetchall()            
            for row in rows:
                requestdetail={}
                requestdetail["ministryrequestid"]=row["foiministryrequestid"]
                requestdetail["id"]=row["foirequest_id"]
                requestdetail["requeststatus"]=row["requeststatuslabel"]
                requestdetail["requestnumber"]=row["axisrequestid"]
                requestdetail["lastname"]=row["lastname"]
                requestdetail["firstname"]=row["firstname"]
                requestdetail["closedate"]=row["closedate"]
                requestdetail["axispagecount"]=row["axispagecount"]
                requestdetail["recordspagecount"]=row["recordspagecount"]
                if row["axispagecount"] is not None and row["recordspagecount"] is not None and int(row["axispagecount"]) > int(row["recordspagecount"]):
                    requestdetail["requestpagecount"] = row["axispagecount"]
                elif row["recordspagecount"] is not None:
                    requestdetail["requestpagecount"] = row["recordspagecount"]
                elif row["axispagecount"] is not None:
                    requestdetail["requestpagecount"] = row["axispagecount"]
                else:
                    requestdetail["requestpagecount"] = "0"
                requestdetail["axislanpagecount"]=row["axislanpagecount"]
                requestdetail["estimatedpagecount"]=row["estimatedpagecount"]
                requestdetail["estimatedtaggedpagecount"]=row["estimatedtaggedpagecount"]
                requestdetail["description"]=row["description"]
                requestdetail["requestType"]=row["requesttype"]
                requestdetail["bcgovcode"]=row["programareacode"]
                requestdetails.append(requestdetail)

        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return requestdetails
class FOIMinistryRequestSchema(ma.Schema):
    class Meta:
        fields = ('foiministryrequestid','version','filenumber','description','recordsearchfromdate','recordsearchtodate',
                'startdate','duedate','assignedgroup','assignedto','programarea.programareaid',
                'foirequest.foirequestid','foirequest.requesttype','foirequest.receiveddate','foirequest.deliverymodeid',
                'foirequest.receivedmodeid','requeststatus.requeststatusid','requeststatuslabel','requeststatus.name','programarea.bcgovcode',
                'programarea.name','foirequest_id','foirequestversion_id','created_at','updated_at','createdby','assignedministryperson',
                'assignedministrygroup','cfrduedate','closedate','closereasonid','closereason.name',
                'assignee.firstname','assignee.lastname','ministryassignee.firstname','ministryassignee.lastname', 'axisrequestid', 
                'axissyncdate', 'axispagecount', 'axislanpagecount', 'linkedrequests', 'ministrysignoffapproval', 'identityverified','originalldd',
                'isoipcreview', 'isphasedrelease', 'recordspagecount', 'estimatedpagecount', 'estimatedtaggedpagecount', 'userrecordslockstatus', 'isconsultflag')
    
