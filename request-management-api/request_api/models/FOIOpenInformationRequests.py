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
from .FOIRequestStatus import FOIRequestStatus
from request_api.models.default_method_result import DefaultMethodResult
from sqlalchemy import text
from datetime import datetime as datetime2
import logging

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

    def getcurrentfoiopeninforequest(cls, foiminstryrequestid)->DefaultMethodResult:
        try:
            foiopeninforequest_schema = FOIOpenInfoRequestSchema()
            query = db.session.query(FOIOpenInformationRequests).filter_by(foiministryrequest_id=foiminstryrequestid).order_by(FOIOpenInformationRequests.version.desc()).first()
            return foiopeninforequest_schema.dump(query)
        except Exception as exception:
            logging.error(f"Error: {exception}")
                
    def createopeninfo(cls, foiopeninforequest, userid)->DefaultMethodResult:
        try:
            createddate = datetime2.now().isoformat()
            new_foiopeninforequest = FOIOpenInformationRequests(
                version=1,
                foiministryrequest_id=foiopeninforequest["foiministryrequest_id"],
                foiministryrequestversion_id=foiopeninforequest["foiministryrequestversion_id"],
                oipublicationstatus_id=foiopeninforequest["oipublicationstatus_id"],
                oiexemption_id=foiopeninforequest["oiexemption_id"],
                pagereference=foiopeninforequest["pagereference"],
                iaorationale=foiopeninforequest["iaorationale"],
                isactive=True,
                created_at=createddate,
                createdby=userid,
            )
            db.session.add(new_foiopeninforequest)
            db.session.commit()      
            return DefaultMethodResult(True, "FOIOpenInfo request created", new_foiopeninforequest.foiopeninforequestid)
        except Exception as exception:
            logging.error(f"Error: {exception}")
            return DefaultMethodResult(False, "FOIOpenInfo request unable to be created")
    
    def updateopeninfo(cls, foiopeninforequest, userid)->DefaultMethodResult:
        try:
            updateddate = datetime2.now().isoformat()
            updated_foiopeninforequest = FOIOpenInformationRequests(
                version=foiopeninforequest['version']+1,
                foiministryrequest_id=foiopeninforequest["foiministryrequest_id"],
                foiministryrequestversion_id=foiopeninforequest["foiministryrequestversion_id"],
                oipublicationstatus_id=foiopeninforequest["oipublicationstatus_id"],
                oiexemption_id=foiopeninforequest["oiexemption_id"],
                iaorationale=foiopeninforequest["iaorationale"],
                pagereference=foiopeninforequest["pagereference"],
                oiassignedto=foiopeninforequest["oiassignedto"],
                oiexemptionapproved=foiopeninforequest["oiexemptionapproved"],
                oifeedback=foiopeninforequest["oifeedback"],
                publicationdate=foiopeninforequest["publicationdate"],
                isactive=True,
                created_at=foiopeninforequest["created_at"],
                updated_at=updateddate,
                createdby=foiopeninforequest["createdby"],
                updatedby=userid,
            )
            db.session.add(updated_foiopeninforequest)
            db.session.commit()
            return DefaultMethodResult(True, "FOIOpenInfo request version updated", updated_foiopeninforequest.foiopeninforequestid)
        except Exception as exception:
            logging.error(f"Error: {exception}")
            return DefaultMethodResult(False, "FOIOpenInfo request version unable to be updated")
        
    def deactivatefoiopeninforequest(cls, foiopeninforequestid, userid, foiministryrequestid)->DefaultMethodResult:
        try:
            sql = """UPDATE public."FOIOpenInformationRequests" 
            SET isactive=false, updated_at=now(), updatedby=:userid 
            WHERE foiministryrequest_id=:foiministryrequestid AND isactive=true 
            AND version != (SELECT version FROM public."FOIOpenInformationRequests" WHERE foiopeninforequestid = :foiopeninforequestid ORDER BY "version" desc limit 1);"""
            db.session.execute(text(sql), {'foiopeninforequestid': foiopeninforequestid, 'userid':userid, 'foiministryrequestid': foiministryrequestid})
            db.session.commit()
            return DefaultMethodResult(True, "FOIOpenInfo request version updated", foiopeninforequestid)
        except Exception as exception:
            logging.error(f"Error: {exception}")
            return DefaultMethodResult(False, "FOIOpenInfo request version unable to be updated")
        finally:
            db.session.close()
    
    @classmethod
    def getoibasequery(cls, additionalfilter=None, userid=None, isiaorestrictedfilemanager=False, groups=[]):
        _session = db.session

        # subquery for getting the latest version of FOIOpenInformationRequests
        subquery_maxversion = (
                _session.query(
                    FOIOpenInformationRequests.foiopeninforequestid,
                    func.max(FOIOpenInformationRequests.version).label('max_version')
                )
                .group_by(FOIOpenInformationRequests.foiopeninforequestid)
                .subquery()
        )

        joincondition = [
            subquery_maxversion.c.foiopeninforequestid == FOIOpenInformationRequests.foiopeninforequestid,
            subquery_maxversion.c.max_version == FOIOpenInformationRequests.version,
        ]

        print("subquery_maxversion : ",subquery_maxversion)
        print("userid:", userid)

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

        # duedate = case([
        #                     (FOIMinistryRequest.requeststatuslabel == StateName.onhold.name,  # On Hold
        #                      literal(None)),
        #                    ],
        #                    else_ = cast(FOIMinistryRequest.duedate, String)).label('duedate')
        
        # cfrduedate = case([
        #                     (FOIMinistryRequest.requeststatuslabel == StateName.onhold.name,  # On Hold
        #                      literal(None)),
        #                    ],
        #                    else_ = cast(FOIMinistryRequest.cfrduedate, String)).label('cfrduedate')
        
        # onbehalfformatted = case([
        #                     (and_(onbehalf_applicant.lastname.isnot(None), onbehalf_applicant.firstname.isnot(None)),
        #                      func.concat(onbehalf_applicant.lastname, ', ', onbehalf_applicant.firstname)),
        #                     (and_(onbehalf_applicant.lastname.isnot(None), onbehalf_applicant.firstname.is_(None)),
        #                      onbehalf_applicant.lastname),
        #                     (and_(onbehalf_applicant.lastname.is_(None), onbehalf_applicant.firstname.isnot(None)),
        #                      onbehalf_applicant.firstname),
        #                    ],
        #                    else_ = 'N/A').label('onBehalfFormatted')
        
        # axispagecount = case ([
        #     (FOIMinistryRequest.axispagecount.isnot(None), FOIMinistryRequest.axispagecount)
        #     ],
        #     else_= literal("0").label("axispagecount")
        # )
        # axislanpagecount = case ([
        #     (FOIMinistryRequest.axislanpagecount.isnot(None), FOIMinistryRequest.axislanpagecount)
        #     ],
        #     else_= literal("0").label("axislanpagecount")
        # )
        recordspagecount = case ([
            (FOIMinistryRequest.recordspagecount.isnot(None), FOIMinistryRequest.recordspagecount)
            ],
            else_= literal("0").label("recordspagecount")
        )
        # requestpagecount = case([
        #         (and_(axispagecount.isnot(None), recordspagecount.isnot(None), cast(axispagecount, Integer) > cast(recordspagecount, Integer)),
        #             axispagecount),
        #         (and_(recordspagecount.isnot(None)),
        #             recordspagecount),
        #         (and_(axispagecount.isnot(None)),
        #             axispagecount),
        #         ],
        #         else_= literal("0"))

        assignedToFormatted = case([
                (and_(FOIAssignee.lastname.isnot(None), FOIAssignee.firstname.isnot(None)),
                func.concat(FOIAssignee.lastname, ', ', FOIAssignee.firstname)),
                (and_(FOIAssignee.lastname.isnot(None), FOIAssignee.firstname.is_(None)),
                FOIAssignee.lastname),
                (and_(FOIAssignee.lastname.is_(None), FOIAssignee.firstname.isnot(None)),
                FOIAssignee.firstname),
                (FOIOpenInformationRequests.oiassignedto.is_(None),
                'Unassigned'),
            ],
            else_ = FOIOpenInformationRequests.oiassignedto).label('assignedToFormatted')
        
        oifilter = cls.getgroupfilters(groups)
        # from_closed = case(
        #     [(FOIMinistryRequest.closedate.isnot(None), 
        #     func.greatest(
        #         cast(func.date_part('day', func.current_date() - FOIMinistryRequest.closedate), Integer),
        #         1
        #     )
        #     )],
        #     else_=literal('N/A')
        # ).label('from_closed')

        # Define the selected columns
        selectedcolumns = [
            FOIRequest.foirequestid.label('id'), 
            #FOIMinistryRequest.version,
            FOIMinistryRequest.foiministryrequestid.label('ministryrequestid'), 
            cast(FOIMinistryRequest.axisrequestid, String).label('axisRequestId'),
            # FOIAssignee.firstname.label('assignedToFirstName'),
            # FOIAssignee.lastname.label('assignedToLastName'),
            FOIMinistryRequest.closedate, 
            FOIRequest.requesttype.label('requestType'), 
            cast(FOIMinistryRequest.filenumber, String).label('idNumber'),
            #cast(FOIRequest.receiveddate, String).label('receivedDateUF'),
            #FOIRequestStatus.name.label('currentState'),
            #FOIMinistryRequest.assignedgroup.label('assignedGroup'),
            #FOIMinistryRequest.assignedto.label('assignedTo'),
            # FOIRequestApplicant.firstname.label('firstName'),
            # FOIRequestApplicant.lastname.label('lastName'),
            #FOIMinistryRequest.description,
            # onbehalf_applicant.firstname.label('onBehalfFirstName'),
            # onbehalf_applicant.lastname.label('onBehalfLastName'),
            # cast(FOIMinistryRequest.recordsearchfromdate, String).label('recordsearchfromdate'),
            # cast(FOIMinistryRequest.recordsearchtodate, String).label('recordsearchtodate'),
            # cfrduedate,
            # duedate,
            ApplicantCategory.name.label('applicantcategory'),
            #onbehalfformatted,
            # cast(requestpagecount, Integer).label('requestpagecount'),
            # axispagecount.label('axispagecount'),
            # axislanpagecount.label('axislanpagecount'),
            recordspagecount.label('recordspagecount'),  
            # func.lower(ProgramArea.bcgovcode).label('bcgovcode'), 
            # FOIMinistryRequest.isoipcreview.label('isoipcreview'),
            # FOIRestrictedMinistryRequest.isrestricted.label('isiaorestricted'),
            # ministry_restricted_requests.isrestricted.label('isministryrestricted'),
            OpenInformationStatuses.name.label('oiStatusName'), 
            cls.publicationdate,
            cls.created_at, 
            assignedToFormatted, 
            cls.version,
            cls.foiopeninforequestid,
            FOIRequestStatus.name.label('currentState'),
            FOIRestrictedMinistryRequest.isrestricted.label('isiaorestricted'),
            #from_closed
        ]   

        basequery = (
            _session.query(*selectedcolumns)
            .join(subquery_maxversion, and_(*joincondition))
            .join(FOIMinistryRequest, and_(
                FOIMinistryRequest.foiministryrequestid == cls.foiministryrequest_id, 
                FOIMinistryRequest.version == cls.foiministryrequestversion_id,
                FOIMinistryRequest.isactive == True))
            .join(FOIRequest, and_(FOIRequest.foirequestid == FOIMinistryRequest.foirequest_id, FOIRequest.version == FOIMinistryRequest.foirequestversion_id))
            .join(ApplicantCategory,and_(ApplicantCategory.applicantcategoryid == FOIRequest.applicantcategoryid, ApplicantCategory.isactive == True))
            .join(OpenInformationStatuses, OpenInformationStatuses.oistatusid == FOIMinistryRequest.oistatus_id)
            .join(FOIRequestStatus, FOIRequestStatus.requeststatusid == FOIMinistryRequest.requeststatusid)
            .join(FOIRestrictedMinistryRequest,
                                and_(
                                    FOIRestrictedMinistryRequest.ministryrequestid == FOIMinistryRequest.foiministryrequestid,
                                    FOIRestrictedMinistryRequest.type == 'iao',
                                    FOIRestrictedMinistryRequest.isactive == True),
                                isouter=True
            ).outerjoin(FOIAssignee, FOIAssignee.username == cls.oiassignedto) 
        )
            
        if additionalfilter == 'watchingRequests':
            print("foi open info inside: watchingRequests ")
            # basequery = basequery.join(subquery_watchby, subquery_watchby.c.ministryrequestid == FOIMinistryRequest.foiministryrequestid)
            # basequery.join(subquery_watchby, subquery_watchby.c.ministryrequestid == FOIMinistryRequest.foiministryrequestid).filter(activefilter).filter(or_(or_(FOIRestrictedMinistryRequest.isrestricted == False, FOIRestrictedMinistryRequest.isrestricted == None), and_(FOIRestrictedMinistryRequest.isrestricted == True, FOIMinistryRequest.assignedto == userid)))
            subquery_watchby = FOIRequestWatcher.getrequestidsbyuserid(userid)
            basequery = basequery.join(
                subquery_watchby, 
                subquery_watchby.c.ministryrequestid == FOIMinistryRequest.foiministryrequestid
            ).filter(FOIMinistryRequest.isactive == True ,cls.oiassignedto == userid)
        elif additionalfilter == 'myRequests':
            print("foi open info inside: myRequests ")
            basequery = basequery.filter(
                and_(
                    FOIMinistryRequest.assignedgroup == 'OI Team',
                    cls.oiassignedto == userid
                )
            ).order_by(
                # Exemption requests first (1 if no exemption, 0 if has exemption)
                case(
                    [(cls.oiexemption_id.isnot(None), 0)],
                    else_=1
                ),
                desc(FOIMinistryRequest.closedate)  # Then sort by closedate (newest to oldest)
            )
            
            # basequery = (basequery
            #     .filter(cls.oiassignedto == userid)
            #     .order_by(
            #         exemption_priority,  # Sort exemption requests first
            #         asc(cls.publicationdate)  # Then by publication date (earliest to latest)
            #     ))
        elif additionalfilter == 'unassignedRequests':
            print("foi open info inside: unassignedRequests ")
            #basequery = basequery.filter(cls.oiassignedto == None)
            basequery = basequery.filter(
                and_(
                    FOIMinistryRequest.assignedgroup == 'OI Team',  # Requests assigned to OI Team
                    FOIMinistryRequest.isactive == True,            # Active requests only
                    cls.oiassignedto.is_(None)                      # Requests that are assigned to a user
                )
            ).order_by(
                # Priority order: 
                # 1. Exemption requests (oistatus_id = 2)
                # 2. Publication reviews (oistatus_id = 4)
                # 3. Other requests
                case(
                    [(FOIMinistryRequest.oistatus_id == 2, 0),     # Exemption requests first
                    (FOIMinistryRequest.oistatus_id == 4, 1)],    # Publication reviews second
                    else_=2                                         # Other requests last
                ),
                desc(FOIMinistryRequest.closedate)
            )
        elif additionalfilter == 'teamRequests':
            print("foi open info inside: teamRequests ")
            basequery = basequery.filter(
            and_(
                FOIMinistryRequest.assignedgroup == 'OI Team',  # Requests assigned to OI Team
                FOIMinistryRequest.isactive == True,            # Active requests only
                cls.oiassignedto.isnot(None)                    # Requests that are assigned to a user
            )
            ).order_by(
                # Exemption requests first (1 if no exemption, 0 if has exemption)
                case(
                    [(cls.oiexemption_id.isnot(None), 0)],
                    else_=1
                ),
                desc(FOIMinistryRequest.closedate)  # Then sort by creation date (newest to oldest)
            )


        print("additionalfilter basequery : ",basequery)
        
        return basequery

    @classmethod
    def getrequestssubquery(cls, groups, filterfields, keyword, additionalfilter, userid, iaoassignee, ministryassignee, requestby, isiaorestrictedfilemanager=False, isministryrestrictedfilemanager=False):
        oibasequery = cls.getoibasequery(additionalfilter, userid, isiaorestrictedfilemanager, groups)
        
        if len(filterfields) > 0 and keyword is not None:
            filtercondition = cls.getfilterforrequestssubquery(filterfields, keyword)
            return oibasequery.filter(filtercondition)
        else:
            return oibasequery

    @classmethod
    def getrequestspagination(cls, group, page, size, sortingitems, sortingorders, filterfields, keyword, additionalfilter, userid, isiaorestrictedfilemanager, usertype, isministryrestrictedfilemanager=False):
        iaoassignee = aliased(FOIAssignee)
        ministryassignee = aliased(FOIAssignee)
        subquery_oirequest_queue = cls.getrequestssubquery(group, filterfields, keyword, additionalfilter, userid, iaoassignee, ministryassignee, "OI", isiaorestrictedfilemanager, isministryrestrictedfilemanager)
        
        sortingcondition = cls.getsorting(sortingitems, sortingorders)
        
        return subquery_oirequest_queue.order_by(*sortingcondition).paginate(page=page, per_page=size)

    @classmethod
    def getsorting(cls, sortingitems, sortingorders):
        sortingcondition = []
        if len(sortingitems) > 0 and len(sortingorders) > 0 and len(sortingitems) == len(sortingorders):
            for field, order in zip(sortingitems, sortingorders):
                if cls.validatefield(field):
                    sortfield = cls.findfield(field)
                    if order == 'desc':
                        sortingcondition.append(nullslast(desc(sortfield)))
                    else:
                        sortingcondition.append(nullsfirst(asc(sortfield)))
        
        # Default sorting: Received Date (newest to oldest)
        if len(sortingcondition) == 0:
            sortingcondition.append(asc(cls.created_at))
            #sortingcondition.append(nullslast(desc(cls.findfield('created_at'))))
            

        # Always sort by id last to prevent pagination collisions
        sortingcondition.append(asc('id'))
        
        return sortingcondition

    @classmethod
    def validatefield(cls, field):
        valid_fields = ['receivedDateUF', 'requestType', 'pageCount', 
                        'publicationStatus', 'from_closed', 'publicationdate', 'assignee']
        return field in valid_fields

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
    def findfield(cls, field):
        if field == 'receivedDateUF':
            return FOIRequest.receiveddate
        elif field == 'requestType':
            return FOIRequest.requesttype
        elif field == 'pageCount':
            return FOIMinistryRequest.recordspagecount
        elif field == 'publicationStatus':
            return OpenInformationStatuses.name
        elif field == 'from_closed':
            return func.coalesce(
                func.greatest(
                    func.ceil((func.date_part('day', func.current_date() - FOIMinistryRequest.closedate) + 1) * 5 / 7) - 
                    func.ceil((func.date_part('dow', FOIMinistryRequest.closedate) + func.date_part('dow', func.current_date())) / 5),
                    0
                ),
                0
            )
        elif field == 'publicationdate':
            return cls.publicationdate
        elif field == 'assignee':
            return cls.oiassignedto
        else:
            return text(field)

    @classmethod
    def getfilterforrequestssubquery(cls, filterfields, keyword):
        return or_(*[cls.getfiltercondition(filterfield, keyword) for filterfield in filterfields])

    @classmethod
    def getfiltercondition(cls, filterfield, keyword):
        if filterfield == 'requestType':
            return FOIRequest.requesttype.ilike(f'%{keyword}%')
        elif filterfield == 'publicationStatus':
            return OpenInformationStatuses.name.ilike(f'%{keyword}%')
        elif filterfield == 'assignee':
            return cls.oiassignedto.ilike(f'%{keyword}%')
        else:
            return text(filterfield).ilike(f'%{keyword}%')
    
    @classmethod
    def getgroupfilters(cls, groups):
        if groups is None:
            return FOIMinistryRequest.isactive == True
        else:
            groupfilter = []
            if IAOTeamWithKeycloackGroup.oi.value in groups:
                groupfilter.append(
                            and_(
                                FOIMinistryRequest.assignedgroup.in_(tuple(groups))
                            )
                        )
                statusfilter = FOIMinistryRequest.requeststatuslabel != StateName.closed.name
            else:
                groupfilter.append(
                        or_(
                            FOIMinistryRequest.assignedgroup.in_(tuple(groups))
                        )
                    )
                statusfilter = FOIMinistryRequest.requeststatuslabel.in_([StateName.callforrecords.name,StateName.recordsreview.name,StateName.feeestimate.name,StateName.consult.name,StateName.ministrysignoff.name,StateName.onhold.name,StateName.deduplication.name,StateName.harmsassessment.name,StateName.response.name,StateName.peerreview.name,StateName.tagging.name,StateName.readytoscan.name, StateName.recordsreadyforreview.name])
            oifilter = and_(
                                FOIMinistryRequest.isactive == True,
                                FOIRequestStatus.isactive == True,
                                or_(*groupfilter)
                            )
            return oifilter

class FOIOpenInfoRequestSchema(ma.Schema):
    class Meta:
        fields = (
            'foiopeninforequestid', 'version', 'foiministryrequest_id', 'foiministryrequestversion_id', 'oipublicationstatus_id', 'oiexemption_id', 'oiassignedto',
            'oiexemptionapproved', 'pagereference', 'iaorationale', 'oifeedback', 'publicationdate', 'created_at', 'updated_at', 'createdby', 'updatedby'
        )