from flask.app import Flask
from sqlalchemy.sql.schema import ForeignKey, ForeignKeyConstraint
from .db import  db, ma
from datetime import datetime
from sqlalchemy.orm import relationship, backref, aliased
from sqlalchemy import or_, and_, text, func, literal, cast, case, nullslast, nullsfirst, desc, asc
from sqlalchemy.sql.sqltypes import String
from sqlalchemy.sql.sqltypes import Date, Integer
from request_api.models.default_method_result import DefaultMethodResult
from sqlalchemy import text
from datetime import datetime as datetime2
import logging
from request_api.utils.enums import StateName, IAOTeamWithKeycloackGroup, OICloseReason, ExcludedProgramArea, OIStatusEnum
# from .FOIMinistryRequests import FOIMinistryRequest
from .FOIAssignees import FOIAssignee
from .FOIRequests import FOIRequest
from .FOIRequestStatus import FOIRequestStatus
from .ApplicantCategories import ApplicantCategory
from .FOIRequestWatchers import FOIRequestWatcher
from .FOIRequestStatus import FOIRequestStatus
from .FOIMinistryRequestSubjectCodes import FOIMinistryRequestSubjectCode
from .SubjectCodes import SubjectCode
from .ProactiveDisclosureCategories import ProactiveDisclosureCategory




