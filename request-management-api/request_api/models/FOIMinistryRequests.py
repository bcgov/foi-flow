from flask.app import Flask
from sqlalchemy.sql.schema import ForeignKey, ForeignKeyConstraint
from .db import  db, ma
from datetime import datetime
from sqlalchemy.orm import relationship, backref, aliased
from .default_method_result import DefaultMethodResult
from .FOIRequests import FOIRequest, FOIRequestsSchema
from sqlalchemy.sql.expression import distinct
from sqlalchemy import or_, and_, text, func, literal, cast
from sqlalchemy.sql.sqltypes import String

from .FOIRequestApplicantMappings import FOIRequestApplicantMapping
from .FOIRequestApplicants import FOIRequestApplicant
from .FOIRequestStatus import FOIRequestStatus
from .ApplicantCategories import ApplicantCategory
from .FOIRequestWatchers import FOIRequestWatcher
from .ProgramAreas import ProgramArea
from request_api.utils.enums import ProcessingTeamWithKeycloackGroup
from .FOIAssignees import FOIAssignee

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
    assignedto = db.Column(db.String(120), ForeignKey('FOIAssignees.username'), unique=False, nullable=True)
                
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=True)
    createdby = db.Column(db.String(120), unique=False, nullable=True)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)
    assignedministryperson = db.Column(db.String(120), ForeignKey('FOIAssignees.username'), unique=False, nullable=True)
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
    assignee = relationship('FOIAssignee', foreign_keys="[FOIMinistryRequest.assignedto]")
    ministryassignee = relationship('FOIAssignee', foreign_keys="[FOIMinistryRequest.assignedministryperson]")

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
        elif (group in ProcessingTeamWithKeycloackGroup.list()):
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
    def getrequestssubquery(cls, groups, filterfields, keyword, additionalfilter, userid, iaoassignee, ministryassignee):
        _session = db.session

        #ministry filter for group/team
        ministryfilter = FOIMinistryRequest.getgroupfilters(groups)

        #subquery for getting latest version & proper group/team for FOIMinistryRequest
        subquery_ministry_maxversion = _session.query(FOIMinistryRequest.foiministryrequestid, func.max(FOIMinistryRequest.version).label('max_version')).group_by(FOIMinistryRequest.foiministryrequestid).subquery()
        joincondition_ministry = [
            subquery_ministry_maxversion.c.foiministryrequestid == FOIMinistryRequest.foiministryrequestid,
            subquery_ministry_maxversion.c.max_version == FOIMinistryRequest.version,
        ]

        #subquery for getting the first applicant mapping
        subquery_applicantmapping_first = _session.query(FOIRequestApplicantMapping.foirequest_id, FOIRequestApplicantMapping.foirequestversion_id, func.min(FOIRequestApplicantMapping.foirequestapplicantid).label('first_id')).group_by(FOIRequestApplicantMapping.foirequest_id, FOIRequestApplicantMapping.foirequestversion_id).subquery()
        joincondition_applicantmapping = [
            subquery_applicantmapping_first.c.foirequest_id == FOIRequestApplicantMapping.foirequest_id,
            subquery_applicantmapping_first.c.foirequestversion_id == FOIRequestApplicantMapping.foirequestversion_id,
            subquery_applicantmapping_first.c.first_id == FOIRequestApplicantMapping.foirequestapplicantid,
        ]

        #filter/search
        if(len(filterfields) > 0 and keyword is not None):
            filtercondition = []
            for field in filterfields:
                filtercondition.append(FOIMinistryRequest.findfield(field, iaoassignee, ministryassignee).ilike('%'+keyword+'%'))

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
            FOIMinistryRequest.foiministryrequestid.label('ministryrequestid'),
            FOIMinistryRequest.assignedministrygroup.label('assignedministrygroup'),
            FOIMinistryRequest.assignedministryperson.label('assignedministryperson'),
            cast(FOIMinistryRequest.cfrduedate, String).label('cfrduedate'),
            cast(FOIMinistryRequest.duedate, String).label('duedate'),
            ApplicantCategory.name.label('applicantcategory'),
            FOIRequest.created_at.label('created_at'),
            func.lower(ProgramArea.bcgovcode).label('bcgovcode'),
            iaoassignee.firstname.label('assignedToFirstName'),
            iaoassignee.lastname.label('assignedToLastName'),
            ministryassignee.firstname.label('assignedministrypersonFirstName'),
            ministryassignee.lastname.label('assignedministrypersonLastName'),
            FOIMinistryRequest.description
        ]

        basequery = _session.query(
                                *selectedcolumns
                            ).join(
                                subquery_ministry_maxversion,
                                and_(*joincondition_ministry)
                            ).join(
                                FOIRequest,
                                and_(FOIRequest.foirequestid == FOIMinistryRequest.foirequest_id, FOIRequest.version == FOIMinistryRequest.foirequestversion_id)
                            ).join(
                                FOIRequestStatus,
                                FOIRequestStatus.requeststatusid == FOIMinistryRequest.requeststatusid
                            ).join(
                                FOIRequestApplicantMapping,
                                and_(FOIRequestApplicantMapping.foirequest_id == FOIMinistryRequest.foirequest_id, FOIRequestApplicantMapping.foirequestversion_id == FOIMinistryRequest.foirequestversion_id)
                            ).join(
                                subquery_applicantmapping_first,
                                and_(*joincondition_applicantmapping)
                            ).join(
                                FOIRequestApplicant,
                                FOIRequestApplicant.foirequestapplicantid == FOIRequestApplicantMapping.foirequestapplicantid
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
                            )

        if(additionalfilter == 'watchingRequests'):
            #watchby
            subquery_watchby = FOIRequestWatcher.getrequestidsbyuserid(userid)
            dbquery = basequery.join(subquery_watchby, subquery_watchby.c.ministryrequestid == FOIMinistryRequest.foiministryrequestid).filter(ministryfilter)
        elif(additionalfilter == 'myRequests'):
            #myrequest
            dbquery = basequery.filter(FOIMinistryRequest.assignedministryperson == userid).filter(ministryfilter)
        else:
            dbquery = basequery.filter(ministryfilter)


        if(keyword is None):
            return dbquery
        else:
            return dbquery.filter(or_(*filtercondition))

    @classmethod
    def getrequestspagination(cls, group, page, size, sortingitems, sortingorders, filterfields, keyword, additionalfilter, userid):
        iaoassignee = aliased(FOIAssignee)
        ministryassignee = aliased(FOIAssignee)

        subquery = FOIMinistryRequest.getrequestssubquery(group, filterfields, keyword, additionalfilter, userid, iaoassignee, ministryassignee)

        #sorting
        sortingcondition = []
        if(len(sortingitems) > 0 and len(sortingorders) > 0 and len(sortingitems) == len(sortingorders)):
            for field in sortingitems:
                order = sortingorders.pop()
                if(order == 'desc'):
                    sortingcondition.append(FOIMinistryRequest.findfield(field, iaoassignee, ministryassignee).desc())
                else:
                    sortingcondition.append(FOIMinistryRequest.findfield(field, iaoassignee, ministryassignee).asc())

        #default sorting
        if(len(sortingcondition) == 0):
            sortingcondition.append(FOIMinistryRequest.findfield('currentState', iaoassignee, ministryassignee).asc())
        return subquery.order_by(*sortingcondition).paginate(page=page, per_page=size)

    @classmethod
    def findfield(cls, x, iaoassignee, ministryassignee):
        #add more fields here if need sort/filter/search more columns

        return {
            'firstName': FOIRequestApplicant.firstname,
            'lastName': FOIRequestApplicant.lastname,
            'requestType': FOIRequest.requesttype,
            'idNumber': FOIMinistryRequest.filenumber,
            'rawRequestNumber': FOIMinistryRequest.filenumber,
            'currentState': FOIRequestStatus.name,
            'assignedTo': FOIMinistryRequest.assignedto,
            'receivedDate': FOIRequest.receiveddate,
            'applicantcategory': ApplicantCategory.name,
            'assignedministryperson': FOIMinistryRequest.assignedministryperson,
            'assignedToFirstName': iaoassignee.firstname,
            'assignedToLastName': iaoassignee.lastname,
            'assignedministrypersonFirstName': ministryassignee.firstname,
            'assignedministrypersonLastName': ministryassignee.lastname,
            'description': FOIMinistryRequest.description,
            'requestdescription': FOIMinistryRequest.description,
            'duedate': FOIMinistryRequest.duedate,
            'ministry': func.upper(ProgramArea.bcgovcode)
        }.get(x, FOIMinistryRequest.filenumber)

    @classmethod
    def getgroupfilters(cls, groups):
        #ministry filter for group/team
        if groups is None:
            ministryfilter = FOIMinistryRequest.isactive == True
        else:
            groupfilter = []
            for group in groups:
                if (group == 'Flex Team'):
                    groupfilter.append(
                        and_(
                            FOIMinistryRequest.assignedgroup == group,
                            FOIMinistryRequest.requeststatusid.in_([1,2,3,12,13,7,8,9,10,11,14])
                        )
                    )
                elif (group in ProcessingTeamWithKeycloackGroup.list()):
                    groupfilter.append(
                        and_(
                            FOIMinistryRequest.assignedgroup == group,
                            FOIMinistryRequest.requeststatusid.in_([1,2,12,13,7,9,10,14,3])
                        )
                    )
                elif (group == 'Intake Team'):
                    groupfilter.append(
                        or_(
                            FOIMinistryRequest.assignedgroup == group,
                            FOIMinistryRequest.requeststatusid.in_([1])
                        )
                    )
                else:
                    groupfilter.append(
                        or_(
                            FOIMinistryRequest.assignedgroup == group,
                            and_(
                                FOIMinistryRequest.assignedministrygroup == group,
                                FOIMinistryRequest.requeststatusid.in_([2,7,9,8,10,11,12,13,14])
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
    def getupcomingcfrduerecords(cls):
        sql = """select distinct on (filenumber) filenumber, cfrduedate, foiministryrequestid, version, foirequest_id, created_at, createdby from "FOIMinistryRequests" fpa 
                    where isactive = true and cfrduedate is not null and requeststatusid = 2  
                    and cfrduedate between  NOW() - INTERVAL '7 DAY' AND NOW() + INTERVAL '7 DAY'
                    order by filenumber , version desc;""" 
        rs = db.session.execute(text(sql))
        upcomingduerecords = []
        for row in rs:
            upcomingduerecords.append({"filenumber": row["filenumber"], "cfrduedate": row["cfrduedate"],"foiministryrequestid": row["foiministryrequestid"], "version": row["version"], "foirequest_id": row["foirequest_id"], "created_at": row["created_at"], "createdby": row["createdby"]})
        return upcomingduerecords    

    @classmethod
    def getupcominglegislativeduerecords(cls):
        sql = """select distinct on (filenumber) filenumber, duedate, foiministryrequestid, version, foirequest_id, created_at, createdby from "FOIMinistryRequests" fpa 
                    where isactive = true and duedate is not null and requeststatusid not in (5,6,4,11,3,15)     
                    and duedate between  NOW() - INTERVAL '7 DAY' AND NOW() + INTERVAL '7 DAY'
                    order by filenumber , version desc;""" 
        rs = db.session.execute(text(sql))
        upcomingduerecords = []
        for row in rs:
            upcomingduerecords.append({"filenumber": row["filenumber"], "duedate": row["duedate"],"foiministryrequestid": row["foiministryrequestid"], "version": row["version"], "foirequest_id": row["foirequest_id"], "created_at": row["created_at"], "createdby": row["createdby"]})
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
        sql = """select distinct filenumber, foiministryrequestid, foirequest_id, pa."name" from "FOIMinistryRequests" fpa 
                    inner join  "FOIRequests" frt on fpa.foirequest_id  = frt.foirequestid and fpa.foirequestversion_id = frt."version" 
                    inner join "ProgramAreas" pa on fpa.programareaid  = pa.programareaid 
                    where fpa.isactive = true and frt.isactive =true and frt.foirawrequestid=:rawrequestid;""" 
        rs = db.session.execute(text(sql), {'rawrequestid': rawrequestid})
        ministries = []
        for row in rs:
            ministries.append({"filenumber": row["filenumber"], "name": row["name"], "requestid": row["foirequest_id"],"ministryrequestid": row["foiministryrequestid"]})
        return ministries

    @classmethod
    def getbasequery(cls, iaoassignee, ministryassignee):
        _session = db.session

        #ministry filter for group/team
        ministryfilter = and_(FOIMinistryRequest.isactive == True, FOIRequestStatus.isactive == True)

        #subquery for getting latest version & proper group/team for FOIMinistryRequest
        subquery_ministry_maxversion = _session.query(FOIMinistryRequest.foiministryrequestid, func.max(FOIMinistryRequest.version).label('max_version')).group_by(FOIMinistryRequest.foiministryrequestid).subquery()
        joincondition_ministry = [
            subquery_ministry_maxversion.c.foiministryrequestid == FOIMinistryRequest.foiministryrequestid,
            subquery_ministry_maxversion.c.max_version == FOIMinistryRequest.version,
        ]

        #subquery for getting the first applicant mapping
        subquery_applicantmapping_first = _session.query(FOIRequestApplicantMapping.foirequest_id, FOIRequestApplicantMapping.foirequestversion_id, func.min(FOIRequestApplicantMapping.foirequestapplicantid).label('first_id')).group_by(FOIRequestApplicantMapping.foirequest_id, FOIRequestApplicantMapping.foirequestversion_id).subquery()
        joincondition_applicantmapping = [
            subquery_applicantmapping_first.c.foirequest_id == FOIRequestApplicantMapping.foirequest_id,
            subquery_applicantmapping_first.c.foirequestversion_id == FOIRequestApplicantMapping.foirequestversion_id,
            subquery_applicantmapping_first.c.first_id == FOIRequestApplicantMapping.foirequestapplicantid,
        ]

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
            FOIMinistryRequest.foiministryrequestid.label('ministryrequestid'),
            FOIMinistryRequest.assignedministrygroup.label('assignedministrygroup'),
            FOIMinistryRequest.assignedministryperson.label('assignedministryperson'),
            cast(FOIMinistryRequest.cfrduedate, String).label('cfrduedate'),
            cast(FOIMinistryRequest.duedate, String).label('duedate'),
            ApplicantCategory.name.label('applicantcategory'),
            FOIRequest.created_at.label('created_at'),
            func.lower(ProgramArea.bcgovcode).label('bcgovcode'),
            iaoassignee.firstname.label('assignedToFirstName'),
            iaoassignee.lastname.label('assignedToLastName'),
            ministryassignee.firstname.label('assignedministrypersonFirstName'),
            ministryassignee.lastname.label('assignedministrypersonLastName'),
            FOIMinistryRequest.description
        ]

        basequery = _session.query(
                                *selectedcolumns
                            ).join(
                                subquery_ministry_maxversion,
                                and_(*joincondition_ministry)
                            ).join(
                                FOIRequest,
                                and_(FOIRequest.foirequestid == FOIMinistryRequest.foirequest_id, FOIRequest.version == FOIMinistryRequest.foirequestversion_id)
                            ).join(
                                FOIRequestStatus,
                                FOIRequestStatus.requeststatusid == FOIMinistryRequest.requeststatusid
                            ).join(
                                FOIRequestApplicantMapping,
                                and_(FOIRequestApplicantMapping.foirequest_id == FOIMinistryRequest.foirequest_id, FOIRequestApplicantMapping.foirequestversion_id == FOIMinistryRequest.foirequestversion_id)
                            ).join(
                                subquery_applicantmapping_first,
                                and_(*joincondition_applicantmapping)
                            ).join(
                                FOIRequestApplicant,
                                FOIRequestApplicant.foirequestapplicantid == FOIRequestApplicantMapping.foirequestapplicantid
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
                            )

        return basequery.filter(ministryfilter)

    @classmethod
    def advancedsearch(cls, params, iaoassignee, ministryassignee):
        basequery = FOIMinistryRequest.getbasequery(iaoassignee, ministryassignee)

        #filter/search
        filtercondition = FOIMinistryRequest.getfilterforadvancedsearch(params, iaoassignee, ministryassignee)
        return basequery.filter(and_(*filtercondition))

    @classmethod
    def getfilterforadvancedsearch(cls, params, iaoassignee, ministryassignee):

        #filter/search
        filtercondition = []

        #request state: unopened, call for records, etc.
        if(len(params['requeststate']) > 0):
            requeststatecondition = []
            for stateid in params['requeststate']:
                requeststatecondition.append(FOIMinistryRequest.requeststatusid == stateid)
            filtercondition.append(or_(*requeststatecondition))
        
        #request status: overdue || on time
        # if(len(params['requeststatus']) == 1):
        #     if(params['requeststatus'][0] == 'overdue'):
        #         filtercondition.append(FOIMinistryRequest.findfield('duedate', iaoassignee, ministryassignee) < datetime.now())
        #     else:
        #         filtercondition.append(FOIMinistryRequest.findfield('duedate', iaoassignee, ministryassignee) >= datetime.now())

        #request type: personal, general
        if(len(params['requesttype']) > 0):
            requesttypecondition = []
            for type in params['requesttype']:
                requesttypecondition.append(FOIMinistryRequest.findfield('requestType', iaoassignee, ministryassignee) == type)
            filtercondition.append(or_(*requesttypecondition))
        
        #public body: EDUC, etc.
        if(len(params['publicbody']) > 0):
            publicbodycondition = []
            for ministry in params['publicbody']:
                publicbodycondition.append(FOIMinistryRequest.findfield('ministry', iaoassignee, ministryassignee) == ministry)
            filtercondition.append(or_(*publicbodycondition))

        #axis request #, raw request #, applicant name, assignee name, request description, subject code
        if(len(params['keywords']) > 0 and params['search'] is not None):
            if(params['search'] == 'applicantname'):
                searchcondition1 = []
                searchcondition2 = []
                for keyword in params['keywords']:
                    searchcondition1.append(FOIMinistryRequest.findfield('firstName', iaoassignee, ministryassignee).ilike('%'+keyword+'%'))
                    searchcondition2.append(FOIMinistryRequest.findfield('lastName', iaoassignee, ministryassignee).ilike('%'+keyword+'%'))
                filtercondition.append(or_(and_(*searchcondition1), and_(*searchcondition2)))
            elif(params['search'] == 'assigneename'):
                searchcondition1 = []
                searchcondition2 = []
                for keyword in params['keywords']:
                    searchcondition1.append(FOIMinistryRequest.findfield('assignedToFirstName', iaoassignee, ministryassignee).ilike('%'+keyword+'%'))
                    searchcondition2.append(FOIMinistryRequest.findfield('assignedToLastName', iaoassignee, ministryassignee).ilike('%'+keyword+'%'))
                filtercondition.append(or_(and_(*searchcondition1), and_(*searchcondition2)))
            else:
                searchcondition = []
                for keyword in params['keywords']:
                    searchcondition.append(FOIMinistryRequest.findfield(params['search'], iaoassignee, ministryassignee).ilike('%'+keyword+'%'))
                filtercondition.append(and_(*searchcondition))

        # if(params['fromdate'] is not None):
        #     filtercondition.append(FOIMinistryRequest.findfield('receivedDate', iaoassignee, ministryassignee) >= params['fromdate'])

        # if(params['todate'] is not None):
        #     filtercondition.append(FOIMinistryRequest.findfield('duedate', iaoassignee, ministryassignee) <= params['todate'])
        
        return filtercondition
class FOIMinistryRequestSchema(ma.Schema):
    class Meta:
        fields = ('foiministryrequestid','version','filenumber','description','recordsearchfromdate','recordsearchtodate',
                'startdate','duedate','assignedgroup','assignedto','programarea.programareaid','requeststatus.requeststatusid',
                'foirequest.foirequestid','foirequest.requesttype','foirequest.receiveddate','foirequest.deliverymodeid',
                'foirequest.receivedmodeid','requeststatus.requeststatusid','requeststatus.name','programarea.bcgovcode',
                'programarea.name','foirequest_id','foirequestversion_id','created_at','updated_at','createdby','assignedministryperson',
                'assignedministrygroup','cfrduedate','closedate','closereasonid','closereason.name',
                'assignee.firstname','assignee.lastname','ministryassignee.firstname','ministryassignee.lastname')
    