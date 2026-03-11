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
    version = db.Column(db.Integer, primary_key=True, nullable=False)
    foiministryrequest_id = db.Column(db.Integer, ForeignKey('FOIMinistryRequests.foiministryrequestid'), nullable=False)
    foiministryrequestversion_id = db.Column(db.Integer, ForeignKey('FOIMinistryRequests.version'), nullable=False)
    proactivedisclosurecategoryid = db.Column(db.Integer,ForeignKey('ProactiveDisclosureCategories.proactivedisclosurecategoryid')) 
    proactivedisclosurecategory =  relationship("ProactiveDisclosureCategory",backref=backref("ProactiveDisclosureCategories"),uselist=False)
    reportperiod = db.Column(db.String, nullable=True)
    publicationdate = db.Column(db.DateTime, nullable=True)
    earliesteligiblepublicationdate = db.Column(db.DateTime, nullable=True)
    isactive = db.Column(db.Boolean, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=True)
    createdby = db.Column(db.String(120), nullable=False)
    updatedby = db.Column(db.String(120), nullable=True)
    pdpublicationstatus_id = db.Column(db.Integer, ForeignKey('OpenInfoPublicationStatuses.oipublicationstatusid'), nullable=False)
    processingstatus = db.Column(db.String(120), nullable=True)
    processingmessage = db.Column(db.String(250), nullable=True)
    sitemap_pages = db.Column(db.String(120), nullable=True)


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
                
class FOIProactiveDisclosureRequestSchema(ma.Schema):
    class Meta:
        fields = (
            'proactivedisclosureid', 'foiministryrequest_id', 'foiministryrequestversion_id',
            'proactivedisclosurecategory.proactivedisclosurecategoryid','proactivedisclosurecategory.name','reportperiod',
            'publicationdate', 'created_at', 'updated_at', 'createdby', 'updatedby', 'version', 'isactive', 'oipublicationstatus_id',
            'processingstatus', 'processingmessage', 'sitemap_pages','earliesteligiblepublicationdate'
        )