class FOIProactiveDisclosureRequests(db.Model):
    __tablename__ = "FOIProactiveDisclosureRequests"
    # Defining the columns
    proactivedisclosureid = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    #version = db.Column(db.Integer, primary_key=True, nullable=False)
    foiministryrequest_id = db.Column(db.Integer, ForeignKey('FOIMinistryRequests.foiministryrequestid'), nullable=False)
    foiministryrequestversion_id = db.Column(db.Integer, ForeignKey('FOIMinistryRequests.version'), nullable=False)
    proactivedisclosurecategoryid = db.Column(db.Integer,ForeignKey('ProactiveDisclosureCategories.proactivedisclosurecategoryid')) 
    proactivedisclosurecategory =  relationship("ProactiveDisclosureCategory",backref=backref("ProactiveDisclosureCategories"),uselist=False)
    reportperiod = db.Column(db.String, nullable=True)
    publicationdate = db.Column(db.DateTime, nullable=True)
    #receiveddate = db.Column(db.DateTime, nullable=True)
    #isactive = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=True)
    createdby = db.Column(db.String(120), nullable=False)
    updatedby = db.Column(db.String(120), nullable=True)


    @classmethod
    def getproactiverequestbyministryrequestid(cls,ministryrequestid, ministryversion):
        request_schema = FOIProactiveDisclosureRequestSchema()
        query = db.session.query(FOIProactiveDisclosureRequests).filter_by(foiministryrequest_id=ministryrequestid , foiministryrequestversion_id = ministryversion).order_by(FOIProactiveDisclosureRequests.foiministryrequestversion_id.desc()).first()
        return request_schema.dump(query) 

    @classmethod
    def getcurrentfoiproactiverequest(cls, foiministryrequestid)->DefaultMethodResult:
        try:
            request_schema = FOIProactiveDisclosureRequestSchema()
            query = db.session.query(FOIProactiveDisclosureRequests).filter_by(foiministryrequest_id=foiministryrequestid).order_by(FOIProactiveDisclosureRequests.foiministryrequestversion_id.desc()).first()
            return request_schema.dump(query)
        except Exception as exception:
            logging.error(f"Error: {exception}")
                
    # @classmethod
    # def getrequestssubquery(cls, groups, filterfields, keyword, additionalfilter, userid, iaoassignee, ministryassignee, requestby, 
    #                         isiaorestrictedfilemanager=False, isministryrestrictedfilemanager=False):
    #     pdbasequery = cls.getpdbasequery(additionalfilter, userid, isiaorestrictedfilemanager, groups, isadvancedsearch=False)
    #     if len(filterfields) > 0 and keyword is not None:
    #         filtercondition = cls.getfilterforrequestssubquery(filterfields, keyword)
    #         return pdbasequery.filter(filtercondition)
    #     else:
    #         return pdbasequery  
        
    # @classmethod
    # def getfilterforrequestssubquery(cls, filterfields, keyword):
    #     _keywords = []
    #     if(keyword is not None):
    #         _keywords = keyword.lower().replace(",", " ").split()

    #     #filter/search
    #     filtercondition = []
    #     for _keyword in _keywords:
    #         onekeywordfiltercondition = []
    #         #if(_keyword != 'restricted'):
    #         for field in filterfields:
    #             if(field == 'idNumber'):
    #                 _keyword = _keyword.replace('u-00', '')
    #             field_value = cls.findfield(field)
    #             condition = field_value.ilike('%'+_keyword+'%')
    #             onekeywordfiltercondition.append(condition)            
    #         # else:
    #         #     filtercondition.append(FOIRestrictedMinistryRequest.isrestricted == True)

    #         if onekeywordfiltercondition:
    #             filtercondition.append(or_(*onekeywordfiltercondition))
    #         elif _keyword != 'restricted':  
    #             filtercondition.append(literal(False))

    #     return and_(*filtercondition)

        
    # @classmethod
    # def getpdbasequery(cls, additionalfilter=None, userid=None, isiaorestrictedfilemanager=False, groups=[], isadvancedsearch=False):
    #     from .FOIMinistryRequests import FOIMinistryRequest
    #     _session = db.session
    #     # subquery for getting the latest version of FOIProactiveDisclosureRequests
    #     latest_proactive_subq = (
    #         _session.query(
    #             FOIProactiveDisclosureRequests.foiministryrequest_id,
    #             func.max(FOIProactiveDisclosureRequests.foiministryrequestversion_id).label("max_version")
    #         )
    #         .group_by(FOIProactiveDisclosureRequests.foiministryrequest_id)
    #         .subquery()
    #     )
    #     # joincondition = [
    #     #     subquery_maxversion.c.foiopeninforequestid == FOIOpenInformationRequests.foiopeninforequestid,
    #     #     subquery_maxversion.c.max_version == FOIOpenInformationRequests.version,
    #     #     FOIOpenInformationRequests.isactive == True
    #     # ]

    #     recordspagecount = case ([
    #         (FOIMinistryRequest.recordspagecount.isnot(None), FOIMinistryRequest.recordspagecount)
    #         ],
    #         else_= literal("0").label("recordspagecount")
    #     )

    #     # oistatusname = case(
    #     #     [(FOIMinistryRequest.oistatus_id.is_(None), literal('unopened'))],
    #     #     else_=OpenInformationStatuses.name
    #     # ).label('oiStatusName')
    #     assignedtoformatted = case(
    #         (
    #             and_(
    #                 FOIAssignee.lastname.isnot(None),
    #                 FOIAssignee.firstname.isnot(None)
    #             ),
    #             func.concat(FOIAssignee.lastname, ', ', FOIAssignee.firstname)
    #         ),
    #         (
    #             and_(
    #                 FOIAssignee.lastname.isnot(None),
    #                 FOIAssignee.firstname.is_(None)
    #             ),
    #             FOIAssignee.lastname
    #         ),
    #         (
    #             and_(
    #                 FOIAssignee.lastname.is_(None),
    #                 FOIAssignee.firstname.isnot(None)
    #             ),
    #             FOIAssignee.firstname
    #         ),
    #         else_=''
    #     ).label('assignedtoformatted')

    #     #oifilter = cls.getgroupfilters(groups)
    #     excluded_program_areas = ExcludedProgramArea.list()
    #     eligible_close_reasons = OICloseReason.list()
    #     selectedcolumns = [
    #         FOIRequest.foirequestid.label('id'), 
    #         FOIMinistryRequest.foiministryrequestid.label('ministryrequestid'), 
    #         cast(FOIMinistryRequest.axisrequestid, String).label('axisRequestId'),
    #         FOIMinistryRequest.closedate, 
    #         FOIRequest.requesttype.label('requestType'), 
    #         cast(FOIMinistryRequest.filenumber, String).label('idNumber'),
    #         ApplicantCategory.name.label('applicantcategory'),
    #         recordspagecount.label('recordspagecount'),  
    #         #oistatusname.label('oiStatusName'),
    #         cls.receiveddate.label('receivedDate'),
    #         cls.publicationdate,
    #         cls.created_at, 
    #         assignedtoformatted, 
    #         cls.version,
    #         #cls.foiopeninforequestid,
    #         FOIRequestStatus.name.label('currentState'),
    #         #FOIRestrictedMinistryRequest.isrestricted.label('isiaorestricted'),
    #         SubjectCode.name.label('subjectcode'),
    #         FOIMinistryRequest.closedate
    #     ]   
    #     basequery = (
    #         _session.query(*selectedcolumns)
    #         .join(
    #             latest_proactive_subq,
    #             latest_proactive_subq.c.foiministryrequest_id == FOIMinistryRequest.foiministryrequestid
    #         )
    #         .join(
    #             FOIProactiveDisclosureRequests,
    #             and_(
    #                 FOIProactiveDisclosureRequests.foiministryrequest_id == latest_proactive_subq.c.foiministryrequest_id,
    #                 FOIProactiveDisclosureRequests.foiministryrequestversion_id == latest_proactive_subq.c.max_version
    #             )
    #         )
    #         .join(
    #             ProactiveDisclosureCategory,
    #             ProactiveDisclosureCategory.proactivedisclosurecategoryid ==
    #             FOIProactiveDisclosureRequests.proactivedisclosurecategoryid
    #         )
    #         .join(FOIMinistryRequest, and_(
    #             FOIMinistryRequest.foiministryrequestid == cls.foiministryrequest_id, 
    #             FOIMinistryRequest.isactive == True,
    #         ))
    #         .join(FOIRequest, and_(FOIRequest.foirequestid == FOIMinistryRequest.foirequest_id, FOIRequest.version == FOIMinistryRequest.foirequestversion_id, FOIRequest.requesttype != 'personal'))
    #         .join(ApplicantCategory,and_(ApplicantCategory.applicantcategoryid == FOIRequest.applicantcategoryid, ApplicantCategory.isactive == True))
    #         #.outerjoin(OpenInformationStatuses, OpenInformationStatuses.oistatusid == FOIMinistryRequest.oistatus_id)
    #         .join(FOIRequestStatus, FOIRequestStatus.requeststatusid == FOIMinistryRequest.requeststatusid)
    #         # .join(FOIRestrictedMinistryRequest,
    #         #                     and_(
    #         #                         FOIRestrictedMinistryRequest.ministryrequestid == FOIMinistryRequest.foiministryrequestid,
    #         #                         FOIRestrictedMinistryRequest.type == 'iao',
    #         #                         FOIRestrictedMinistryRequest.isactive == True),
    #         #                     isouter=True
    #         #)
    #     .outerjoin(FOIAssignee, FOIAssignee.username == cls.oiassignedto)
    #         .outerjoin(FOIMinistryRequestSubjectCode, 
    #             and_(
    #                 FOIMinistryRequestSubjectCode.foiministryrequestid == FOIMinistryRequest.foiministryrequestid, FOIMinistryRequestSubjectCode.foiministryrequestversion == FOIMinistryRequest.version
    #             )
    #         )
    #         .join(
    #               SubjectCode,
    #               SubjectCode.subjectcodeid == FOIMinistryRequestSubjectCode.subjectcodeid,
    #               isouter=True
    #              )
    #     )
    #     if not isadvancedsearch:
    #         basequery = basequery.filter(
    #             FOIMinistryRequest.programareaid.notin_(excluded_program_areas),
    #             or_( 
    #                 and_(
    #                     FOIMinistryRequest.oistatus_id.isnot(None),
    #                     FOIMinistryRequest.oistatus_id != OIStatusEnum.PUBLISHED.value,                        
    #                     FOIMinistryRequest.oistatus_id != OIStatusEnum.DO_NOT_PUBLISH.value
    #                 ),
    #                 and_(
    #                     FOIMinistryRequest.oistatus_id.is_(None),
    #                     FOIMinistryRequest.requeststatuslabel == StateName.closed.name,
    #                     FOIMinistryRequest.closereasonid.in_(eligible_close_reasons)
    #                 )
    #             )
    #         )
    #     if additionalfilter == 'watchingRequests':
    #         subquery_watchby = FOIRequestWatcher.getrequestidsbyuserid(userid)
    #         basequery = basequery.join(
    #             subquery_watchby, 
    #             subquery_watchby.c.ministryrequestid == FOIMinistryRequest.foiministryrequestid
    #         )
    #     elif additionalfilter == 'myRequests':
    #         basequery = basequery.filter(
    #             and_(
    #                 cls.oiassignedto == userid
    #             )
    #         )
    #     elif additionalfilter == 'unassignedRequests':
    #         basequery = basequery.filter(
    #                 cls.oiassignedto.is_(None),                         
    #         )
    #     elif additionalfilter is not None and additionalfilter.lower() == 'all':
    #         basequery = basequery.filter(cls.oiassignedto != None)
    #     return basequery



class FOIProactiveDisclosureRequestSchema(ma.Schema):
    class Meta:
        fields = (
            'proactivedisclosureid', 'foiministryrequest_id', 'foiministryrequestversion_id',
            'proactivedisclosurecategory.proactivedisclosurecategoryid','proactivedisclosurecategory.name','reportperiod',
            'publicationdate', 'created_at', 'updated_at', 'createdby', 'updatedby',
        )