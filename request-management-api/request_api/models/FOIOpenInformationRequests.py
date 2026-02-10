from flask.app import Flask
from sqlalchemy.sql.schema import ForeignKey, ForeignKeyConstraint
from .db import  db, ma
from datetime import datetime
from sqlalchemy.orm import relationship, backref, aliased
from sqlalchemy import or_, and_, text, func, literal, cast, case, nullslast, nullsfirst, desc, asc, literal_column
from sqlalchemy.sql.sqltypes import String
from sqlalchemy.sql.sqltypes import Date, Integer
from request_api.utils.enums import StateName, IAOTeamWithKeycloackGroup, OICloseReason, ExcludedProgramArea, OIStatusEnum
from .FOIMinistryRequests import FOIMinistryRequest
from .FOIAssignees import FOIAssignee
from .FOIRequests import FOIRequest
from .FOIRequestApplicantMappings import FOIRequestApplicantMapping
from .FOIRequestApplicants import FOIRequestApplicant
from .FOIRequestStatus import FOIRequestStatus
from .ApplicantCategories import ApplicantCategory
from .FOIRequestWatchers import FOIRequestWatcher
from .FOIRestrictedMinistryRequests import FOIRestrictedMinistryRequest
from .ProgramAreas import ProgramArea
from .OpenInformationStatuses import OpenInformationStatuses
from .FOIRequestStatus import FOIRequestStatus
from .FOIMinistryRequestSubjectCodes import FOIMinistryRequestSubjectCode
from .SubjectCodes import SubjectCode
from .FOIRequestOIPC import FOIRequestOIPC
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
    receiveddate = db.Column(db.DateTime, nullable=True)
    isactive = db.Column(db.Boolean, nullable=False)
    copyrightsevered = db.Column(db.Boolean, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=True)
    createdby = db.Column(db.String(120), nullable=False)
    updatedby = db.Column(db.String(120), nullable=True)
    processingstatus = db.Column(db.String(120), nullable=True)
    processingmessage = db.Column(db.String(250), nullable=True)
    sitemap_pages = db.Column(db.String(120), nullable=True)

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
                oiexemption_id=foiopeninforequest.get("oiexemption_id"),
                iaorationale=foiopeninforequest.get("iaorationale"),
                pagereference=foiopeninforequest.get("pagereference"),
                oiassignedto=foiopeninforequest.get("oiassignedto"),
                oiexemptionapproved=foiopeninforequest.get("oiexemptionapproved"),
                oifeedback=foiopeninforequest.get("oifeedback"),
                publicationdate=foiopeninforequest.get("publicationdate"),
                receiveddate=foiopeninforequest.get("receiveddate"),
                copyrightsevered=foiopeninforequest.get("copyrightsevered"),
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
    
    def saveopeninfo(cls, foiopeninforequest, userid)->DefaultMethodResult:
        try:
            query = db.session.query(FOIOpenInformationRequests)
            openinfo = cls.getcurrentfoiopeninforequest(foiopeninforequest['foiministryrequest_id'])
            if openinfo:
                createddate = datetime2.now().isoformat()
                updated_foiopeninforequest = FOIOpenInformationRequests(
                    foiopeninforequestid=openinfo['foiopeninforequestid'],
                    version=openinfo['version']+1,
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
                    receiveddate=foiopeninforequest["receiveddate"],
                    copyrightsevered=foiopeninforequest["copyrightsevered"],
                    isactive=True,
                    created_at=createddate,
                    createdby=userid,
                    sitemap_pages=openinfo["sitemap_pages"]
                )
                db.session.add(updated_foiopeninforequest)
                db.session.commit()
                return DefaultMethodResult(True, "FOIOpenInfo request version updated", updated_foiopeninforequest.foiopeninforequestid)
            else:
                return cls.createopeninfo(foiopeninforequest, userid)
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
    def getoibasequery(cls, additionalfilter=None, userid=None, isiaorestrictedfilemanager=False, groups=[], isadvancedsearch=False):
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

        recordspagecount = case ([
            (FOIMinistryRequest.recordspagecount.isnot(None), FOIMinistryRequest.recordspagecount)
            ],
            else_= literal("0").label("recordspagecount")
        )

        oistatusname = case(
            [(FOIMinistryRequest.oistatus_id.is_(None), literal('unopened'))],
            else_=OpenInformationStatuses.name
        ).label('oiStatusName')

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
            cls.receiveddate.label('receivedDate'),
            cls.publicationdate,
            cls.created_at, 
            assignedToFormatted.label('assignedToFormatted'), 
            FOIMinistryRequest.oistatus_id.label('oistatus_id'),
            cls.version,
            cls.foiopeninforequestid.label('foiopeninforequestid'),
            FOIRequestStatus.name.label('currentState'),
            FOIRestrictedMinistryRequest.isrestricted.label('isiaorestricted'),
            SubjectCode.name.label('subjectcode'),
            FOIMinistryRequest.closedate,
            FOIMinistryRequest.cfrduedate,
            literal(None).label('proactivedisclosurecategory'),
        ]   

        basequery = (
            _session.query(*selectedcolumns)
            .join(subquery_maxversion, and_(*joincondition))
            .join(FOIMinistryRequest, and_(
                FOIMinistryRequest.foiministryrequestid == cls.foiministryrequest_id, 
                FOIMinistryRequest.isactive == True,
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
            .outerjoin(FOIMinistryRequestSubjectCode, 
                and_(
                    FOIMinistryRequestSubjectCode.foiministryrequestid == FOIMinistryRequest.foiministryrequestid, FOIMinistryRequestSubjectCode.foiministryrequestversion == FOIMinistryRequest.version
                )
            )
            .join(
                  SubjectCode,
                  SubjectCode.subjectcodeid == FOIMinistryRequestSubjectCode.subjectcodeid,
                  isouter=True
                 )
        )

        if not isadvancedsearch:
            basequery = basequery.filter(
                FOIMinistryRequest.programareaid.notin_(excluded_program_areas),
                or_( 
                    and_(
                        FOIMinistryRequest.oistatus_id.isnot(None),
                        FOIMinistryRequest.oistatus_id != OIStatusEnum.PUBLISHED.value,                        
                        FOIMinistryRequest.oistatus_id != OIStatusEnum.DO_NOT_PUBLISH.value
                    ),
                    and_(
                        FOIMinistryRequest.oistatus_id.is_(None),
                        FOIMinistryRequest.requeststatuslabel == StateName.closed.name,
                        FOIMinistryRequest.closereasonid.in_(eligible_close_reasons)
                    )
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

        elif additionalfilter is not None and additionalfilter.lower() == 'all':
            basequery = basequery.filter(cls.oiassignedto != None)
        
        return basequery

    @classmethod
    def getrequestssubquery(cls, groups, filterfields, keyword, additionalfilter, userid, iaoassignee, ministryassignee, requestby, isiaorestrictedfilemanager=False, isministryrestrictedfilemanager=False):
        oibasequery = cls.getoibasequery(additionalfilter, userid, isiaorestrictedfilemanager, groups, isadvancedsearch=False)
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
    def getsorting(cls, sortingitems, sortingorders, isunion=False):
        sortingcondition = []
        if len(sortingitems) > 0 and len(sortingorders) > 0 and len(sortingitems) == len(sortingorders):
            for field in sortingitems:
                if cls.validatefield(field):
                    order = sortingorders.pop(0)
                    sortfield = cls.findsortfield(field) if isunion else cls.findfield(field)
                    if order == 'desc':
                        sortingcondition.append(nullslast(desc(sortfield)))
                    else:
                        sortingcondition.append(nullsfirst(asc(sortfield)))
        
        #default sorting
        if(len(sortingcondition) == 0):
            default_sort = cls.findsortfield('defaultSorting') if isunion else cls.findfield('defaultSorting')

            sortingcondition.append(default_sort)
            sortingcondition.append(cls.findsortfield('receivedDate').desc() if isunion else cls.findfield('receivedDate').desc())
        
        return sortingcondition

    @classmethod
    def validatefield(cls, field):
        valid_fields = ['receivedDate', 'axisRequestId', 'requestType', 'recordspagecount', 
                        'publicationStatus', 'closedDate', 'publicationDate', 'assignedTo', 'applicantType']
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

        defaultsorting = case(
                [(FOIMinistryRequest.oistatus_id == OIStatusEnum.EXEMPTION_REQUEST.value, 0)],
                else_=1
            )

        if field == 'receivedDateUF':
            return FOIRequest.receiveddate
        elif field == 'receivedDate':
            return cls.receiveddate
        elif field == 'defaultSorting':      
            return defaultsorting
        elif field == 'requestType':
            return FOIRequest.requesttype
        elif field == 'pageCount':
            return FOIMinistryRequest.recordspagecount
        elif field == 'recordspagecount':
            return cast(FOIMinistryRequest.recordspagecount, Integer)   
        elif field == 'publicationStatus':
            return cast(
                case(
                    [(FOIMinistryRequest.oistatus_id.is_(None), literal('unopened'))],
                    else_=OpenInformationStatuses.name
                ),
                String
            )
        elif (field == 'closedDate' or field == 'from_closed'):
            return FOIMinistryRequest.closedate
        elif field == 'applicantType':
            return ApplicantCategory.name
        elif (field == 'publicationdate' or field == 'publicationDate'):
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
        elif field == 'assignedTo':
            return FOIAssignee.lastname
        elif field == 'idNumber':
            return cast(FOIMinistryRequest.filenumber, String)
        elif field == 'axisRequestId':
            return cast(FOIMinistryRequest.axisrequestid, String)
        elif field == 'currentState':   
            return FOIRequestStatus.name
        elif field == 'subjectcode':
            return SubjectCode.name
        else:
            return text(field)

    @classmethod
    def findsortfield(cls, field):

        defaultsorting = case(
                [(literal_column('oistatus_id') == OIStatusEnum.EXEMPTION_REQUEST.value, 0)],
                else_=1
            )

        if field == 'receivedDateUF':
            return literal_column('"receivedDate"')
        elif field == 'receivedDate':
            return literal_column('"receivedDate"')
        elif field == 'defaultSorting':      
            return defaultsorting
        elif field == 'requestType':
            return literal_column('"requestType"')
        elif field == 'pageCount':
            return literal_column('recordspagecount')
        elif field == 'recordspagecount':
            return literal_column('recordspagecount')
        elif field == 'publicationStatus':
            return literal_column('"oiStatusName"')
        elif (field == 'closedDate' or field == 'from_closed'):
            return literal_column('closedate')
        elif field == 'applicantType':
            return literal_column('applicantcategory')
        elif (field == 'publicationdate' or field == 'publicationDate'):
            return literal_column('publicationdate')
        elif field == 'assignee':
            return literal_column('"assignedToFormatted"')
        elif field == 'assignedTo':
            return literal_column('"assignedToFormatted"')
        elif field == 'idNumber':
            return literal_column('"idNumber"')
        elif field == 'axisRequestId':
            return literal_column('"axisRequestId"')
        elif field == 'currentState':   
            return literal_column('currentState')
        elif field == 'subjectcode':
            return literal_column('subjectcode')
        else:
            return literal_column(field)

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
                    if(field == 'idNumber'):
                        _keyword = _keyword.replace('u-00', '')
                    field_value = cls.findfield(field)
                    condition = field_value.ilike('%'+_keyword+'%')
                    onekeywordfiltercondition.append(condition)            
            else:
                filtercondition.append(FOIRestrictedMinistryRequest.isrestricted == True)

            if onekeywordfiltercondition:
                filtercondition.append(or_(*onekeywordfiltercondition))
            elif _keyword != 'restricted':  
                filtercondition.append(literal(False))

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
    def advancedsearch(cls, params, userid, isiaorestrictedfilemanager=False):
        basequery = FOIOpenInformationRequests.getoibasequery(None, userid, isiaorestrictedfilemanager,isadvancedsearch=True)
        #filter/search
        filtercondition = FOIOpenInformationRequests.getfilterforadvancedsearch(params)
        searchquery = basequery.filter(and_(*filtercondition))

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
        iaoassignee = aliased(FOIAssignee)
        ministryassignee = aliased(FOIAssignee)

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
        return requestflagscondition

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
        elif(params['search'] == 'subjectcode'):
            return FOIOpenInformationRequests.__getfilterforsubjectcode(params)
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
                searchcondition.append(FOIOpenInformationRequests.findfield(params['search']).ilike('%'+keyword+'%'))
            return and_(*searchcondition)
    
    @classmethod
    def __getfilterfordescription(cls,params):
        searchcondition1 = []
        searchcondition2 = []
        for keyword in params['keywords']:
            searchcondition1.append(FOIOpenInformationRequests.findfield('description').ilike('%'+keyword+'%'))
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
        return or_(and_(*searchcondition1), and_(*searchcondition2)) 

    @classmethod        
    def __getfilterforassigneename(cls,params):
        searchcondition1 = []
        searchcondition2 = []
        searchcondition3 = []
        for keyword in params['keywords']:
            searchcondition1.append(FOIOpenInformationRequests.findfield('assignedToFirstName').ilike('%'+keyword+'%'))
            searchcondition2.append(FOIOpenInformationRequests.findfield('assignedToLastName').ilike('%'+keyword+'%'))
        return or_(and_(*searchcondition1), and_(*searchcondition2))

    @classmethod
    def __getfilterforidnumber(cls,params):
        searchcondition1 = []
        searchcondition2 = []
        for keyword in params['keywords']:
            keyword = keyword.lower()
            keyword = keyword.replace('u-00', '')
            searchcondition1.append(FOIOpenInformationRequests.findfield('idNumber').ilike('%'+keyword+'%'))
            searchcondition2.append(FOIOpenInformationRequests.findfield('axisRequestId').ilike('%'+keyword+'%'))
        return or_(and_(*searchcondition1), and_(*searchcondition2))
    
    @classmethod
    def __getfilterforaxisnumber(cls,params):
        searchcondition1 = []
        searchcondition2 = []
        for keyword in params['keywords']:
            keyword = keyword.lower()
            keyword = keyword.replace('u-00', '')
            searchcondition1.append(FOIOpenInformationRequests.findfield('idNumber').ilike('%'+keyword+'%'))
            searchcondition2.append(FOIOpenInformationRequests.findfield('axisRequestId').ilike('%'+keyword+'%'))
        return or_(and_(*searchcondition1), and_(*searchcondition2))

    @classmethod
    def __getfilterforsubjectcode(cls,params):
        searchcondition1 = []
        for keyword in params['keywords']:
            searchcondition1.append(FOIOpenInformationRequests.findfield('subjectcode').ilike('%'+keyword+'%'))
        return or_(*searchcondition1)

    @classmethod
    def getfilterfordate(cls, params):
        filterconditionfordate = []
        if(params['daterangetype'] == 'closedate'):
            #no rawrequest returned for this case
            filterconditionfordate.append(FOIMinistryRequest.foirequest_id < 0)
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
                    filterconditionfordate.append(FOIOpenInformationRequests.findfield(params['daterangetype']).cast(Date) >= parser.parse(params['fromdate']))

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
            "receiveddate", 'processingstatus', 'processingmessage', 'sitemap_pages'
        )