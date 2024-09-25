from flask.app import Flask
from sqlalchemy.sql.schema import ForeignKey, ForeignKeyConstraint
from .db import  db, ma
from datetime import datetime
from sqlalchemy.orm import relationship, backref, aliased
from sqlalchemy import or_, and_, text, func, literal, cast, case, nullslast, nullsfirst, desc, asc
from sqlalchemy.sql.sqltypes import String
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.sql.sqltypes import Date, Integer
from sqlalchemy.sql.expression import distinct
from request_api.utils.enums import RequestorType, StateName, ProcessingTeamWithKeycloackGroup, IAOTeamWithKeycloackGroup
from .FOIMinistryRequests import FOIMinistryRequest
from .FOIAssignees import FOIAssignee
from .FOIRequests import FOIRequest, FOIRequestsSchema
from .FOIRequestApplicantMappings import FOIRequestApplicantMapping
from .FOIRequestApplicants import FOIRequestApplicant
from .FOIRequestStatus import FOIRequestStatus
from .ApplicantCategories import ApplicantCategory
from .FOIRequestWatchers import FOIRequestWatcher
from .FOIRestrictedMinistryRequests import FOIRestrictedMinistryRequest
from .ProgramAreas import ProgramArea
from .FOIRequestExtensions import FOIRequestExtension
from .OpenInformationStatuses import OpenInformationStatuses
from .FOIRequestOIPC import FOIRequestOIPC
from .SubjectCodes import SubjectCode
from .FOIMinistryRequestSubjectCodes import FOIMinistryRequestSubjectCode

