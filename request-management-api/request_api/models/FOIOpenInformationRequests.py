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
from request_api.utils.enums import RequestorType, StateName, ProcessingTeamWithKeycloackGroup, IAOTeamWithKeycloackGroup, OICloseReason, ExcludedProgramArea, OIStatusEnum
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
from request_api.models.FOIRequestRecords import FOIRequestRecord
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
    oiexemptiondate = db.Column(db.DateTime, nullable=True)
    isactive = db.Column(db.Boolean, nullable=False)
    copyrightsevered = db.Column(db.Boolean, nullable=True)

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
            createddate = datetime2.now().isoformat()
            updated_foiopeninforequest = FOIOpenInformationRequests(
                foiopeninforequestid=foiopeninforequest['foiopeninforequestid'],
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
                oiexemptiondate=foiopeninforequest["oiexemptiondate"],
                copyrightsevered=foiopeninforequest["copyrightsevered"],
                isactive=True,
                created_at=createddate,
                createdby=userid,
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
            FOIOpenInformationRequests.isactive == True
        ]

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

        recordspagecount = case ([
            (FOIMinistryRequest.recordspagecount.isnot(None), FOIMinistryRequest.recordspagecount)
            ],
            else_= literal("0").label("recordspagecount")
        )

        oistatusname = case(
            [(FOIMinistryRequest.oistatus_id.is_(None), literal('unopened'))],
            else_=OpenInformationStatuses.name
        ).label('oiStatusName')

        receiveddate = case(
            [
                (FOIMinistryRequest.oistatus_id.is_(None), FOIMinistryRequest.closedate),
                (and_(
                    FOIMinistryRequest.oistatus_id.isnot(None),
                    cls.oiexemptiondate.is_(None)
                ), FOIMinistryRequest.closedate),
            ],
            else_=cls.oiexemptiondate
        ).label('receivedDate')

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
     
        excluded_program_areas = ExcludedProgramArea.list()

        eligible_close_reasons = OICloseReason.list()

        selectedcolumns = [
            FOIRequest.foirequestid.label('id'), 
            FOIMinistryRequest.foiministryrequestid.label('ministryrequestid'), 
            cast(FOIMinistryRequest.axisrequestid, String).label('axisRequestId'),
            FOIMinistryRequest.closedate, 
            FOIRequest.requesttype.label('requestType'), 
            cast(FOIMinistryRequest.filenumber, String).label('idNumber'),
            ApplicantCategory.name.label('applicantcategory'),
            recordspagecount.label('recordspagecount'),  
            oistatusname.label('oiStatusName'),
            receiveddate.label('receivedDate'),
            cls.publicationdate,
            cls.created_at, 
            assignedToFormatted, 
            cls.version,
            cls.foiopeninforequestid,
            FOIRequestStatus.name.label('currentState'),
            FOIRestrictedMinistryRequest.isrestricted.label('isiaorestricted'),
        ]   

        basequery = (
            _session.query(*selectedcolumns)
            .join(subquery_maxversion, and_(*joincondition))
            .join(FOIMinistryRequest, and_(
                FOIMinistryRequest.foiministryrequestid == cls.foiministryrequest_id, 
                FOIMinistryRequest.isactive == True,
                FOIMinistryRequest.programareaid.notin_(excluded_program_areas),
            ))
            .join(FOIRequest, and_(FOIRequest.foirequestid == FOIMinistryRequest.foirequest_id, FOIRequest.version == FOIMinistryRequest.foirequestversion_id, FOIRequest.requesttype != 'personal'))
            .join(ApplicantCategory,and_(ApplicantCategory.applicantcategoryid == FOIRequest.applicantcategoryid, ApplicantCategory.isactive == True))
            .outerjoin(OpenInformationStatuses, OpenInformationStatuses.oistatusid == FOIMinistryRequest.oistatus_id)
            .join(FOIRequestStatus, FOIRequestStatus.requeststatusid == FOIMinistryRequest.requeststatusid)
            .join(FOIRestrictedMinistryRequest,
                                and_(
                                    FOIRestrictedMinistryRequest.ministryrequestid == FOIMinistryRequest.foiministryrequestid,
                                    FOIRestrictedMinistryRequest.type == 'iao',
                                    FOIRestrictedMinistryRequest.isactive == True),
                                isouter=True
            ).outerjoin(FOIAssignee, FOIAssignee.username == cls.oiassignedto) 
            .filter(
                or_( 
                    and_(
                        FOIMinistryRequest.oistatus_id.isnot(None),
                        #FOIMinistryRequest.requeststatuslabel != StateName.closed.name
                    ),
                    and_(
                        FOIMinistryRequest.oistatus_id.is_(None),
                        FOIMinistryRequest.requeststatuslabel == StateName.closed.name,
                        FOIMinistryRequest.closereasonid.in_(eligible_close_reasons)
                    )
                )
            )
            .order_by(  
                case(
                    [(FOIMinistryRequest.oistatus_id == OIStatusEnum.EXEMPTION_REQUEST.value, 0)],
                    else_=1
                ),
                receiveddate.desc()
            )
        )
            
        if additionalfilter == 'watchingRequests':
            subquery_watchby = FOIRequestWatcher.getrequestidsbyuserid(userid)
            basequery = basequery.join(
                subquery_watchby, 
                subquery_watchby.c.ministryrequestid == FOIMinistryRequest.foiministryrequestid
            )
        elif additionalfilter == 'myRequests':
            basequery = basequery.filter(
                and_(
                    cls.oiassignedto == userid
                )
            )

        elif additionalfilter == 'unassignedRequests':
            basequery = basequery.filter(
                    cls.oiassignedto.is_(None),                         
            )
            
        elif additionalfilter == 'teamRequests':
            pass
        
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
        
        if len(sortingcondition) == 0:
            default_sort = case(
                [(cls.oiexemptiondate.is_(None), FOIMinistryRequest.closedate)],
                else_=cls.oiexemptiondate
            )
            sortingcondition.append(asc(default_sort))

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
        elif field == 'duedate':
            return FOIMinistryRequest.duedate
        elif field == 'isoipcreview':
            return FOIMinistryRequest.isoipcreview
        elif field == 'ministry':
            return func.upper(ProgramArea.bcgovcode)
        elif field == 'description':
            return FOIMinistryRequest.description
        elif field == 'firstName':
            return FOIRequestApplicant.firstname
        elif field == 'lastName':
            return FOIRequestApplicant.lastname
        elif field == 'assignedToFirstName':
            return FOIAssignee.firstname
        elif field == 'assignedToLastName':
            return FOIAssignee.lastname
        elif field == 'idNumber':
            return cast(FOIMinistryRequest.filenumber, String)
        elif field == 'axisRequestId':
            return cast(FOIMinistryRequest.axisrequestid, String)
        elif field == 'currentState':   
            return FOIRequestStatus.name
        else:
            return text(field)

    @classmethod
    def getfilterforrequestssubquery(cls, filterfields, keyword):
        _keywords = []
        if(keyword is not None):
            _keywords = keyword.lower().replace(",", " ").split()

        #filter/search
        filtercondition = []
        for _keyword in _keywords:
            onekeywordfiltercondition = []
            if(_keyword != 'restricted'):
                for field in filterfields:
                    field_value = cls.findfield(field)
                    condition = field_value.ilike('%'+_keyword+'%')
                    exists_query = db.session.query(field_value).filter(condition).exists()
                    has_match = db.session.query(exists_query).scalar()
                    if has_match:
                        onekeywordfiltercondition.append(condition)                   
            else:
                filtercondition.append(FOIRestrictedMinistryRequest.isrestricted == True)
        
            filtercondition.append(or_(*onekeywordfiltercondition))

        return and_(*filtercondition)

    @classmethod
    def getfiltercondition(cls, filterfield, keyword):

        # Map filter fields to their corresponding model attributes
        field_mapping = {
            'requestType': FOIRequest.requesttype,
            'publicationStatus': OpenInformationStatuses.name,
            'assignee': cls.oiassignedto,
            'idNumber': cast(FOIMinistryRequest.filenumber, String),
            'axisRequestId': cast(FOIMinistryRequest.axisrequestid, String),
            'description': FOIMinistryRequest.description,
            'ministry': ProgramArea.bcgovcode,
            'firstName': FOIRequestApplicant.firstname,
            'lastName': FOIRequestApplicant.lastname,
            'assignedToFirstName': FOIAssignee.firstname,
            'assignedToLastName': FOIAssignee.lastname,
            # Add more mappings as needed
        }

        # Get the corresponding model attribute from the mapping
        field = field_mapping.get(filterfield)
    
        if field is not None:
            return field.ilike(f'%{keyword}%')
        else:
            return filterfield.ilike(f'%{keyword}%')
    
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

    @classmethod
    def getdatafromOILayerpagecounts(cls, requestid, ministryRequestid):
        try:
            # Import moved inside the method to avoid circular import
            from request_api.services.records.recordservicebase import recordservicebase

            service = recordservicebase() 
            uploadedrecords = FOIRequestRecord.fetch(requestid, ministryRequestid) 

            response = None
            err = None
            
            if len(uploadedrecords) > 0:
                response, err = service.makedocreviewerrequest(
                    "GET", "/api/ministryrequest/{}/pageflag/count".format(ministryRequestid)
            )

            return response, err
        except Exception as e:
            logging.error(f"Error getting OI Layer page counts: {str(e)}")
            return None, str(e)
    
    @classmethod
    def advancedsearch(cls, params, userid, isiaorestrictedfilemanager=False):
        basequery = FOIOpenInformationRequests.getoibasequery(None, userid, isiaorestrictedfilemanager)

        #filter/search
        filtercondition = FOIOpenInformationRequests.getfilterforadvancedsearch(params)
        searchquery = basequery.filter(and_(*filtercondition))

        #ministry requests
        # iaoassignee = aliased(FOIAssignee)
        # ministryassignee = aliased(FOIAssignee)
        # subquery_ministry_queue = FOIMinistryRequest.advancedsearchsubquery(params, iaoassignee, ministryassignee, userid, 'IAO', isiaorestrictedfilemanager)

        #oi requests

        #sorting
        sortingcondition = FOIOpenInformationRequests.getsorting(params['sortingitems'], params['sortingorders'])

        #rawrequests
        #query_full_queue = searchquery.union(subquery_ministry_queue)
        return searchquery.order_by(*sortingcondition).paginate(page=params['page'], per_page=params['size'])

    @classmethod
    def getfilterforadvancedsearch(cls, params):
        #filter/search
        filtercondition = []
        includeclosed = False

        #request state: unopened, call for records, etc.
        if(len(params['requeststate']) > 0):
            requeststatecondition = FOIOpenInformationRequests.getfilterforrequeststate(params, includeclosed)
            filtercondition.append(requeststatecondition['condition'])
            includeclosed = requeststatecondition['includeclosed']
        # else:
        #     filtercondition.append(FOIMinistryRequest.requeststatuslabel != StateName.unopened.name)  #not return Unopened by default
        
        if(len(params['requeststatus']) == 1):
            requeststatuscondition = FOIOpenInformationRequests.getfilterforrequeststatus(params)
            filtercondition.append(requeststatuscondition)

            # return all except closed
            if(includeclosed == False):
                filtercondition.append(FOIMinistryRequest.requeststatuslabel != StateName.closed.name)
        elif(len(params['requeststatus']) > 1 and includeclosed == False):
            # return all except closed
            filtercondition.append(FOIMinistryRequest.requeststatuslabel != StateName.closed.name)
        
        #request type: personal, general
        if(len(params['requesttype']) > 0):
            requesttypecondition = FOIOpenInformationRequests.getfilterforrequesttype(params)
            filtercondition.append(or_(*requesttypecondition))

        #request flags: restricted, oipc, phased
        if(len(params['requestflags']) > 0):
            requestflagscondition = FOIOpenInformationRequests.getfilterforrequestflags(params)
            filtercondition.append(or_(*requestflagscondition))
        
        #public body: EDUC, etc.
        if(len(params['publicbody']) > 0):
            ministrycondition = FOIOpenInformationRequests.getfilterforpublicbody(params)
            filtercondition.append(ministrycondition)

        #axis request #, raw request #, applicant name, assignee name, request description, subject code
        if(len(params['keywords']) > 0 and params['search'] is not None):
            searchcondition = FOIOpenInformationRequests.getfilterforsearch(params)
            filtercondition.append(searchcondition)

        if(params['daterangetype'] is not None):
            filterconditionfordate = FOIOpenInformationRequests.getfilterfordate(params)
            filtercondition += filterconditionfordate

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
    def getfilterforrequeststatus(cls, params):        
        #request status: overdue || on time
        if(params['requeststatus'][0] == 'overdue'):
            #exclude "on hold" for overdue
            # statelabel = StateName.onhold.name
            return and_(FOIOpenInformationRequests.findfield('duedate') < datetime.now().date(), and_(FOIMinistryRequest.requeststatuslabel != StateName.onhold.name, FOIMinistryRequest.requeststatuslabel != StateName.onholdother.name))
        else:
            return FOIOpenInformationRequests.findfield('duedate') >= datetime.now().date()
    
    @classmethod
    def getfilterforrequesttype(cls, params):  
        #request type: personal, general
        requesttypecondition = []
        for request_type in params['requesttype']:
            requesttypecondition.append(FOIRequest.requesttype == request_type)
        return requesttypecondition

    @classmethod
    def getfilterforrequestflags(cls, params):
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
                requestflagscondition.append(FOIOpenInformationRequests.findfield('isoipcreview') == True)
            if (flag.lower() == 'phased'):
                continue
        return or_(*requestflagscondition)

    @classmethod
    def getfilterforpublicbody(cls, params):
        #public body: EDUC, etc.
        publicbodycondition = []
        for ministry in params['publicbody']:
            publicbodycondition.append(FOIOpenInformationRequests.findfield('ministry') == ministry)
        return or_(*publicbodycondition)

    @classmethod
    def getfilterforsearch(cls, params):
        #axis request #, raw request #, applicant name, assignee name, request description, subject code
        if(params['search'] == 'requestdescription'):
            return FOIOpenInformationRequests.__getfilterfordescription(params)
        elif(params['search'] == 'applicantname'):
            return FOIOpenInformationRequests.__getfilterforapplicantname(params)
        elif(params['search'] == 'assigneename'):
            return FOIOpenInformationRequests.__getfilterforassigneename(params)
        elif(params['search'] == 'idnumber'):
            return FOIOpenInformationRequests.__getfilterforidnumber(params)
        elif(params['search'] == 'axisrequest_number'):
            return FOIOpenInformationRequests.__getfilterforaxisnumber(params)
        else:
            searchcondition = []
            for keyword in params['keywords']:
                searchcondition.append(FOIOpenInformationRequests.findfield(params['search']).ilike('%'+keyword+'%'))
            return and_(*searchcondition)
    
    @classmethod
    def __getfilterfordescription(cls,params):
        searchcondition1 = []
        searchcondition2 = []
        for keyword in params['keywords']:
            searchcondition1.append(FOIOpenInformationRequests.findfield('description').ilike('%'+keyword+'%'))
            #searchcondition2.append(FOIOpenInformationRequests.findfield('descriptionDescription').ilike('%'+keyword+'%'))
        #return or_(and_(*searchcondition1), and_(*searchcondition2))   
        return or_(and_(*searchcondition1))   

    @classmethod
    def __getfilterforapplicantname(cls,params):
        searchcondition1 = []
        searchcondition2 = []
        searchcondition3 = []
        searchcondition4 = []
        for keyword in params['keywords']:
            searchcondition1.append(FOIOpenInformationRequests.findfield('firstName').ilike('%'+keyword+'%'))
            searchcondition2.append(FOIOpenInformationRequests.findfield('lastName').ilike('%'+keyword+'%'))
            # searchcondition3.append(FOIOpenInformationRequests.findfield('contactFirstName').ilike('%'+keyword+'%'))
            # searchcondition4.append(FOIOpenInformationRequests.findfield('contactLastName').ilike('%'+keyword+'%'))
        #return or_(and_(*searchcondition1), and_(*searchcondition2), and_(*searchcondition3), and_(*searchcondition4))
        return or_(and_(*searchcondition1), and_(*searchcondition2)) 

    @classmethod        
    def __getfilterforassigneename(cls,params):
        searchcondition1 = []
        searchcondition2 = []
        searchcondition3 = []
        for keyword in params['keywords']:
            searchcondition1.append(FOIOpenInformationRequests.findfield('assignedToFirstName').ilike('%'+keyword+'%'))
            searchcondition2.append(FOIOpenInformationRequests.findfield('assignedToLastName').ilike('%'+keyword+'%'))
            searchcondition3.append(FOIMinistryRequest.assignedgroup.ilike('%'+keyword+'%'))
        return or_(and_(*searchcondition1), and_(*searchcondition2), and_(*searchcondition3))

    @classmethod
    def __getfilterforidnumber(cls,params):
        searchcondition = []
        for keyword in params['keywords']:
            keyword = keyword.lower()
            keyword = keyword.replace('u-00', '')
            searchcondition.append(cls.idNumber.ilike('%'+keyword+'%'))
        return and_(*searchcondition)
    
    @classmethod
    def __getfilterforaxisnumber(cls,params):
        searchcondition1 = []
        searchcondition2 = []
        for keyword in params['keywords']:
            keyword = keyword.lower()
            keyword = keyword.replace('u-00', '')
            searchcondition1.append(cls.idNumber.ilike('%'+keyword+'%'))
            searchcondition2.append(cls.axisRequestId.ilike('%'+keyword+'%'))
        return or_(and_(*searchcondition1), and_(*searchcondition2))

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
                            and_(cls.receiveddate.is_(None), FOIOpenInformationRequests.created_at.cast(Date) >= parser.parse(params['fromdate'])),
                            and_(cls.receiveddate.isnot(None), FOIOpenInformationRequests.findfield(params['daterangetype']).cast(Date) >= parser.parse(params['fromdate'])),
                        )
                    )
                else:
                    filterconditionfordate.append(FOIRawRequest.findfield(params['daterangetype']).cast(Date) >= parser.parse(params['fromdate']))

            if(params['todate'] is not None):
                if(params['daterangetype'] == 'receivedDate'):
                    #online form submission has no receivedDate in json - using created_at
                    filterconditionfordate.append(
                        or_(
                            and_(cls.receiveddate.is_(None), FOIOpenInformationRequests.created_at.cast(Date) <= parser.parse(params['todate'])),
                            and_(cls.receiveddate.isnot(None), FOIOpenInformationRequests.findfield(params['daterangetype']).cast(Date) <= parser.parse(params['todate'])),
                        )
                    )
                else:
                    filterconditionfordate.append(FOIOpenInformationRequests.findfield(params['daterangetype']).cast(Date) <= parser.parse(params['todate']))

        return filterconditionfordate



class FOIOpenInfoRequestSchema(ma.Schema):
    class Meta:
        fields = (
            'foiopeninforequestid', 'version', 'foiministryrequest_id', 'foiministryrequestversion_id', 'oipublicationstatus_id', 'oiexemption_id', 'oiassignedto',
            'oiexemptionapproved', 'copyrightsevered', 'pagereference', 'iaorationale', 'oifeedback', 'publicationdate', 'created_at', 'updated_at', 'createdby', 'updatedby',
            "oiexemptiondate"
        )