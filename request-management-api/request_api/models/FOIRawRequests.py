from enum import unique

from sqlalchemy.sql.sqltypes import DateTime, String, Date, Integer

from flask.app import Flask
from sqlalchemy.sql.schema import ForeignKey, ForeignKeyConstraint
from sqlalchemy.sql.expression import distinct
from .db import  db, ma
from sqlalchemy.dialects.postgresql import JSON, UUID
from .default_method_result import DefaultMethodResult
from datetime import datetime
from sqlalchemy.orm import relationship, backref, aliased
from sqlalchemy import insert, and_, or_, text, func, literal, cast, asc, desc, case, nullsfirst, nullslast, TIMESTAMP

from .FOIMinistryRequests import FOIMinistryRequest
from .FOIRawRequestWatchers import FOIRawRequestWatcher
from .FOIRequestApplicants import FOIRequestApplicant
from .FOIAssignees import FOIAssignee
import logging
from dateutil import parser
import json
from request_api.utils.enums import StateName
from request_api.utils.enums import ProcessingTeamWithKeycloackGroup, IAOTeamWithKeycloackGroup

class FOIRawRequest(db.Model):
    # Name of the table in our database
    __tablename__ = 'FOIRawRequests' 
    # Defining the columns
    requestid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    version = db.Column(db.Integer, primary_key=True,nullable=False)
    requestrawdata = db.Column(JSON, unique=False, nullable=True)
    status = db.Column(db.String(25), unique=False, nullable=True)
    requeststatuslabel = db.Column(db.String(50), unique=False, nullable=False)
    notes = db.Column(db.String(120), unique=False, nullable=True)
    wfinstanceid = db.Column(UUID(as_uuid=True), unique=False, nullable=True)
    assignedgroup = db.Column(db.String(250), unique=False, nullable=True) 
    assignedto = db.Column(db.String(120), ForeignKey('FOIAssignees.username'), unique=False, nullable=True)    
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=True)
    createdby = db.Column(db.String(120), unique=False, nullable=True)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)
    sourceofsubmission = db.Column(db.String(120),  nullable=True)
    ispiiredacted = db.Column(db.Boolean, unique=False, nullable=False,default=False)    
    closedate = db.Column(db.DateTime, nullable=True)    
    requirespayment = db.Column(db.Boolean, unique=False, nullable=True, default=False)
    
    axissyncdate = db.Column(db.DateTime, nullable=True)    
    axisrequestid = db.Column(db.String(120), nullable=True)
    linkedrequests = db.Column(JSON, unique=False, nullable=True)


    isiaorestricted = db.Column(db.Boolean, unique=False, nullable=False,default=False)

    closereasonid = db.Column(db.Integer,ForeignKey('CloseReasons.closereasonid'))
    closereason = relationship("CloseReason", uselist=False)

    assignee = relationship('FOIAssignee', foreign_keys="[FOIRawRequest.assignedto]")

    @classmethod
    def saverawrequest(cls, _requestrawdata, sourceofsubmission, ispiiredacted, userid, notes, requirespayment, axisrequestid, axissyncdate, linkedrequests, assigneegroup=None, assignee=None, assigneefirstname=None, assigneemiddlename=None, assigneelastname=None)->DefaultMethodResult:        
        version = 1
        newrawrequest = FOIRawRequest(requestrawdata=_requestrawdata, status = StateName.unopened.value if sourceofsubmission != "intake" else StateName.intakeinprogress.value, requeststatuslabel = StateName.unopened.name if sourceofsubmission != "intake" else StateName.intakeinprogress.name, createdby=userid, version=version, sourceofsubmission=sourceofsubmission, assignedgroup=assigneegroup, assignedto=assignee, ispiiredacted=ispiiredacted, notes=notes, requirespayment=requirespayment, axisrequestid=axisrequestid, axissyncdate=axissyncdate, linkedrequests=linkedrequests)
        if assignee is not None:
            FOIAssignee.saveassignee(assignee, assigneefirstname, assigneemiddlename, assigneelastname)

        db.session.add(newrawrequest)
        db.session.commit()               
        return DefaultMethodResult(True,'Request added',newrawrequest.requestid)

    @classmethod
    def saverawrequest_foipayment(cls,_requestrawdata,notes, requirespayment, ispiiredacted)->DefaultMethodResult: 
        version = 1
        newrawrequest = FOIRawRequest(requestrawdata=_requestrawdata, status=StateName.unopened.value, requeststatuslabel = StateName.unopened.name ,createdby=None,version=version,sourceofsubmission="onlineform",assignedgroup=None,assignedto=None,ispiiredacted=ispiiredacted,notes=notes, requirespayment= requirespayment)
        db.session.add(newrawrequest)
        db.session.commit()               
        return DefaultMethodResult(True,'Request added',newrawrequest.requestid)

    @classmethod
    def saverawrequestversion(cls,_requestrawdata,requestid,assigneegroup,assignee,status,ispiiredacted,userid,statuslabel,assigneefirstname=None,assigneemiddlename=None,assigneelastname=None)->DefaultMethodResult:        
        request = db.session.query(FOIRawRequest).filter_by(requestid=requestid).order_by(FOIRawRequest.version.desc()).first()
        if request is not None:
            _assginee = assignee if assignee not in (None,'') else None
            if _assginee not in (None,''):
                FOIAssignee.saveassignee(_assginee, assigneefirstname, assigneemiddlename, assigneelastname)

            closedate = _requestrawdata["closedate"] if 'closedate' in _requestrawdata  else None
            closereasonid = _requestrawdata["closereasonid"] if 'closereasonid' in _requestrawdata  else None
            axisrequestid = _requestrawdata["axisRequestId"] if 'axisRequestId' in _requestrawdata  else None
            axissyncdate = _requestrawdata["axisSyncDate"] if 'axisSyncDate' in _requestrawdata  else None   
            linkedrequests = _requestrawdata["linkedRequests"] if 'linkedRequests' in _requestrawdata  else None     
            _version = request.version+1           
            insertstmt =(
                insert(FOIRawRequest).
                values(
                    requestid=request.requestid, 
                    requestrawdata=_requestrawdata,
                    version=_version,
                    updatedby=None,
                    updated_at=datetime.now(),
                    status=status,
                    requeststatuslabel=statuslabel,
                    assignedgroup=assigneegroup,
                    assignedto=_assginee,
                    wfinstanceid=request.wfinstanceid,
                    sourceofsubmission=request.sourceofsubmission,
                    ispiiredacted=ispiiredacted,
                    createdby=userid,
                    closedate=closedate,
                    closereasonid=closereasonid,
                    axisrequestid= axisrequestid,
                    axissyncdate=axissyncdate,
                    linkedrequests=linkedrequests,
                    isiaorestricted = request.isiaorestricted
                   
                )
            )
            db.session.execute(insertstmt)               
            db.session.commit()                
            return DefaultMethodResult(True,'Request versioned - {0}'.format(str(_version)),requestid,request.wfinstanceid,assignee)    
        else:
            return DefaultMethodResult(True,'No request foound')
    

    @classmethod
    def saveiaorestrictedrawrequest(cls,requestid,_isiaorestricted=False, _updatedby=None)->DefaultMethodResult:
        currentrequest = db.session.query(FOIRawRequest).filter_by(requestid=requestid).order_by(FOIRawRequest.version.desc()).first()
        request = currentrequest
        _version = currentrequest.version+1               
        insertstmt = (
            insert(FOIRawRequest).
            values(
                    requestid=request.requestid, 
                    requestrawdata=request.requestrawdata,
                    version=_version,
                    updatedby=_updatedby,
                    updated_at=datetime.now(),
                    status=request.status,
                    assignedgroup=request.assignedgroup,
                    assignedto=request.assignedto,
                    wfinstanceid=request.wfinstanceid,
                    sourceofsubmission=request.sourceofsubmission,
                    ispiiredacted=request.ispiiredacted,
                    createdby=request.createdby,
                    closedate=request.closedate,
                    closereasonid=request.closereasonid,
                    axisrequestid= request.axisrequestid,
                    axissyncdate=request.axissyncdate,
                    linkedrequests=request.linkedrequests,
                    created_at=request.created_at,
                    requirespayment = request.requirespayment,
                    isiaorestricted =_isiaorestricted,
                    notes = request.notes,
                    requeststatuslabel = request.requeststatuslabel,
                    
            )
        )
        db.session.execute(insertstmt)               
        db.session.commit()                
        return DefaultMethodResult(True,'Request Updated for iaorestricted - {0}'.format(str(request.version)),requestid,request.wfinstanceid,_isiaorestricted)    

    @classmethod
    def saverawrequestassigneeversion(cls,requestid,assigneegroup,assignee,userid,assigneefirstname=None,assigneemiddlename=None,assigneelastname=None)->DefaultMethodResult:        
        request = db.session.query(FOIRawRequest).filter_by(requestid=requestid).order_by(FOIRawRequest.version.desc()).first()
        if request is not None:
            _assginee = assignee if assignee not in (None,'') else None
            if _assginee not in (None,''):
                FOIAssignee.saveassignee(_assginee, assigneefirstname, assigneemiddlename, assigneelastname)

            closedate = request.closedate
            closereasonid = request.closereasonid
            axisrequestid = request.axisrequestid
            axissyncdate = request.axissyncdate
            linkedrequests=request.linkedrequests
            _version = request.version+1
            rawrequest = request.requestrawdata
            rawrequest["assignedGroup"] = assigneegroup
            rawrequest["assignedTo"] = _assginee
            rawrequest["assignedToFirstName"] = assigneefirstname
            rawrequest["assignedToLastName"] = assigneelastname
            insertstmt =(
                insert(FOIRawRequest).
                values(
                    requestid=request.requestid, 
                    requestrawdata=rawrequest,
                    version=_version,
                    updatedby=None,
                    updated_at=datetime.now(),
                    status=request.status,
                    assignedgroup=assigneegroup,
                    assignedto=_assginee,
                    wfinstanceid=request.wfinstanceid,
                    sourceofsubmission=request.sourceofsubmission,
                    ispiiredacted=request.ispiiredacted,
                    createdby=userid,
                    closedate=closedate,
                    closereasonid=closereasonid,
                    axisrequestid= axisrequestid,
                    axissyncdate=axissyncdate,
                    linkedrequests=linkedrequests,
                    isiaorestricted = request.isiaorestricted,
                    requeststatuslabel = request.requeststatuslabel                    
                )
            )
            db.session.execute(insertstmt)               
            db.session.commit()                
            return DefaultMethodResult(True,'Request versioned - {0}'.format(str(_version)),requestid,request.wfinstanceid,assignee)    
        else:
            return DefaultMethodResult(True,'No request foound')

    @classmethod
    def getworkflowinstancebyraw(cls,requestid)->DefaultMethodResult:
        request_schema = FOIRawRequestSchema()
        try:
            sql = """select wfinstanceid, assignedto, assignedgroup, requestid  from "FOIRawRequests" fr where requestid = :requestid order by "version" desc limit 1;"""
            rs = db.session.execute(text(sql), {'requestid': requestid})
            for row in rs:
                request_schema.__dict__.update({"requestid": row["requestid"],"assignedto": row["assignedto"], "assignedgroup": row["assignedgroup"], "wfinstanceid": row["wfinstanceid"]})
        except Exception as ex:
            logging.error(ex)
        finally:
            db.session.close()  
        return request_schema


    @classmethod
    def getworkflowinstancebyministry(cls,requestid)->DefaultMethodResult:
        request_schema = FOIRawRequestSchema()
        try:
            sql = """select fr.wfinstanceid,  fr.assignedto,  fr.assignedgroup, fr.requestid 
                        from "FOIMinistryRequests" fr2, "FOIRequests" fr3, "FOIRawRequests" fr 
                        where fr2.foirequest_id = fr3.foirequestid and fr3.foirawrequestid  = fr.requestid 
                        and fr2.foiministryrequestid= :requestid order by fr."version" desc limit 1"""
            rs = db.session.execute(text(sql), {'requestid': requestid})
            for row in rs:
                request_schema.__dict__.update({"requestid": row["requestid"], "assignedto": row["assignedto"], "assignedgroup": row["assignedgroup"], "wfinstanceid": row["wfinstanceid"]})
        except Exception as ex:
            logging.error(ex)
        finally:
            db.session.close()  
        return request_schema
            
    @classmethod
    def updateworkflowinstance(cls,wfinstanceid,requestid, userid)->DefaultMethodResult:
        updatedat = datetime.now()
        dbquery = db.session.query(FOIRawRequest)
        requestraqw = dbquery.filter_by(requestid=requestid,version = 1)
        if(requestraqw.count() > 0) :
            existingrequestswithwfid = dbquery.filter_by(wfinstanceid=wfinstanceid)               
            if(existingrequestswithwfid.count() == 0) :
                requestraqw.update({FOIRawRequest.wfinstanceid:wfinstanceid, FOIRawRequest.updated_at:updatedat,FOIRawRequest.updatedby:userid, FOIRawRequest.notes:"WF Instance created"}, synchronize_session = False)
                db.session.commit()
                return DefaultMethodResult(True,'Request updated with WF Instance Id',requestid)
            else:
                return DefaultMethodResult(False,'WF instance already exists',requestid) 
        else:
            return DefaultMethodResult(False,'Requestid not exists',-1)      

    @classmethod
    def updateworkflowinstance_n(cls,wfinstanceid,requestid, userid)->DefaultMethodResult:
        updatedat = datetime.now()
        dbquery = db.session.query(FOIRawRequest)
        _requestraqw = dbquery.filter_by(requestid=requestid).order_by(FOIRawRequest.version.desc()).first()
        requestraqw = dbquery.filter_by(requestid=requestid,version = _requestraqw.version)        
        if(requestraqw.count() > 0) :            
            requestraqw.update({FOIRawRequest.wfinstanceid:wfinstanceid, FOIRawRequest.updated_at:updatedat,FOIRawRequest.updatedby:userid}, synchronize_session = False)
            db.session.commit()
            return DefaultMethodResult(True,'Request updated',requestid)       
        else:
            return DefaultMethodResult(False,'Requestid not exists',-1)        

    @classmethod
    def updateworkflowinstancewithstatus(cls,wfinstanceid,requestid,notes,userid)-> DefaultMethodResult:
        updatedat = datetime.now()
        dbquery = db.session.query(FOIRawRequest)
        _requestraqw = dbquery.filter_by(requestid=requestid).order_by(FOIRawRequest.version.desc()).first()
        requestraqw = dbquery.filter_by(requestid=requestid,version = _requestraqw.version)        
        if(requestraqw.count() > 0) :            
            request_schema = FOIRawRequestSchema()
            request = request_schema.dump(_requestraqw)            
            status = request["status"]
                                
            requestraqw.update({FOIRawRequest.wfinstanceid:wfinstanceid, FOIRawRequest.updated_at:updatedat,FOIRawRequest.notes:notes,FOIRawRequest.status:status,FOIRawRequest.updatedby:userid}, synchronize_session = False)
            db.session.commit()
            return DefaultMethodResult(True,'Request updated',requestid)       
        else:
            return DefaultMethodResult(False,'Requestid not exists',-1)    

    @classmethod
    def getrequests(cls):
        _session = db.session
        _archivedrequestids = _session.query(distinct(FOIRawRequest.requestid)).filter(FOIRawRequest.status.in_(['Archived'])).all()
        _requestids = _session.query(distinct(FOIRawRequest.requestid)).filter(FOIRawRequest.requestid.notin_(_archivedrequestids)).all()
        requests = []
        for _requestid in _requestids:
           request = _session.query(FOIRawRequest).filter(FOIRawRequest.requestid == _requestid).order_by(FOIRawRequest.version.desc()).first()           
           requests.append(request)

        return requests
    

    @classmethod
    def getDescriptionSummaryById(cls, requestid):
        requests = []
        try:
            sql = """select * ,
                        CASE WHEN description = (select requestrawdata -> 'descriptionTimeframe' ->> 'description' from "FOIRawRequests" where requestid = :requestid and status = :requeststatus and version = 1) 
                                then 'Online Form' 
                                else savedby END  as createdby 
                        from (select CASE WHEN lower(status) <> 'unopened' 
                                then requestrawdata ->> 'description' 
                                ELSE requestrawdata -> 'descriptionTimeframe' ->> 'description' END as description ,  
                            CASE WHEN lower(status) <> 'unopened' 
                                then requestrawdata ->> 'fromDate' 
                                ELSE requestrawdata -> 'descriptionTimeframe' ->> 'fromDate' END as fromdate, 
                            CASE WHEN lower(status) <> 'unopened'
                                then requestrawdata ->> 'toDate' 
                                ELSE requestrawdata -> 'descriptionTimeframe' ->> 'toDate' END as todate, 
                            to_char(created_at, 'YYYY-MM-DD HH24:MI:SS') as createdat, status, ispiiredacted,
                            createdby as savedby from "FOIRawRequests" fr 
                        where requestid = :requestid order by version ) as sq;"""
            rs = db.session.execute(text(sql), {'requestid': requestid, 'requeststatus': StateName.unopened.value})
            for row in rs:
                requests.append(dict(row))
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return requests

    @classmethod
    def get_request(cls,requestid):   
       request_schema = FOIRawRequestSchema()
       request = db.session.query(FOIRawRequest).filter_by(requestid=requestid).order_by(FOIRawRequest.version.desc()).first()
       return request_schema.dump(request)
    
    @classmethod
    def getrawrequestsbyapplicantid(cls,applicantid):
        request_schema = FOIRawRequestSchema(many=True)
        applicant_subquery = db.session.query(FOIRequestApplicant.applicantprofileid).filter(FOIRequestApplicant.foirequestapplicantid == applicantid).subquery()
        subquery_applicant_id_list = db.session.query(FOIRequestApplicant.foirequestapplicantid).filter(applicant_subquery.c.applicantprofileid == FOIRequestApplicant.applicantprofileid).subquery()

        #subquery for getting the latest version
        subquery_maxversion = db.session.query(FOIRawRequest.requestid, func.max(FOIRawRequest.version).label('max_version')).group_by(FOIRawRequest.requestid).subquery()
        joincondition = [
            subquery_maxversion.c.requestid == FOIRawRequest.requestid,
            subquery_maxversion.c.max_version == FOIRawRequest.version,
        ]
        
        query = db.session.query(FOIRawRequest).distinct(FOIRawRequest.requestid).join(
            FOIAssignee, FOIAssignee.username == FOIRawRequest.assignedto
        ).join(
            subquery_maxversion,
            and_(*joincondition)
        ).filter(
            FOIRawRequest.requestrawdata['foiRequestApplicantID'].astext.cast(db.Integer).in_(subquery_applicant_id_list),
            FOIRawRequest.status.notin_(['Archived', 'Closed'])
        ).order_by(FOIRawRequest.requestid.desc()).all()
        return request_schema.dump(query)
    
    @classmethod
    def getLastStatusUpdateDate(cls,requestid,status):
        lastupdatedate = None
        try:
            sql = """select created_at from "FOIRawRequests" 
                        where requestid = :requestid and status = :status
                        order by version desc limit 1;"""
            rs = db.session.execute(text(sql), {'requestid': requestid, 'status': status})
            lastupdatedate = [row[0] for row in rs][0]
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return lastupdatedate

    @classmethod
    def getassignmenttransition(cls,requestid):
        assignments = []
        try:
            sql = """select version, assignedto, status from "FOIRawRequests" 
                        where requestid = :requestid
                        order by version desc limit 2;"""
            rs = db.session.execute(text(sql), {'requestid': requestid})            
            for row in rs:
                assignments.append({"assignedto": row["assignedto"], "status": row["status"], "version": row["version"]})
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return assignments
    
    @classmethod
    def getappfeeowingrequests(cls): # with the reminder date
        appfeeowingrequests = []
        try:
            sql = '''
                    SELECT * FROM (SELECT DISTINCT ON (requestid) requestid, updated_at, status FROM public."FOIRawRequests"
	                ORDER BY requestid ASC, version DESC) r
                    WHERE r.status = :requeststaus
					order by r.updated_at asc
                    '''
            rs = db.session.execute(text(sql), {'requeststaus': StateName.appfeeowing.value})
            appfeeowingrequests = rs
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return appfeeowingrequests

    @classmethod
    def getversionforrequest(cls,requestid):   
        return db.session.query(FOIRawRequest.version).filter_by(requestid=requestid).order_by(FOIRawRequest.version.desc()).first()
    
    # @classmethod
    # def getstatesummary(cls, requestid):     
    #     transitions = []
    #     try:           
    #         sql = """select status, version from (select distinct on (status) status, version from "FOIRawRequests" 
    #         where requestid=:requestid order by status, version asc) as fs3 order by version desc"""
    #         rs = db.session.execute(text(sql), {'requestid': requestid})
            
    #         for row in rs:
    #             transitions.append({"status": row["status"], "version": row["version"]})
    #     except Exception as ex:
    #         logging.error(ex)
    #         raise ex
    #     finally:
    #         db.session.close()
    #     return transitions

    @classmethod
    def getstatesummary(cls, requestid):  
        transitions = []
        try:
            sql = """select status, version from "FOIRawRequests" where requestid=:requestid order by version desc"""
            rs = db.session.execute(text(sql), {'requestid': requestid})  
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
    def getstatenavigation(cls, requestid):
        _session = db.session
        _requeststates = _session.query(FOIRawRequest.status).filter(FOIRawRequest.requestid == requestid).order_by(FOIRawRequest.version.desc()).limit(2)
        requeststates = []
        for _requeststate in _requeststates:
            requeststates.append(_requeststate[0])
        return requeststates    

    @classmethod
    def getbasequery(cls, additionalfilter=None, userid=None, isiaorestrictedfilemanager=False, groups=[]):
        _session = db.session

        #rawrequests
        #subquery for getting the latest version
        subquery_maxversion = _session.query(FOIRawRequest.requestid, func.max(FOIRawRequest.version).label('max_version')).group_by(FOIRawRequest.requestid).subquery()
        joincondition = [
            subquery_maxversion.c.requestid == FOIRawRequest.requestid,
            subquery_maxversion.c.max_version == FOIRawRequest.version,
        ]

        requesttype = case([
                            (FOIRawRequest.status == StateName.unopened.value,
                             FOIRawRequest.requestrawdata['requestType']['requestType'].astext),
                           ],
                           else_ = FOIRawRequest.requestrawdata['requestType'].astext).label('requestType')
        firstname = case([
                            (FOIRawRequest.status == StateName.unopened.value,
                             FOIRawRequest.requestrawdata['contactInfo']['firstName'].astext),
                           ],
                           else_ = FOIRawRequest.requestrawdata['firstName'].astext).label('firstName')
        lastname = case([
                            (FOIRawRequest.status == StateName.unopened.value,
                             FOIRawRequest.requestrawdata['contactInfo']['lastName'].astext),
                           ],
                           else_ = FOIRawRequest.requestrawdata['lastName'].astext).label('lastName')
        description = case([
                            (FOIRawRequest.status == StateName.unopened.value,
                             FOIRawRequest.requestrawdata['descriptionTimeframe']['description'].astext),
                           ],
                           else_ = FOIRawRequest.requestrawdata['description'].astext).label('description')
        recordsearchfromdate = case([
                            (FOIRawRequest.status == StateName.unopened.value,
                             FOIRawRequest.requestrawdata['descriptionTimeframe']['fromDate'].astext),
                           ],
                           else_ = FOIRawRequest.requestrawdata['fromDate'].astext).label('recordsearchfromdate')
        recordsearchtodate = case([
                            (FOIRawRequest.status == StateName.unopened.value,
                             FOIRawRequest.requestrawdata['descriptionTimeframe']['toDate'].astext),
                           ],
                           else_ = FOIRawRequest.requestrawdata['toDate'].astext).label('recordsearchtodate')
        duedate = case([
                            (FOIRawRequest.status == StateName.unopened.value,
                             literal(None)),
                           ],
                           else_ = FOIRawRequest.requestrawdata['dueDate'].astext).label('duedate')
        receiveddate = case([
                            (and_(FOIRawRequest.status == StateName.unopened.value, FOIRawRequest.requestrawdata['receivedDate'].is_(None)),
                             func.to_char(FOIRawRequest.created_at, 'YYYY-mm-DD')),
                           ],
                           else_ = FOIRawRequest.requestrawdata['receivedDate'].astext).label('receivedDate')
        receiveddateuf = case([
                            (and_(FOIRawRequest.status == StateName.unopened.value, FOIRawRequest.requestrawdata['receivedDateUF'].is_(None)),
                             func.to_char(FOIRawRequest.created_at, 'YYYY-mm-DD HH:MM:SS')),
                           ],
                           else_ = FOIRawRequest.requestrawdata['receivedDateUF'].astext).label('receivedDateUF')

        assignedtoformatted = case([
                            (and_(FOIAssignee.lastname.isnot(None), FOIAssignee.firstname.isnot(None)),
                             func.concat(FOIAssignee.lastname, ', ', FOIAssignee.firstname)),
                            (and_(FOIAssignee.lastname.isnot(None), FOIAssignee.firstname.is_(None)),
                             FOIAssignee.lastname),
                            (and_(FOIAssignee.lastname.is_(None), FOIAssignee.firstname.isnot(None)),
                             FOIAssignee.firstname),
                            (and_(FOIAssignee.lastname.is_(None), FOIAssignee.firstname.is_(None), FOIRawRequest.assignedgroup.is_(None)),
                             'Unassigned'),
                           ],
                           else_ = FOIRawRequest.assignedgroup).label('assignedToFormatted')

        axisrequestid = case([
            (FOIRawRequest.axisrequestid.is_(None),
            'U-00' + cast(FOIRawRequest.requestid, String)),
            ],
            else_ = cast(FOIRawRequest.axisrequestid, String)).label('axisRequestId')

        requestpagecount = case([
            (FOIRawRequest.requestrawdata['axispagecount'].is_(None),
            '0'),
            ],
            else_ = cast(FOIRawRequest.requestrawdata['axispagecount'], String))

        intakesorting = case([
                            (FOIRawRequest.assignedto == None, # Unassigned requests first
                             literal(None)),
                           ],
                           else_ = cast(FOIRawRequest.requestrawdata['receivedDateUF'].astext, TIMESTAMP)).label('intakeSorting')

        isiaorestricted = case([
                            (FOIRawRequest.isiaorestricted.is_(None),
                             False),
                           ],
                           else_ = FOIRawRequest.isiaorestricted).label('isiaorestricted')

        subjectcode = case([
            (FOIRawRequest.requestrawdata['subjectCode'].is_(None),
            literal(None)),
            ],
            else_ = cast(FOIRawRequest.requestrawdata['subjectCode'], String)).label('subjectcode')

        selectedcolumns = [
            FOIRawRequest.requestid.label('id'),
            FOIRawRequest.version,
            FOIRawRequest.sourceofsubmission,
            firstname,
            lastname,
            requesttype,
            receiveddate,
            receiveddateuf,
            FOIRawRequest.status.label('currentState'),
            FOIRawRequest.assignedgroup.label('assignedGroup'),
            FOIRawRequest.assignedto.label('assignedTo'),
            cast(FOIRawRequest.requestid, String).label('idNumber'),
            axisrequestid,
            cast(requestpagecount, Integer).label('requestpagecount'),
            requestpagecount.label('axispagecount'),
            literal(None).label('axislanpagecount'),
            literal(None).label('recordspagecount'),
            literal(None).label('ministryrequestid'),
            literal(None).label('assignedministrygroup'),
            literal(None).label('assignedministryperson'),
            literal(None).label('cfrduedate'),
            duedate,
            FOIRawRequest.requestrawdata['category'].astext.label('applicantcategory'),
            FOIRawRequest.created_at.label('created_at'),
            literal(None).label('bcgovcode'),
            FOIAssignee.firstname.label('assignedToFirstName'),
            FOIAssignee.lastname.label('assignedToLastName'),
            literal(None).label('assignedministrypersonFirstName'),
            literal(None).label('assignedministrypersonLastName'),
            description,
            recordsearchfromdate,
            recordsearchtodate,
            literal(None).label('onBehalfFirstName'),
            literal(None).label('onBehalfLastName'),
            literal(None).label('defaultSorting'),
            intakesorting,
            literal(None).label('ministrySorting'),
            assignedtoformatted,
            literal(None).label('ministryAssignedToFormatted'),
            literal(None).label('closedate'),
            literal(None).label('onBehalfFormatted'),
            literal(None).label('extensions'),
            isiaorestricted,
            literal(None).label('isministryrestricted'),
            subjectcode,
            literal(None).label('isoipcreview'),
            literal(None).label('oipc_number')
        ]

        basequery = _session.query(*selectedcolumns).join(subquery_maxversion, and_(*joincondition)).join(FOIAssignee, FOIAssignee.username == FOIRawRequest.assignedto, isouter=True)

        return FOIRawRequest.handleadditionalfilter(basequery, additionalfilter, userid, isiaorestrictedfilemanager, groups)
    
    @classmethod
    def handleadditionalfilter(cls, basequery, additionalfilter=None, userid=None, isiaorestrictedfilemanager=False, groups=[]):
        if additionalfilter:
            return FOIRawRequest.addadditionalfilter(basequery, additionalfilter, userid, isiaorestrictedfilemanager, groups)
        return FOIRawRequest.noadditionalfilter(basequery, userid, isiaorestrictedfilemanager)
        
    @classmethod
    def noadditionalfilter(cls, basequery, userid=None, isiaorestrictedfilemanager=False):
        if(isiaorestrictedfilemanager == True):
            return basequery.filter(FOIRawRequest.status.notin_(['Archived']))
        else:
            subquery_watchby = FOIRawRequestWatcher.getrequestidsbyuserid(userid)

            return basequery.join(
                                subquery_watchby,
                                subquery_watchby.c.requestid == FOIRawRequest.requestid,
                                isouter=True
                            ).filter(
                                and_(
                                    FOIRawRequest.status.notin_(['Archived']),
                                    or_(
                                        FOIRawRequest.isiaorestricted == False,
                                        and_(FOIRawRequest.isiaorestricted == True, FOIRawRequest.assignedto == userid),
                                        and_(FOIRawRequest.isiaorestricted == True, subquery_watchby.c.watchedby == userid))))
    
    @classmethod    
    def addadditionalfilter(cls, basequery, additionalfilter=None, userid=None, isiaorestrictedfilemanager=False, groups=[]):
        isprocessingteam = False
        
        if groups:
            isprocessingteam = any(item in ProcessingTeamWithKeycloackGroup.list() for item in groups)

        if(additionalfilter == 'watchingRequests' and userid is not None):
            #watchby
            subquery_watchby = FOIRawRequestWatcher.getrequestidsbyuserid(userid)
            return basequery.join(subquery_watchby, subquery_watchby.c.requestid == FOIRawRequest.requestid).filter(FOIRawRequest.status.notin_(['Archived']))
        elif(additionalfilter == 'myRequests'):
            #myrequest
            return basequery.filter(and_(FOIRawRequest.status.notin_(['Archived']), FOIRawRequest.assignedto == userid))
        elif(additionalfilter == 'unassignedRequests'):
            return basequery.filter(and_(FOIRawRequest.status.notin_(['Archived']), FOIRawRequest.assignedto == None, FOIRawRequest.assignedgroup.in_(tuple(groups))))
        elif (additionalfilter.lower() == 'all'):
            if(isiaorestrictedfilemanager == True):
                basequery = basequery.filter(FOIRawRequest.status.notin_(['Archived']))
            else:
                if isprocessingteam:
                    basequery = basequery.filter(
                        and_(
                            FOIRawRequest.status.notin_(['Archived']),
                            or_(and_(FOIRawRequest.isiaorestricted == False, FOIRawRequest.assignedgroup.in_(ProcessingTeamWithKeycloackGroup.list()), FOIRawRequest.assignedgroup.in_(tuple(groups))), and_(FOIRawRequest.isiaorestricted == True, FOIRawRequest.assignedto == userid))))
                basequery = basequery.filter(
                    and_(
                        FOIRawRequest.status.notin_(['Archived']),
                        or_(and_(FOIRawRequest.isiaorestricted == False, FOIRawRequest.assignedgroup == "Intake Team"), and_(FOIRawRequest.isiaorestricted == True, FOIRawRequest.assignedto == userid))))
            return basequery.filter(FOIRawRequest.assignedto != None)
        else:
            if(isiaorestrictedfilemanager == True):
                return basequery.filter(FOIRawRequest.status.notin_(['Archived']))
            else:
                return basequery.filter(
                    and_(
                        FOIRawRequest.status.notin_(['Archived']),
                        or_(FOIRawRequest.isiaorestricted == False, and_(FOIRawRequest.isiaorestricted == True, FOIRawRequest.assignedto == userid))))

    @classmethod
    def getrequestssubquery(cls, filterfields, keyword, additionalfilter, userid, isiaorestrictedfilemanager, groups):
        basequery = FOIRawRequest.getbasequery(additionalfilter, userid, isiaorestrictedfilemanager, groups)
        basequery = basequery.filter(FOIRawRequest.status != 'Unopened').filter(FOIRawRequest.status != 'Closed')
        #filter/search
        if(len(filterfields) > 0 and keyword is not None):
            filtercondition = FOIRawRequest.getfilterforrequestssubquery(filterfields, keyword)
            return basequery.filter(filtercondition)
        else:
            return basequery

    @classmethod
    def getfilterforrequestssubquery(cls, filterfields, keyword):
        _keywords = []
        if(keyword is not None):
            _keywords = keyword.lower().replace(",", " ").split()

        #filter/search
        filtercondition = []
        for _keyword in _keywords:
            if(_keyword != 'restricted'):
                for field in filterfields:
                    if(field == 'idNumber'):
                        _keyword = _keyword.replace('u-00', '')
                    
                    filtercondition.append(FOIRawRequest.findfield(field).ilike('%'+_keyword+'%'))
                    if(field == 'firstName'):
                        filtercondition.append(FOIRawRequest.findfield('contactFirstName').ilike('%'+_keyword+'%'))
                    if(field == 'lastName'):
                        filtercondition.append(FOIRawRequest.findfield('contactLastName').ilike('%'+_keyword+'%'))
                    if(field == 'requestType'):
                        filtercondition.append(FOIRawRequest.findfield('requestTypeRequestType').ilike('%'+_keyword+'%'))
            else:
                filtercondition.append(FOIRawRequest.isiaorestricted == True)

        return or_(*filtercondition)


    @classmethod
    def getrequestspagination(cls, groups, page, size, sortingitems, sortingorders, filterfields, keyword, additionalfilter, userid, isiaorestrictedfilemanager, usertype, isministryrestrictedfilemanager=False):
        #ministry requests
        iaoassignee = aliased(FOIAssignee)
        ministryassignee = aliased(FOIAssignee)
        subquery_ministry_queue = FOIMinistryRequest.getrequestssubquery(groups, filterfields, keyword, additionalfilter, userid, iaoassignee, ministryassignee, 'IAO', isiaorestrictedfilemanager, isministryrestrictedfilemanager)

        #sorting
        sortingcondition = FOIRawRequest.getsorting(sortingitems, sortingorders)
        #rawrequests
        if usertype == "iao" or groups is None:
            subquery_rawrequest_queue = FOIRawRequest.getrequestssubquery(filterfields, keyword, additionalfilter, userid, isiaorestrictedfilemanager, groups)
            query_full_queue = subquery_rawrequest_queue.union(subquery_ministry_queue)
            return query_full_queue.order_by(*sortingcondition).paginate(page=page, per_page=size)
        else:
            return subquery_ministry_queue.order_by(*sortingcondition).paginate(page=page, per_page=size)

    @classmethod
    def findfield(cls, x):
        return {
            'firstName': FOIRawRequest.requestrawdata['firstName'].astext,
            'lastName': FOIRawRequest.requestrawdata['lastName'].astext,
            'contactFirstName': FOIRawRequest.requestrawdata['contactInfo']['firstName'].astext,
            'contactLastName': FOIRawRequest.requestrawdata['contactInfo']['lastName'].astext,
            'requestType': FOIRawRequest.requestrawdata['requestType'].astext,
            'requestTypeRequestType': FOIRawRequest.requestrawdata['requestType']['requestType'].astext,
            'idNumber': cast(FOIRawRequest.requestid, String),
            'axisRequestId': cast(FOIRawRequest.axisrequestid, String),
            'axisrequest_number': cast(FOIRawRequest.axisrequestid, String),
            'currentState': FOIRawRequest.status,
            'assignedTo': FOIRawRequest.assignedto,
            'assignedToFirstName': FOIAssignee.firstname,
            'assignedToLastName': FOIAssignee.lastname,
            'receivedDate': FOIRawRequest.requestrawdata['receivedDate'].astext,
            'description': FOIRawRequest.requestrawdata['description'].astext,
            'descriptionDescription': FOIRawRequest.requestrawdata['descriptionTimeframe']['description'].astext,
            'ministry': FOIRawRequest.requestrawdata['selectedMinistries'].astext,
            'ministryMinistry': FOIRawRequest.requestrawdata['ministry']['selectedMinistry'].astext,
            'duedate': FOIRawRequest.requestrawdata['dueDate'].astext,
            'DueDateValue': FOIRawRequest.requestrawdata['dueDate'].astext,
            'DaysLeftValue': FOIRawRequest.requestrawdata['dueDate'].astext,
            'subjectcode': FOIRawRequest.requestrawdata['subjectCode'].astext
        }.get(x, cast(FOIRawRequest.requestid, String))
    
    @classmethod
    def validatefield(cls, x):
        validfields = [
            'firstName',
            'lastName',
            'requestType',
            'idNumber',
            'axisRequestId',
            'requestpagecount',
            'currentState',
            'assignedTo',
            'receivedDate',
            'receivedDateUF',
            'assignedToFirstName',
            'assignedToLastName',
            'duedate',
            'defaultSorting',
            'intakeSorting',
            'ministrySorting',
            'assignedToFormatted',
            'ministryAssignedToFormatted',
            'cfrduedate',
            'applicantcategory',
            'onBehalfFormatted',
            'extensions',
            'isiaorestricted'
        ]
        if x in validfields:
            return True
        else:
            return False

    @classmethod
    def getsorting(cls, sortingitems, sortingorders):
        sortingcondition = []
        if(len(sortingitems) > 0 and len(sortingorders) > 0 and len(sortingitems) == len(sortingorders)):
            for field in sortingitems:
                if(FOIRawRequest.validatefield(field)):
                    order = sortingorders.pop(0)
                    if(order == 'desc'):
                        sortingcondition.append(nullslast(desc(field)))
                    else:
                        sortingcondition.append(nullsfirst(asc(field)))
        #default sorting
        if(len(sortingcondition) == 0):
            sortingcondition.append(asc('currentState'))

        #always sort by created_at last to prevent pagination collisions
        sortingcondition.append(asc('created_at'))
        
        return sortingcondition


    @classmethod
    def advancedsearch(cls, params, userid, isiaorestrictedfilemanager=False):
        basequery = FOIRawRequest.getbasequery(None, userid, isiaorestrictedfilemanager)

        #filter/search
        filtercondition = FOIRawRequest.getfilterforadvancedsearch(params)
        searchquery = basequery.filter(and_(*filtercondition))

        #ministry requests
        iaoassignee = aliased(FOIAssignee)
        ministryassignee = aliased(FOIAssignee)
        subquery_ministry_queue = FOIMinistryRequest.advancedsearchsubquery(params, iaoassignee, ministryassignee, userid, 'IAO', isiaorestrictedfilemanager)

        #sorting
        sortingcondition = FOIRawRequest.getsorting(params['sortingitems'], params['sortingorders'])

        #rawrequests
        query_full_queue = searchquery.union(subquery_ministry_queue)
        return query_full_queue.order_by(*sortingcondition).paginate(page=params['page'], per_page=params['size'])

    @classmethod
    def getfilterforadvancedsearch(cls, params):

        #filter/search
        filtercondition = []
        includeclosed = False

        #request state: unopened, call for records, etc.
        if(len(params['requeststate']) > 0):
            requeststatecondition = FOIRawRequest.getfilterforrequeststate(params, includeclosed)
            filtercondition.append(requeststatecondition['condition'])
            includeclosed = requeststatecondition['includeclosed']
        else:
            filtercondition.append(FOIRawRequest.status != StateName.unopened.value)  #not return Unopened by default
        
        #request status: overdue, on time - no due date for unopen & intake in progress, so return all except closed
        if(len(params['requeststatus']) > 0 and includeclosed == False):
            if(len(params['requeststatus']) == 1 and params['requeststatus'][0] == 'overdue'):
                #no rawrequest returned for this case
                filtercondition.append(FOIRawRequest.status == 'ReturnNothing')
            else:
                filtercondition.append(FOIRawRequest.status != StateName.closed.value)
        
        #request type: personal, general
        if(len(params['requesttype']) > 0):
            requesttypecondition = FOIRawRequest.getfilterforrequesttype(params)
            filtercondition.append(or_(*requesttypecondition))

        #request flags: restricted, oipc, phased
        if(len(params['requestflags']) > 0):
            requestflagscondition = FOIRawRequest.getfilterforrequestflags(params)
            filtercondition.append(or_(*requestflagscondition))
        
        #public body: EDUC, etc.
        if(len(params['publicbody']) > 0):
            ministrycondition = FOIRawRequest.getfilterforpublicbody(params)
            filtercondition.append(ministrycondition)

        #axis request #, raw request #, applicant name, assignee name, request description, subject code
        if(len(params['keywords']) > 0 and params['search'] is not None):
            searchcondition = FOIRawRequest.getfilterforsearch(params)
            filtercondition.append(searchcondition)

        if(params['daterangetype'] is not None):
            filterconditionfordate = FOIRawRequest.getfilterfordate(params)
            filtercondition += filterconditionfordate

        return filtercondition

    @classmethod
    def getfilterfordate(cls, params):
        filterconditionfordate = []
        if(params['daterangetype'] == 'closedate'):
            #no rawrequest returned for this case
            filterconditionfordate.append(FOIRawRequest.requestid < 0)
        else:
            if(params['fromdate'] is not None):
                if(params['daterangetype'] == 'receivedDate'):
                    #online form submission has no receivedDate in json - using created_at
                    filterconditionfordate.append(
                        or_(
                            and_(FOIRawRequest.requestrawdata['receivedDate'].is_(None), FOIRawRequest.created_at.cast(Date) >= parser.parse(params['fromdate'])),
                            and_(FOIRawRequest.requestrawdata['receivedDate'].isnot(None), FOIRawRequest.findfield(params['daterangetype']).cast(Date) >= parser.parse(params['fromdate'])),
                        )
                    )
                else:
                    filterconditionfordate.append(FOIRawRequest.findfield(params['daterangetype']).cast(Date) >= parser.parse(params['fromdate']))

            if(params['todate'] is not None):
                if(params['daterangetype'] == 'receivedDate'):
                    #online form submission has no receivedDate in json - using created_at
                    filterconditionfordate.append(
                        or_(
                            and_(FOIRawRequest.requestrawdata['receivedDate'].is_(None), FOIRawRequest.created_at.cast(Date) <= parser.parse(params['todate'])),
                            and_(FOIRawRequest.requestrawdata['receivedDate'].isnot(None), FOIRawRequest.findfield(params['daterangetype']).cast(Date) <= parser.parse(params['todate'])),
                        )
                    )
                else:
                    filterconditionfordate.append(FOIRawRequest.findfield(params['daterangetype']).cast(Date) <= parser.parse(params['todate']))

        return filterconditionfordate

    @classmethod
    def getfilterforrequeststate(cls, params, includeclosed):
        #request state: unopened, call for records, etc.
        requeststatecondition = []
        for state in params['requeststate']:
            if(state == StateName.closed.name):
                requeststatecondition.append(FOIRawRequest.status == StateName.closed.value)
                includeclosed = True
            elif(state == StateName.redirect.name):
                requeststatecondition.append(FOIRawRequest.status == StateName.redirect.value)
            elif(state == StateName.unopened.name):
                requeststatecondition.append(FOIRawRequest.status == StateName.unopened.value)
            elif(state == StateName.intakeinprogress.name):
                requeststatecondition.append(FOIRawRequest.status == StateName.intakeinprogress.value)
        
        if(len(requeststatecondition) == 0):
            requeststatecondition.append(FOIRawRequest.status == 'Not Applicable')  #searched state does not apply to rawrequests

        return {'condition': or_(*requeststatecondition), 'includeclosed': includeclosed}
    
    @classmethod
    def getfilterforrequesttype(cls, params):
        #request type: personal, general
        requesttypecondition = []
        for type in params['requesttype']:
            requesttypecondition.append(FOIRawRequest.findfield('requestType') == type)
            requesttypecondition.append(FOIRawRequest.findfield('requestTypeRequestType') == type)

        return or_(*requesttypecondition)

    @classmethod
    def getfilterforrequestflags(cls, params):
        # this search will be done by the ministry union, so returns filter with no results
        requestflagscondition = []
        for flag in params['requestflags']:
            if (flag.lower() == 'restricted'): # no results for raw restricted
                requestflagscondition.append(FOIRawRequest.findfield('axisRequestId') == 'thisismeanttoreturnafilterconditionwith0results')
            if (flag.lower() == 'oipc'): # no results for raw oipc
                requestflagscondition.append(FOIRawRequest.findfield('axisRequestId') == 'thisismeanttoreturnafilterconditionwith0results')
            if (flag.lower() == 'phased'):
                # requestflagscondition.append(FOIMinistryRequest.findfield('isphasedrelease', iaoassignee, ministryassignee) == True)
                continue
        return requestflagscondition

    @classmethod
    def getfilterforpublicbody(cls, params):
        #public body: EDUC, etc.
        ministrycondition = []
        for ministry in params['publicbody']:
            ministrycondition.append(FOIRawRequest.findfield('ministry').ilike('%"'+ministry+'"%'))
            ministrycondition.append(FOIRawRequest.findfield('ministryMinistry').ilike('%"'+ministry+'"%'))
        
        return or_(*ministrycondition)

    @classmethod
    def getfilterforsearch(cls, params):
        #axis request #, raw request #, applicant name, assignee name, request description, subject code
        if(params['search'] == 'requestdescription'):
            return FOIRawRequest.__getfilterfordescription(params)
        elif(params['search'] == 'applicantname'):
            return FOIRawRequest.__getfilterforapplicantname(params)
        elif(params['search'] == 'assigneename'):
            return FOIRawRequest.__getfilterforassigneename(params)
        elif(params['search'] == 'idnumber'):
            return FOIRawRequest.__getfilterforidnumber(params)
        elif(params['search'] == 'axisrequest_number'):
            return FOIRawRequest.__getfilterforaxisnumber(params)
        else:
            searchcondition = []
            for keyword in params['keywords']:
                searchcondition.append(FOIRawRequest.findfield(params['search']).ilike('%'+keyword+'%'))
            return and_(*searchcondition)
    
    @classmethod
    def __getfilterfordescription(cls,params):
        searchcondition1 = []
        searchcondition2 = []
        for keyword in params['keywords']:
            searchcondition1.append(FOIRawRequest.findfield('description').ilike('%'+keyword+'%'))
            searchcondition2.append(FOIRawRequest.findfield('descriptionDescription').ilike('%'+keyword+'%'))
        return or_(and_(*searchcondition1), and_(*searchcondition2))    
    
    @classmethod
    def __getfilterforapplicantname(cls,params):
        searchcondition1 = []
        searchcondition2 = []
        searchcondition3 = []
        searchcondition4 = []
        for keyword in params['keywords']:
            searchcondition1.append(FOIRawRequest.findfield('firstName').ilike('%'+keyword+'%'))
            searchcondition2.append(FOIRawRequest.findfield('lastName').ilike('%'+keyword+'%'))
            searchcondition3.append(FOIRawRequest.findfield('contactFirstName').ilike('%'+keyword+'%'))
            searchcondition4.append(FOIRawRequest.findfield('contactLastName').ilike('%'+keyword+'%'))
        return or_(and_(*searchcondition1), and_(*searchcondition2), and_(*searchcondition3), and_(*searchcondition4))
    
    @classmethod        
    def __getfilterforassigneename(cls,params):
        searchcondition1 = []
        searchcondition2 = []
        searchcondition3 = []
        for keyword in params['keywords']:
            searchcondition1.append(FOIRawRequest.findfield('assignedToFirstName').ilike('%'+keyword+'%'))
            searchcondition2.append(FOIRawRequest.findfield('assignedToLastName').ilike('%'+keyword+'%'))
            searchcondition3.append(FOIRawRequest.assignedgroup.ilike('%'+keyword+'%'))
        return or_(and_(*searchcondition1), and_(*searchcondition2), and_(*searchcondition3))

    @classmethod
    def __getfilterforidnumber(cls,params):
        searchcondition = []
        for keyword in params['keywords']:
            keyword = keyword.lower()
            keyword = keyword.replace('u-00', '')
            searchcondition.append(FOIRawRequest.findfield('idNumber').ilike('%'+keyword+'%'))
        return and_(*searchcondition)
    
    @classmethod
    def __getfilterforaxisnumber(cls,params):
        searchcondition1 = []
        searchcondition2 = []
        for keyword in params['keywords']:
            keyword = keyword.lower()
            keyword = keyword.replace('u-00', '')
            searchcondition1.append(FOIRawRequest.findfield('idNumber').ilike('%'+keyword+'%'))
            searchcondition2.append(FOIRawRequest.findfield('axisrequest_number').ilike('%'+keyword+'%'))
        return or_(and_(*searchcondition1), and_(*searchcondition2))
    
    
    @classmethod
    def getDistinctAXISRequestIds(cls):
        axisrequestids = []
        try:
            sql = """select distinct axisrequestid from "FOIRawRequests" where axisrequestid is not null;"""
            axisids = db.session.execute(text(sql))
            for axisid in axisids:
                axisrequestids.append(axisid[0])
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return axisrequestids

    @classmethod
    def getCountOfAXISRequestIdbyAXISRequestId(cls, axisrequestid):       
        try:
            query  = db.session.query(func.count(FOIRawRequest.axisrequestid)).filter_by(axisrequestid=axisrequestid)
            return query.scalar()
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()        

    @classmethod
    def getmetadata(cls,requestid):
        requestdetails = {}
        try:
            sql = """select requestrawdata ->> 'assignedTo' as assignedTo,
            requestrawdata ->> 'assignedToFirstName' as assignedToFirstName,
            requestrawdata ->> 'assignedToLastName' as assignedToLastName,
            requestrawdata -> 'selectedMinistries'-> 0 ->> 'code' as bcgovcode from "FOIRawRequests" 
                    where requestid = :requestid
                    order by version desc limit 1;"""
            rs = db.session.execute(text(sql), {'requestid': requestid})
            for row in rs:
                requestdetails["assignedTo"] = row['assignedto']
                requestdetails["assignedToFirstName"] = row["assignedtofirstname"]
                requestdetails["assignedToLastName"] = row["assignedtolastname"]
                requestdetails["bcgovcode"] = row["bcgovcode"]
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return requestdetails
    
    @classmethod
    def getlatestsection5pendings(cls):
        section5pendings = []
        try:
            sql = """SELECT * FROM 
                (SELECT DISTINCT ON (requestid) requestid, created_at, version, status, axisrequestid
                FROM public."FOIRawRequests"
                ORDER BY requestid ASC, version DESC) foireqs
            WHERE foireqs.status = :requeststatus;"""
            rs = db.session.execute(text(sql), {'requeststatus': StateName.section5pending.value})
            for row in rs:
                section5pendings.append({"requestid": row["requestid"], "version": row["version"], "statusname": row["status"], "created_at": row["created_at"], "axisrequestid": ["axisrequestid"]})
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return section5pendings
    
    @classmethod
    def getunopenedunactionedrequests(cls, startdate, enddate):
        try:
            requests = []
            sql = '''select rr.created_at, rr.requestrawdata, rr.requestid, coalesce(p.status, '') as status,
                         coalesce(p.transaction_number, '') as txnno,
                         coalesce(p.total::text, '') as fee
                    from public."FOIRawRequests" rr
                    join (
                        select max(version) as version, requestid from public."FOIRawRequests"
                        group by requestid
                    ) mv on mv.requestid = rr.requestid and mv.version = rr.version
                    left join (
                        select request_id, max(payment_id) from public."Payments"
                        where fee_code_id = 1
                        group by request_id
                        order by request_id
                    ) mp on mp.request_id = rr.requestid
                    left join public."Payments" p on p.payment_id = mp.max
                    where rr.status = 'Unopened' and rr.version = 1 and created_at > :startdate and created_at < :enddate
                    order by rr.requestid '''
            rs = db.session.execute(text(sql), {'startdate': startdate, 'enddate': enddate})
            for row in rs:
                requests.append({
                    "requestid": row["requestid"],
                    "created_at": row["created_at"],
                    "requestrawdata": row["requestrawdata"],
                    "paymentstatus": row["status"],
                    "fee": row["fee"],
                    "txnno": row["txnno"]
                })
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return requests
    
    @classmethod
    def getpotentialactionedmatches(cls, request):
        try:
            requests = []
            sql = '''select rr.created_at, rr.* from public."FOIRawRequests" rr
                    join (
                        select max(version) as version, requestid from public."FOIRawRequests"
                        group by requestid
                    ) mv on mv.requestid = rr.requestid and mv.version = rr.version
                    where (
                        requestrawdata->>'lastName' ilike :lastName
                        or requestrawdata->>'firstName' ilike :firstName
                        or requestrawdata->>'email' ilike :email
                        or requestrawdata->>'address' ilike :address
                        or requestrawdata->>'phonePrimary' ilike :phonePrimary
                        or requestrawdata->>'postal' ilike :postal
                    ) and substring(rr.requestrawdata->>'receivedDateUF', 1, 10) = :receiveddate
                    order by requestid desc, version desc '''
            rs = db.session.execute(text(sql), {
                'lastName': request['requestrawdata']['contactInfo']['lastName'],
                'firstName': request['requestrawdata']['contactInfo']['firstName'],
                'email': request['requestrawdata']['contactInfoOptions']['email'],
                'address': request['requestrawdata']['contactInfoOptions']['address'],
                'phonePrimary': request['requestrawdata']['contactInfoOptions']['phonePrimary'],
                'postal': request['requestrawdata']['contactInfoOptions']['postal'],
                'receiveddate': request['requestrawdata']['receivedDateUF'][0:10],
            })
            for row in rs:
                requests.append({"requestid": row["requestid"], "created_at": row["created_at"], "requestrawdata": row["requestrawdata"]})
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return requests



class FOIRawRequestSchema(ma.Schema):
    class Meta:
        fields = ('requestid', 'requestrawdata', 'status', 'requeststatuslabel', 'notes','created_at','wfinstanceid','version','updated_at','assignedgroup','assignedto','updatedby','createdby','sourceofsubmission','ispiiredacted','assignee.firstname','assignee.lastname', 'axisrequestid', 'axissyncdate', 'linkedrequests', 'closedate','isiaorestricted')