class FOIOpenInformationRequests(db.Model):
    __tablename__ = "FOIOpenInformationRequests"
    # Defining the columns
    foiopeninforequestid = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    version = db.Column(db.Integer, primary_key=True, nullable=False)
    foiministryrequest_id = db.Column(db.Integer, ForeignKey('FOIMinistryRequests.foiministryrequestid'), nullable=False)
    foiministryrequestversion_id = db.Column(db.Integer, ForeignKey('FOIMinistryRequests.version'), nullable=False)
    oipublicationstatus_id = db.Column(db.Integer, ForeignKey('OpenInfoPublicationStatuses.oipublicationstatusid'), nullable=False)
    oiexemption_id = db.Column(db.Integer, ForeignKey('OpenInformationExemptions.oiexemptionid'), nullable=True)
    oiassignedto = db.Column(db.String(120), ForeignKey('FOIAssignees.username'), nullable=True)

    oiexemptionapproved = db.Column(db.Boolean, nullable=True)
    pagereference = db.Column(db.String, nullable=True)
    iaorationale = db.Column(db.String, nullable=True)
    oifeedback = db.Column(db.String, nullable=True)
    publicationdate = db.Column(db.DateTime, nullable=True)
    isactive = db.Column(db.Boolean, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=True)
    createdby = db.Column(db.String(120), nullable=False)
    updatedby = db.Column(db.String(120), nullable=True)

    @classmethod
    def getoibasequery(cls, additionalfilter=None, userid=None, isiaorestrictedfilemanager=False, groups=[]):
        _session = db.session

        #rawrequests
        #subquery for getting the latest version
        subquery_maxversion = _session.query(FOIMinistryRequest.foiministryrequestid, func.max(FOIMinistryRequest.version).label('max_version')).group_by(FOIMinistryRequest.foiministryrequestid).subquery()
        joincondition = [
            subquery_maxversion.c.foiministryrequestid == FOIMinistryRequest.foiministryrequestid,
            subquery_maxversion.c.max_version == FOIMinistryRequest.version,
        ]

        print("subquery_maxversion : ",subquery_maxversion)

        #aliase for onbehalf of applicant info
        onbehalf_applicantmapping = aliased(FOIRequestApplicantMapping)
        onbehalf_applicant = aliased(FOIRequestApplicant)

        #aliase for getting ministry restricted flag from FOIRestrictedMinistryRequest
        ministry_restricted_requests = aliased(FOIRestrictedMinistryRequest)

        defaultsorting = case([
                            (FOIMinistryRequest.assignedto == None, # Unassigned requests first
                             literal(None)),
                           ],
        else_ = FOIMinistryRequest.duedate).label('defaultSorting')
        
        recordspagecount = case ([
            (FOIMinistryRequest.recordspagecount.isnot(None), FOIMinistryRequest.recordspagecount)
            ],
            else_= literal("0").label("recordspagecount")
        )

        duedate = case([
                            (FOIMinistryRequest.requeststatuslabel == StateName.onhold.name,  # On Hold
                             literal(None)),
                           ],
                           else_ = cast(FOIMinistryRequest.duedate, String)).label('duedate')
        
        cfrduedate = case([
                            (FOIMinistryRequest.requeststatuslabel == StateName.onhold.name,  # On Hold
                             literal(None)),
                           ],
                           else_ = cast(FOIMinistryRequest.cfrduedate, String)).label('cfrduedate')
        
        onbehalfformatted = case([
                            (and_(onbehalf_applicant.lastname.isnot(None), onbehalf_applicant.firstname.isnot(None)),
                             func.concat(onbehalf_applicant.lastname, ', ', onbehalf_applicant.firstname)),
                            (and_(onbehalf_applicant.lastname.isnot(None), onbehalf_applicant.firstname.is_(None)),
                             onbehalf_applicant.lastname),
                            (and_(onbehalf_applicant.lastname.is_(None), onbehalf_applicant.firstname.isnot(None)),
                             onbehalf_applicant.firstname),
                           ],
                           else_ = 'N/A').label('onBehalfFormatted')
        
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

        selectedcolumns = [
            FOIRequest.foirequestid.label('id'),
            FOIMinistryRequest.version,
            FOIMinistryRequest.foiministryrequestid.label('ministryrequestid'),
            cast(FOIMinistryRequest.axisrequestid, String).label('axisRequestId'),
            cast(FOIMinistryRequest.filenumber, String).label('idNumber'),
            FOIAssignee.firstname.label('assignedToFirstName'),
            FOIAssignee.lastname.label('assignedToLastName'),
            FOIMinistryRequest.closedate,
            FOIOpenInformationRequests.publicationdate,
            FOIRequest.requesttype.label('requestType'),
            cast(FOIRequest.receiveddate, String).label('receivedDateUF'),
            FOIRequestStatus.name.label('currentState'),
            FOIMinistryRequest.assignedgroup.label('assignedGroup'),
            FOIMinistryRequest.assignedto.label('assignedTo'),
            FOIRequestApplicant.firstname.label('firstName'),
            FOIRequestApplicant.lastname.label('lastName'),
            FOIMinistryRequest.description,
            onbehalf_applicant.firstname.label('onBehalfFirstName'),
            onbehalf_applicant.lastname.label('onBehalfLastName'),
            cast(FOIMinistryRequest.recordsearchfromdate, String).label('recordsearchfromdate'),
            cast(FOIMinistryRequest.recordsearchtodate, String).label('recordsearchtodate'),
            cfrduedate,
            duedate,
            ApplicantCategory.name.label('applicantcategory'),
            onbehalfformatted,
            cast(requestpagecount, Integer).label('requestpagecount'),
            axispagecount.label('axispagecount'),
            axislanpagecount.label('axislanpagecount'),
            recordspagecount.label('recordspagecount'),  
            func.lower(ProgramArea.bcgovcode).label('bcgovcode'), 
            FOIMinistryRequest.isoipcreview.label('isoipcreview'),
            FOIRestrictedMinistryRequest.isrestricted.label('isiaorestricted'),
            ministry_restricted_requests.isrestricted.label('isministryrestricted'),
            OpenInformationStatuses.name.label('oiStatusName'),
        ]   


        basequery = (
            _session.query(*selectedcolumns)
            .join(subquery_maxversion, and_(*joincondition))
            .join(FOIOpenInformationRequests, FOIMinistryRequest.foiministryrequestid == FOIOpenInformationRequests.foiministryrequest_id)  # 여기에 적절히 조인 추가
            .join(FOIRequest,and_(FOIRequest.foirequestid == FOIMinistryRequest.foirequest_id, FOIRequest.version == FOIMinistryRequest.foirequestversion_id))
            .join(FOIRequestStatus, FOIRequestStatus.requeststatusid == FOIMinistryRequest.requeststatusid)
            .join(FOIRequestApplicantMapping, and_(FOIRequestApplicantMapping.foirequest_id == FOIMinistryRequest.foirequest_id, FOIRequestApplicantMapping.foirequestversion_id == FOIMinistryRequest.foirequestversion_id, FOIRequestApplicantMapping.requestortypeid == RequestorType['applicant'].value))
            .join(FOIRequestApplicant,FOIRequestApplicant.foirequestapplicantid == FOIRequestApplicantMapping.foirequestapplicantid)
            .join(ApplicantCategory,and_(ApplicantCategory.applicantcategoryid == FOIRequest.applicantcategoryid, ApplicantCategory.isactive == True))
            .join(ProgramArea,FOIMinistryRequest.programareaid == ProgramArea.programareaid)
            .join(FOIRestrictedMinistryRequest,and_(FOIRestrictedMinistryRequest.ministryrequestid == FOIMinistryRequest.foiministryrequestid,
                  FOIRestrictedMinistryRequest.type == 'iao',FOIRestrictedMinistryRequest.isactive == True),isouter=True)
            .join(ministry_restricted_requests,and_(ministry_restricted_requests.ministryrequestid == FOIMinistryRequest.foiministryrequestid,ministry_restricted_requests.type == 'ministry',ministry_restricted_requests.isactive == True),isouter=True)
            .join(OpenInformationStatuses, OpenInformationStatuses.oistatusid == FOIMinistryRequest.oistatus_id)
            .outerjoin(FOIAssignee, FOIAssignee.username == FOIOpenInformationRequests.oiassignedto)  
        )

        # if(additionalfilter == 'watchingRequests'):
        #     #watchby
        #     activefilter = and_(FOIMinistryRequest.isactive == True, FOIRequestStatus.isactive == True)

        #     subquery_watchby = FOIRequestWatcher.getrequestidsbyuserid(userid)
        #     if(requestby == 'IAO'):
        #         dbquery = basequery.join(subquery_watchby, subquery_watchby.c.ministryrequestid == FOIMinistryRequest.foiministryrequestid).filter(activefilter).filter(or_(or_(FOIRestrictedMinistryRequest.isrestricted == False, FOIRestrictedMinistryRequest.isrestricted == None), and_(FOIRestrictedMinistryRequest.isrestricted == True, FOIMinistryRequest.assignedto == userid)))
        #     else:
        #         dbquery = basequery.join(subquery_watchby, subquery_watchby.c.ministryrequestid == FOIMinistryRequest.foiministryrequestid).filter(activefilter).filter(or_(or_(ministry_restricted_requests.isrestricted == isministryrestrictedfilemanager, ministry_restricted_requests.isrestricted == None), and_(ministry_restricted_requests.isrestricted == True, FOIMinistryRequest.assignedministryperson == userid)))   
            
        # elif(additionalfilter == 'myRequests'):
        #     #myrequest
        #     if(requestby == 'IAO'):
        #         dbquery = basequery.filter(FOIMinistryRequest.assignedto == userid).filter(ministryfilter)
        #     else:
        #         dbquery = basequery.filter(FOIMinistryRequest.assignedministryperson == userid).filter(ministryfilter)
        # elif(additionalfilter == 'unassignedRequests'):
        #     if(requestby == 'IAO'):
        #         dbquery = basequery.filter(FOIMinistryRequest.assignedto == None).filter(ministryfilter)
        # elif(additionalfilter.lower() == 'all'):           
        #     if(requestby == 'IAO'):
        #         dbquery = basequery.filter(ministryfilter).filter(FOIMinistryRequest.assignedto.isnot(None)).filter(or_(FOIRestrictedMinistryRequest.isrestricted == isiaorestrictedfilemanager, or_(FOIRestrictedMinistryRequest.isrestricted.is_(None), FOIRestrictedMinistryRequest.isrestricted == False)))
        #     else:               
        #         dbquery = basequery.filter(ministryfilter).filter(or_(ministry_restricted_requests.isrestricted == isministryrestrictedfilemanager, or_(ministry_restricted_requests.isrestricted.is_(None), ministry_restricted_requests.isrestricted == False)))
        # else:
        #     if(isiaorestrictedfilemanager == True or isministryrestrictedfilemanager == True):
        #         dbquery = basequery.filter(ministryfilter)
        #     else:
        #         if(requestby == 'IAO'):
        #             dbquery = basequery.filter(or_(or_(FOIRestrictedMinistryRequest.isrestricted == False, FOIRestrictedMinistryRequest.isrestricted == None), and_(FOIRestrictedMinistryRequest.isrestricted == True, FOIMinistryRequest.assignedto == userid))).filter(ministryfilter)
        #         else:
        #             dbquery = basequery.filter(or_(or_(ministry_restricted_requests.isrestricted == False, ministry_restricted_requests.isrestricted == None), and_(ministry_restricted_requests.isrestricted == True, FOIMinistryRequest.assignedministryperson == userid))).filter(ministryfilter)

        return basequery
    

    @classmethod
    def getrequestssubquery(cls, groups, filterfields, keyword, additionalfilter, userid, iaoassignee, ministryassignee, requestby, isiaorestrictedfilemanager=False, isministryrestrictedfilemanager=False):
        #for queue/ oi dashboard       
        oibasequery = FOIOpenInformationRequests.getoibasequery(additionalfilter, userid, isiaorestrictedfilemanager, groups)
        #oibasequery = oibasequery.filter(FOIRawRequest.status != 'Unopened').filter(FOIRawRequest.status != 'Closed')
        print("oibasequery : ",oibasequery)

        #filter/search
        # if(len(filterfields) > 0 and keyword is not None):
        #     filtercondition = FOIRawRequest.getfilterforrequestssubquery(filterfields, keyword)
        #     return basequery.filter(filtercondition)
        # else:
        #     return basequery

        return oibasequery
        
        

    @classmethod
    def getrequestspagination(cls, group, page, size, sortingitems, sortingorders, filterfields, keyword, additionalfilter, userid, isiaorestrictedfilemanager, usertype, isministryrestrictedfilemanager=False):
        iaoassignee = aliased(FOIAssignee)
        ministryassignee = aliased(FOIAssignee)
        #subquery_ministry_queue = FOIMinistryRequest.getrequestssubquery(groups, filterfields, keyword, additionalfilter, userid, iaoassignee, ministryassignee, 'IAO', isiaorestrictedfilemanager, isministryrestrictedfilemanager)
        subquery_oirequest_queue = FOIOpenInformationRequests.getrequestssubquery(group, filterfields, keyword, additionalfilter, userid, iaoassignee, ministryassignee, "OI", isiaorestrictedfilemanager, isministryrestrictedfilemanager)
        print("subquery_oirequest_queue : ",subquery_oirequest_queue)
        #sorting
        sortingcondition = FOIMinistryRequest.getsorting(sortingitems, sortingorders, iaoassignee, ministryassignee)
        print("sortingcondition : ",sortingcondition)
        #rawrequests
        # if usertype == "iao" or groups is None:
        #     subquery_rawrequest_queue = FOIRawRequest.getrequestssubquery(filterfields, keyword, additionalfilter, userid, isiaorestrictedfilemanager, groups)
        #     query_full_queue = subquery_rawrequest_queue.union(subquery_ministry_queue)
        #     return query_full_queue.order_by(*sortingcondition).paginate(page=page, per_page=size)
        # elif usertype == "oi":
        #     requestby = 'OI'
        #     subquery_oirequest_queue = FOIOpenInformationRequests.getrequestssubquery(group, filterfields, keyword, additionalfilter, userid, iaoassignee, ministryassignee, requestby, isiaorestrictedfilemanager, isministryrestrictedfilemanager)
        # else:
        print("getrequestspagination안에 group : ",group)
        return subquery_oirequest_queue.order_by(*sortingcondition).paginate(page=page, per_page=size)
    
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
                statusfilter = FOIMinistryRequest.requeststatuslabel.in_([StateName.callforrecords.name,StateName.recordsreview.name,StateName.feeestimate.name,StateName.consult.name,StateName.ministrysignoff.name,StateName.onhold.name,StateName.deduplication.name,StateName.harmsassessment.name,StateName.response.name,StateName.peerreview.name,StateName.tagging.name,StateName.readytoscan.name, StateName.recordsreadyforreview.name])
            ministryfilter = and_(
                                FOIMinistryRequest.isactive == True,
                                FOIRequestStatus.isactive == True,
                                or_(*groupfilter)
                            )
        ministryfilterwithclosedoipc = and_(ministryfilter, 
                                            or_(statusfilter, 
                                                and_(FOIMinistryRequest.requeststatuslabel == StateName.closed.name)
                                                )
                                            )
        return ministryfilter


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
    
class FOIOpenInfoRequestSchema(ma.Schema):
    class Meta:
        fields = (
            'foiopeninforequestid', 'foiministryrequest_id', 'foiministryrequestversion_id', 'oipublicationstatus_id', 'oiexemption_id', 'oiassignedto',
            'oiexemptionapproved', 'pagereference', 'iaorationale', 'oifeedback', 'publicationdate', 'created_at', 'updated_at', 'createdby', 'updatedby'
        )