from enum import unique

from sqlalchemy.sql.sqltypes import DateTime, String

from flask.app import Flask
from sqlalchemy.sql.schema import ForeignKey, ForeignKeyConstraint
from sqlalchemy.sql.expression import distinct
from .db import  db, ma
from sqlalchemy.dialects.postgresql import JSON, UUID
from .default_method_result import DefaultMethodResult
from datetime import datetime
from sqlalchemy.orm import relationship, backref, aliased
from sqlalchemy import insert, and_, or_, text, func, literal, cast, asc, desc, case

from .FOIMinistryRequests import FOIMinistryRequest
from .FOIRawRequestWatchers import FOIRawRequestWatcher
from .FOIAssignees import FOIAssignee

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
    assignedto = db.Column(db.String(120), ForeignKey('FOIAssignees.username'), unique=False, nullable=True)    
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=True)
    createdby = db.Column(db.String(120), unique=False, nullable=True)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)
    sourceofsubmission = db.Column(db.String(120),  nullable=True)
    ispiiredacted = db.Column(db.Boolean, unique=False, nullable=False,default=False)    
    closedate = db.Column(db.DateTime, nullable=True)    
    requirespayment = db.Column(db.Boolean, unique=False, nullable=True, default=False)
    
    closereasonid = db.Column(db.Integer,ForeignKey('CloseReasons.closereasonid'))
    closereason = relationship("CloseReason", uselist=False)

    assignee = relationship('FOIAssignee', foreign_keys="[FOIRawRequest.assignedto]")

    @classmethod
    def saverawrequest(cls, _requestrawdata, sourceofsubmission, ispiiredacted, userid, notes, requirespayment, assigneegroup=None, assignee=None, assigneefirstname=None, assigneemiddlename=None, assigneelastname=None)->DefaultMethodResult:
        createdat = datetime.now()        
        version = 1
        newrawrequest = FOIRawRequest(requestrawdata=_requestrawdata, status='Unopened' if sourceofsubmission != "intake" else 'Intake in Progress',created_at=createdat,createdby=userid,version=version,sourceofsubmission=sourceofsubmission,assignedgroup=assigneegroup,assignedto=assignee,ispiiredacted=ispiiredacted,notes=notes, requirespayment=requirespayment)

        if assignee is not None:
            FOIAssignee.saveassignee(assignee, assigneefirstname, assigneemiddlename, assigneelastname)

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
    def saverawrequestversion(cls,_requestrawdata,requestid,assigneegroup,assignee,status,ispiiredacted,userid,assigneefirstname=None,assigneemiddlename=None,assigneelastname=None)->DefaultMethodResult:        
        request = db.session.query(FOIRawRequest).filter_by(requestid=requestid).order_by(FOIRawRequest.version.desc()).first()
        if request is not None:
            if assignee is not None:
                FOIAssignee.saveassignee(assignee, assigneefirstname, assigneemiddlename, assigneelastname)

            closedate = _requestrawdata["closedate"] if 'closedate' in _requestrawdata  else None
            closereasonid = _requestrawdata["closereasonid"] if 'closereasonid' in _requestrawdata  else None                
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
                    assignedgroup=assigneegroup,
                    assignedto=assignee,
                    wfinstanceid=request.wfinstanceid,
                    sourceofsubmission=request.sourceofsubmission,
                    ispiiredacted=ispiiredacted,
                    createdby=userid,
                    closedate=closedate,
                    closereasonid=closereasonid,
                )
            )
            db.session.execute(insertstmt)               
            db.session.commit()                
            return DefaultMethodResult(True,'Request versioned - {0}'.format(str(_version)),requestid,request.wfinstanceid,assignee)    
        else:
            return DefaultMethodResult(True,'No request foound')
            
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
    def updateworkflowinstancewithstatus(cls,wfinstanceid,requestid,status,notes,userid)-> DefaultMethodResult:
        updatedat = datetime.now()
        dbquery = db.session.query(FOIRawRequest)
        _requestraqw = dbquery.filter_by(requestid=requestid).order_by(FOIRawRequest.version.desc()).first()
        requestraqw = dbquery.filter_by(requestid=requestid,version = _requestraqw.version)        
        if(requestraqw.count() > 0) :            
            request_schema = FOIRawRequestSchema()
            request = request_schema.dump(_requestraqw)            
            if(request is not None and (request["status"] == "Redirect" or request["status"] == "Closed")):
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
    
    @classmethod
    def getLastStatusUpdateDate(cls,requestid,status):
        sql = """select created_at from "FOIRawRequests" 
                    where requestid = :requestid and status = :status
                    order by version desc limit 1;"""
        rs = db.session.execute(text(sql), {'requestid': requestid, 'status': status})
        return [row[0] for row in rs][0]

    @classmethod
    def getassignmenttransition(cls,requestid):
        sql = """select version, assignedto, status from "FOIRawRequests" 
                    where requestid = :requestid
                    order by version desc limit 2;"""
        rs = db.session.execute(text(sql), {'requestid': requestid})
        assignments = []
        for row in rs:
            assignments.append({"assignedto": row["assignedto"], "status": row["status"], "version": row["version"]})
        return assignments
    
    @classmethod
    def getversionforrequest(cls,requestid):   
        return db.session.query(FOIRawRequest.version).filter_by(requestid=requestid).order_by(FOIRawRequest.version.desc()).first()
    
    @classmethod
    def getstatesummary(cls, requestid):                
        sql = """select status, version from (select distinct on (status) status, version from "FOIRawRequests" 
        where requestid=:requestid order by status, version asc) as fs3 order by version desc"""
        rs = db.session.execute(text(sql), {'requestid': requestid})
        transitions = []
        for row in rs:
            transitions.append({"status": row["status"], "version": row["version"]})
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
    def getbasequery(cls, additionalfilter=None, userid=None):
        _session = db.session

        #rawrequests
        #subquery for getting the latest version
        subquery_maxversion = _session.query(FOIRawRequest.requestid, func.max(FOIRawRequest.version).label('max_version')).group_by(FOIRawRequest.requestid).subquery()
        joincondition = [
            subquery_maxversion.c.requestid == FOIRawRequest.requestid,
            subquery_maxversion.c.max_version == FOIRawRequest.version,
        ]

        requesttype = case([
                            (FOIRawRequest.status == 'Unopened',
                             FOIRawRequest.requestrawdata['requestType']['requestType'].astext),
                           ],
                           else_ = FOIRawRequest.requestrawdata['requestType'].astext).label('requestType')
        firstname = case([
                            (FOIRawRequest.status == 'Unopened',
                             FOIRawRequest.requestrawdata['contactInfo']['firstName'].astext),
                           ],
                           else_ = FOIRawRequest.requestrawdata['firstName'].astext).label('firstName')
        lastname = case([
                            (FOIRawRequest.status == 'Unopened',
                             FOIRawRequest.requestrawdata['contactInfo']['lastName'].astext),
                           ],
                           else_ = FOIRawRequest.requestrawdata['lastName'].astext).label('lastName')
        description = case([
                            (FOIRawRequest.status == 'Unopened',
                             FOIRawRequest.requestrawdata['descriptionTimeframe']['description'].astext),
                           ],
                           else_ = FOIRawRequest.requestrawdata['description'].astext).label('description')

        selectedcolumns = [
            FOIRawRequest.requestid.label('id'),
            FOIRawRequest.version,
            FOIRawRequest.sourceofsubmission,
            firstname,
            lastname,
            requesttype,
            FOIRawRequest.requestrawdata['receivedDate'].astext.label('receivedDate'),
            FOIRawRequest.requestrawdata['receivedDateUF'].astext.label('receivedDateUF'),
            FOIRawRequest.status.label('currentState'),
            FOIRawRequest.assignedgroup.label('assignedGroup'),
            FOIRawRequest.assignedto.label('assignedTo'),
            cast(FOIRawRequest.requestid, String).label('idNumber'),
            literal(None).label('ministryrequestid'),
            literal(None).label('assignedministrygroup'),
            literal(None).label('assignedministryperson'),
            literal(None).label('cfrduedate'),
            literal(None).label('duedate'),
            FOIRawRequest.requestrawdata['category'].astext.label('applicantcategory'),
            FOIRawRequest.created_at.label('created_at'),
            literal(None).label('bcgovcode'),
            FOIAssignee.firstname.label('assignedToFirstName'),
            FOIAssignee.lastname.label('assignedToLastName'),
            literal(None).label('assignedministrypersonFirstName'),
            literal(None).label('assignedministrypersonLastName'),
            description
        ]

        basequery = _session.query(*selectedcolumns).join(subquery_maxversion, and_(*joincondition)).join(FOIAssignee, FOIAssignee.username == FOIRawRequest.assignedto, isouter=True)

        if additionalfilter is None:
            return basequery.filter(FOIRawRequest.status.notin_(['Archived']))
        else:
            if(additionalfilter == 'watchingRequests' and userid is not None):
                #watchby
                subquery_watchby = FOIRawRequestWatcher.getrequestidsbyuserid(userid)
                return basequery.join(subquery_watchby, subquery_watchby.c.requestid == FOIRawRequest.requestid).filter(FOIRawRequest.status.notin_(['Archived']))
            elif(additionalfilter == 'myRequests'):
                #myrequest
                return basequery.filter(and_(FOIRawRequest.status.notin_(['Archived']), FOIRawRequest.assignedto == userid))
            else:
                return basequery.filter(FOIRawRequest.status.notin_(['Archived']))

    @classmethod
    def getrequestssubquery(cls, filterfields, keyword, additionalfilter, userid):
        basequery = FOIRawRequest.getbasequery(additionalfilter, userid)

        #filter/search
        if(len(filterfields) > 0 and keyword is not None):
            filtercondition = []
            for field in filterfields:
                filtercondition.append(FOIRawRequest.findfield(field).ilike('%'+keyword+'%'))
                if(field == 'firstName'):
                    filtercondition.append(FOIRawRequest.findfield('contactFirstName').ilike('%'+keyword+'%'))
                if(field == 'lastName'):
                    filtercondition.append(FOIRawRequest.findfield('contactLastName').ilike('%'+keyword+'%'))
                if(field == 'requestType'):
                    filtercondition.append(FOIRawRequest.findfield('requestTypeRequestType').ilike('%'+keyword+'%'))

            return basequery.filter(or_(*filtercondition))
        else:
            return basequery

    @classmethod
    def getrequestspagination(cls, groups, page, size, sortingitems, sortingorders, filterfields, keyword, additionalfilter, userid):
        #ministry requests
        iaoassignee = aliased(FOIAssignee)
        ministryassignee = aliased(FOIAssignee)
        subquery_ministry_queue = FOIMinistryRequest.getrequestssubquery(groups, filterfields, keyword, additionalfilter, userid, iaoassignee, ministryassignee)

        #sorting
        sortingcondition = FOIRawRequest.getsorting(sortingitems, sortingorders)

        #rawrequests
        if "Intake Team" in groups or groups is None:                
            subquery_rawrequest_queue = FOIRawRequest.getrequestssubquery(filterfields, keyword, additionalfilter, userid)
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
            'currentState': FOIRawRequest.status,
            'assignedTo': FOIRawRequest.assignedto,
            'assignedToFirstName': FOIAssignee.firstname,
            'assignedToLastName': FOIAssignee.lastname,
            'receivedDate': FOIRawRequest.requestrawdata['receivedDate'].astext,
            'description': FOIRawRequest.requestrawdata['description'].astext,
            'descriptionDescription': FOIRawRequest.requestrawdata['descriptionTimeframe']['description'].astext,
            'ministry': FOIRawRequest.requestrawdata['selectedMinistries'].astext,
            'ministryMinistry': FOIRawRequest.requestrawdata['ministry']['selectedMinistry'].astext
        }.get(x, cast(FOIRawRequest.requestid, String))
    
    @classmethod
    def validatefield(cls, x):
        validfields = ['firstName', 'lastName', 'requestType', 'idNumber', 'currentState', 'assignedTo', 'receivedDate', 'assignedToFirstName', 'assignedToLastName']
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
                    order = sortingorders.pop()
                    if(order == 'desc'):
                        sortingcondition.append(desc(field))
                    else:
                        sortingcondition.append(asc(field))
        #default sorting
        if(len(sortingcondition) == 0):
            sortingcondition.append(asc('currentState'))
        
        return sortingcondition


    @classmethod
    def advancedsearch(cls, params):
        basequery = FOIRawRequest.getbasequery()

        #filter/search
        filtercondition = FOIRawRequest.getfilterforadvancedsearch(params)
        searchquery = basequery.filter(and_(*filtercondition))

        #ministry requests
        iaoassignee = aliased(FOIAssignee)
        ministryassignee = aliased(FOIAssignee)
        subquery_ministry_queue = FOIMinistryRequest.advancedsearch(params, iaoassignee, ministryassignee)

        #sorting
        sortingcondition = FOIRawRequest.getsorting(params['sortingitems'], params['sortingorders'])

        #rawrequests
        if "Intake Team" in params['groups'] or params['groups'] is None:                
            query_full_queue = searchquery.union(subquery_ministry_queue)
            return query_full_queue.order_by(*sortingcondition).paginate(page=params['page'], per_page=params['size'])
        else:
            return subquery_ministry_queue.order_by(*sortingcondition).paginate(page=params['page'], per_page=params['size'])

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
        
        #request status: overdue, on time - no due date for unopen & intake in progress, so return all except closed
        if(len(params['requeststatus']) > 0 and includeclosed == False):
            filtercondition.append(FOIRawRequest.status != 'Closed')
        
        #request type: personal, general
        if(len(params['requesttype']) > 0):
            requesttypecondition = FOIRawRequest.getfilterforrequesttype(params)
            filtercondition.append(or_(*requesttypecondition))
        
        #public body: EDUC, etc.
        if(len(params['publicbody']) > 0):
            ministrycondition = FOIRawRequest.getfilterforpublicbody(params)
            filtercondition.append(ministrycondition)

        #axis request #, raw request #, applicant name, assignee name, request description, subject code
        if(len(params['keywords']) > 0 and params['search'] is not None):
            searchcondition = FOIRawRequest.getfilterforsearch(params)
            filtercondition.append(searchcondition)

        if(params['fromdate'] is not None):
            filtercondition.append(FOIRawRequest.findfield('receivedDate') >= params['fromdate'])

        # no duedate for unopened & intake in progress
        
        return filtercondition

    @classmethod
    def getfilterforrequeststate(cls, params, includeclosed):
        #request state: unopened, call for records, etc.
        requeststatecondition = []
        for state in params['requeststate']:
            if(state == 3):
                requeststatecondition.append(FOIRawRequest.status == 'Closed')
                includeclosed = True
            elif(state == 5):
                requeststatecondition.append(FOIRawRequest.status == 'Unopened')
        
        if(len(requeststatecondition) == 0):
            requeststatecondition.append(FOIRawRequest.status == 'Closed')
            requeststatecondition.append(FOIRawRequest.status == 'Unopened')
        
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
            searchcondition1 = []
            searchcondition2 = []
            for keyword in params['keywords']:
                searchcondition1.append(FOIRawRequest.findfield('description').ilike('%'+keyword+'%'))
                searchcondition2.append(FOIRawRequest.findfield('descriptionDescription').ilike('%'+keyword+'%'))
            return or_(and_(*searchcondition1), and_(*searchcondition2))
        else:
            searchcondition = []
            for keyword in params['keywords']:
                searchcondition.append(FOIRawRequest.findfield(params['search']).ilike('%'+keyword+'%'))
            return and_(*searchcondition)

class FOIRawRequestSchema(ma.Schema):
    class Meta:
        fields = ('requestid', 'requestrawdata', 'status','notes','created_at','wfinstanceid','version','updated_at','assignedgroup','assignedto','updatedby','createdby','sourceofsubmission','ispiiredacted','assignee.firstname','assignee.lastname')