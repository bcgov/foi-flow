from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import relationship
from .db import db, ma
from datetime import datetime as datetime2
from request_api.models.default_method_result import DefaultMethodResult
from sqlalchemy import or_, and_, text, func, literal, cast, case, nullslast, nullsfirst, desc, asc
from sqlalchemy.orm import relationship, backref, aliased
from sqlalchemy.sql.sqltypes import Date, Integer, String
import logging
from request_api.models.ProgramAreas import ProgramArea
from request_api.models.FOIRequestStatus import FOIRequestStatus
from request_api.models.FOIMinistryRequests import FOIMinistryRequestSchema, FOIMinistryRequest
from request_api.models.FOIAssignees import FOIAssignee

class FOIMinistryRequestConsults(db.Model):
    # Name of the table in our database
    __tablename__ = 'FOIMinistryRequestConsults'

    # Defining the columns
    foiministryrequestconsultid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    version = db.Column(db.Integer, primary_key=True, nullable=False)
    foiministryrequest_id = db.Column(db.Integer, ForeignKey('FOIMinistryRequests.foiministryrequestid'), nullable=False)
    foiministryrequestversion_id = db.Column(db.Integer, ForeignKey('FOIMinistryRequests.version'), nullable=False)
    filenumber = db.Column(db.String(50), nullable=False)
    consultassignedto = db.Column(db.String(120), ForeignKey('FOIAssignees.username'), nullable=True)
    assignedgroup = db.Column(db.String(120), nullable=True)
    assignedministryperson = db.Column(db.String(120), nullable=True)
    assignedministrygroup = db.Column(db.String(120), nullable=True)
    requeststatusid = db.Column(db.Integer,ForeignKey('FOIRequestStatuses.requeststatusid'))
    consulttypeid = db.Column(db.Integer, db.ForeignKey('FOIMinistryRequestConsultTypes.consulttypeid'), nullable=False)
    programareaid = db.Column(db.Integer, db.ForeignKey('ProgramAreas.programareaid'), nullable=True)
    consultsubjectcode = db.Column(db.String(20), nullable=True)
    consultduedate = db.Column(db.Date, nullable=False)
    closedate = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=True)
    createdby = db.Column(db.String(120), nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)
    updatedby = db.Column(db.String(120), nullable=True)
    isactive = db.Column(db.Boolean, nullable=False)
    

    @classmethod
    def createconsults(cls, data, userid, assigneedata):
        try:
            createddate = datetime2.now().isoformat()
            new_records = []
            consultassignedto = None
            assignedgroup = None
            ministryid = data[0].get('foiMinistryRequestId')

            _assginee = assigneedata if assigneedata not in (None,'') else None
            if _assginee not in (None,''):
                FOIAssignee.saveassignee(_assginee['assignee'], _assginee['assigneefirstname'],  _assginee.get('assigneeMiddlename', None), _assginee['assigneelastname'])
                consultassignedto = _assginee['assignee']
                assignedgroup = _assginee['assigneegroup']

            existing_consults = cls.getinternalconsults(ministryid)
            if existing_consults:
                new_version = cls.getnextconsultversion(ministryid)
                cls.archiveexistingconsults(ministryid, userid, new_version)
            else:
                new_version = 1

            # Create new consult records with the determined version
            for item in data:
                new_record = FOIMinistryRequestConsults(
                    version=new_version,
                    foiministryrequest_id=item.get('foiMinistryRequestId'),
                    foiministryrequestversion_id=item.get('foiMinistryRequestVersionId'),
                    filenumber=item.get('fileNumber'),
                    consultassignedto=consultassignedto,
                    assignedgroup=assignedgroup,
                    requeststatusid=item.get('requeststatusid'), 
                    consulttypeid=item.get('consultTypeId'),
                    programareaid=item.get('programAreaId'),
                    consultsubjectcode=item.get('subjectCode'),
                    consultduedate=item.get('dueDate'),
                    created_at=createddate,
                    createdby=userid,
                    isactive=True,
                )
                db.session.add(new_record)
                new_records.append(new_record)

            db.session.commit()
            return new_records

        except Exception as exception:
            logging.error(f"Error: {exception}")
            db.session.rollback()
            raise exception

    @classmethod
    def getnextconsultversion(cls, foiministryrequestid):
        max_version = db.session.query(
            db.func.max(FOIMinistryRequestConsults.version)
        ).filter_by(foiministryrequest_id=foiministryrequestid).scalar()
        return (max_version or 0) + 1
    
    @classmethod
    def archiveexistingconsults(cls, foiministryrequestid, userid, new_version):
        try:
            existing_consults = FOIMinistryRequestConsults.query.filter_by(
                foiministryrequest_id=foiministryrequestid,
                isactive=True
            ).all()

            archived_at = datetime2.now().isoformat()

            for consult in existing_consults:
                consult.isactive = False
                consult.updated_at = archived_at
                consult.updatedby = userid

                archived_copy = FOIMinistryRequestConsults(
                    version=new_version,
                    foiministryrequest_id=consult.foiministryrequest_id,
                    foiministryrequestversion_id=consult.foiministryrequestversion_id,
                    filenumber=consult.filenumber,
                    consultassignedto=consult.consultassignedto,
                    assignedgroup=consult.assignedgroup,
                    requeststatusid=consult.requeststatusid,
                    consulttypeid=consult.consulttypeid,
                    programareaid=consult.programareaid,
                    consultsubjectcode=consult.consultsubjectcode,
                    consultduedate=consult.consultduedate,
                    created_at=archived_at,
                    createdby=userid,
                    isactive=True
                )
                db.session.add(archived_copy)

        except Exception as exception:
            logging.error(f"Error archiving consults: {exception}")
            db.session.rollback()
            raise exception
    
    @classmethod
    def updateconsults(cls, data, userid, assigneedata):
        try:
            pass
        except Exception as exception:
            logging.error(f"Error: {exception}")
            db.session.rollback()
            raise exception
    
    @classmethod
    def getinternalconsults(cls, foiministryrequestid) -> DefaultMethodResult:
        try:
            latest_version = (db.session.query(func.max(FOIMinistryRequestConsults.version))
            .filter_by(foiministryrequest_id=foiministryrequestid).scalar())

            consults = (
                    db.session.query(FOIMinistryRequestConsults)
                    .filter_by(foiministryrequest_id=foiministryrequestid, version=latest_version, isactive=True)
                    .order_by(FOIMinistryRequestConsults.foiministryrequest_id.asc())
                    .all()
            )

            if not consults:
                return []
            
            enriched_consults = []
            for consult in consults:
                programarea = ProgramArea.getprogramareabyId(consult.programareaid) if consult.programareaid else None
                requeststatus = FOIRequestStatus.getrequeststatusbyId(consult.requeststatusid) if consult.requeststatusid else None

                enriched = {
                    "foiministryrequestconsultid": consult.foiministryrequestconsultid,
                    "filenumber": consult.filenumber,
                    "consultassignedto": consult.consultassignedto,
                    "assignedgroup": consult.assignedgroup,
                    "assignedministryperson": consult.assignedministryperson,
                    "assignedministrygroup": consult.assignedministrygroup,
                    "consulttypeid": consult.consulttypeid,
                    "programareaid": consult.programareaid,
                    "programareaname": programarea['name'] if programarea else None,
                    "requeststatusid": consult.requeststatusid,
                    "requeststatusname": requeststatus['name'] if requeststatus else None,
                    "consultsubjectcode": consult.consultsubjectcode,
                    "consultduedate": consult.consultduedate.isoformat() if consult.consultduedate else None,
                    "created_at": consult.created_at,
                    "createdby": consult.createdby
                }

                enriched_consults.append(enriched)

            return enriched_consults

        except Exception as exception:
            logging.error(f"Error: {exception}")
            return []
        
    
    @classmethod
    def getoriginalrequestDetailsByAxisRequestId(cls, axisrequestid):
        request_schema = FOIMinistryRequestSchema(many=False)
        query = db.session.query(FOIMinistryRequest).filter_by(axisrequestid=axisrequestid).order_by(FOIMinistryRequest.version.desc()).first()
        return request_schema.dump(query)
    
    @classmethod
    def get_sub_consults_by_ministry_ids(cls, ministry_ids: list[int]):
        _session = db.session

        iaoassignee = aliased(FOIAssignee)
        ministryassignee = aliased(FOIAssignee)

        subquery_max_version = (
        _session.query(
            FOIMinistryRequest.foiministryrequestid,
            func.max(FOIMinistryRequest.version).label("max_version")
        )
        .filter(FOIMinistryRequest.foiministryrequestid.in_(ministry_ids))
        .group_by(FOIMinistryRequest.foiministryrequestid)
        .subquery()
        )

        MinistryRequestLatest = aliased(FOIMinistryRequest)
        MinistryRequest = aliased(FOIMinistryRequest)

        axispagecount = case ([
            (FOIMinistryRequest.axispagecount.isnot(None), FOIMinistryRequest.axispagecount)
            ],
            else_= literal("0").label("axispagecount")
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
        
        consultAssignedToFormatted = case([
                            (and_(iaoassignee.lastname.isnot(None), iaoassignee.firstname.isnot(None)),
                             func.concat(iaoassignee.lastname, ', ', iaoassignee.firstname)),
                            (and_(iaoassignee.lastname.isnot(None), iaoassignee.firstname.is_(None)),
                             iaoassignee.lastname),
                            (and_(iaoassignee.lastname.is_(None), iaoassignee.firstname.isnot(None)),
                             iaoassignee.firstname),
                           ],
                           else_ = FOIMinistryRequest.assignedgroup).label('consultAssignedToFormatted')

        query = (
        _session.query(
            FOIMinistryRequestConsults.foiministryrequestconsultid.label("consultid"),
            FOIMinistryRequestConsults.foiministryrequest_id.label("foiministryrequestid"),
            FOIMinistryRequestConsults.foiministryrequestversion_id.label("foiministryrequestversionid"),
            FOIMinistryRequestConsults.requeststatusid.label("requeststatusid"),
            FOIMinistryRequestConsults.filenumber.label("filenumber"),
            cast(FOIMinistryRequestConsults.filenumber, String).label('axisRequestId'),
            FOIMinistryRequestConsults.consulttypeid,
            FOIMinistryRequestConsults.consultassignedto,
            FOIMinistryRequestConsults.consultduedate,
            FOIMinistryRequestConsults.isactive,
            FOIMinistryRequestConsults.created_at.label("receivedDate"),
            FOIRequestStatus.statuslabel.label('currentState'),
            MinistryRequest.foiministryrequestid.label("sub_foiministryrequestid"),
            MinistryRequest.description.label("sub_description"),
            MinistryRequest.duedate.label("sub_duedate"),
            MinistryRequest.axispagecount.label("sub_axispagecount"),
            MinistryRequest.filenumber.label("sub_idnumber"),
            requestpagecount.label("recordspagecount"),
            consultAssignedToFormatted,
        )
        .join(MinistryRequest, MinistryRequest.foiministryrequestid == FOIMinistryRequestConsults.foiministryrequestversion_id)
        .join(
            MinistryRequestLatest,
            (MinistryRequest.foiministryrequestid == MinistryRequestLatest.foiministryrequestid) &
            (MinistryRequest.version == MinistryRequestLatest.version)
        )
        .join(
            subquery_max_version,
            (MinistryRequestLatest.foiministryrequestid == subquery_max_version.c.foiministryrequestid) &
            (MinistryRequestLatest.version == subquery_max_version.c.max_version)
        )
        .join(FOIRequestStatus, FOIRequestStatus.requeststatusid == FOIMinistryRequestConsults.requeststatusid, isouter=True)
        .join(iaoassignee, iaoassignee.username == FOIMinistryRequestConsults.consultassignedto, isouter=True)
        .filter(FOIMinistryRequestConsults.foiministryrequestversion_id.in_(ministry_ids))
        .filter(FOIMinistryRequestConsults.isactive == True)
        )

        results = []
        for row in query.all():
            consult = {
                "consultid": row.consultid,
                "requeststatusid": row.requeststatusid,
                "filenumber": row.filenumber,
                "consulttypeid": row.consulttypeid,
                "consultassignedto": row.consultassignedto,
                "consultduedate": row.consultduedate,
                "foiministryrequestid": row.foiministryrequestid,
                "currentState": row.currentState,
                "consultAssignedToFormatted": row.consultAssignedToFormatted,
                "receivedDate": row.receivedDate,
                "foiministryrequest": {
                    "foiministryrequestid": row.sub_foiministryrequestid,
                    "description": row.sub_description,
                    "duedate": row.sub_duedate,
                    "axispagecount": row.sub_axispagecount,
                    "idnumber": row.sub_idnumber
                }
            }
            results.append(consult)
        return results
        
class FOIMinistryRequestConsultsSchema(ma.Schema):
    class Meta:
        fields = (
            'foiministryrequestconsultid',
            'version',
            'foiministryrequest_id',
            'foiministryrequestversion_id',
            'filenumber',
            'consultassignedto',
            'assignedgroup',
            'assignedministryperson',
            'assignedministrygroup',
            'requeststatusid',
            'consulttypeid',
            'programareaid',
            'consultsubjectcode',
            'consultduedate',
            'closedate',
            'created_at',
            'createdby',
            'updated_at',
            'updatedby',
            'isactive',
        )