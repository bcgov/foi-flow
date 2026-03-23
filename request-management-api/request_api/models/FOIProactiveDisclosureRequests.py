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
    isactive = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=True)
    createdby = db.Column(db.String(120), nullable=False)
    updatedby = db.Column(db.String(120), nullable=True)
    oipublicationstatus_id = db.Column(db.Integer, ForeignKey('OpenInfoPublicationStatuses.oipublicationstatusid'), nullable=False)
    processingstatus = db.Column(db.String(120), nullable=True)
    processingmessage = db.Column(db.String(250), nullable=True)
    sitemap_pages = db.Column(db.String(120), nullable=True)


    @classmethod
    def getproactiverequestbyministryrequestid(cls,ministryrequestid, ministryversion):
        request_schema = FOIProactiveDisclosureRequestSchema()
        query = db.session.query(FOIProactiveDisclosureRequests).filter_by(foiministryrequest_id=ministryrequestid , foiministryrequestversion_id = ministryversion, isactive=True).order_by(FOIProactiveDisclosureRequests.version.desc()).first()
        return request_schema.dump(query) 

    @classmethod
    def getcurrentfoiproactiverequest(cls, foiministryrequestid)->DefaultMethodResult:
        try:
            request_schema = FOIProactiveDisclosureRequestSchema()
            query = db.session.query(FOIProactiveDisclosureRequests).filter_by(foiministryrequest_id=foiministryrequestid, isactive=True).order_by(FOIProactiveDisclosureRequests.version.desc()).first()
            return request_schema.dump(query)
        except Exception as exception:
            logging.error(f"Error: {exception}")

    @classmethod
    def savefoiproactiverequest(cls, foiproactiverequest, userid)->DefaultMethodResult:
        try:
            current_proactive = cls.getcurrentfoiproactiverequest(foiproactiverequest['foiministryrequest_id'])
            createddate = datetime2.now().isoformat()
            if current_proactive:
                new_proactive = FOIProactiveDisclosureRequests(
                    proactivedisclosureid=current_proactive['proactivedisclosureid'],
                    version=current_proactive['version']+1,
                    foiministryrequest_id=foiproactiverequest["foiministryrequest_id"],
                    foiministryrequestversion_id=foiproactiverequest["foiministryrequestversion_id"],
                    proactivedisclosurecategoryid=foiproactiverequest.get("proactivedisclosurecategoryid", current_proactive.get("proactivedisclosurecategory.proactivedisclosurecategoryid")),
                    reportperiod=foiproactiverequest.get("reportperiod", current_proactive.get("reportperiod")),
                    publicationdate=foiproactiverequest.get("publicationdate", current_proactive.get("publicationdate")) if foiproactiverequest.get("publicationdate", current_proactive.get("publicationdate")) != "" else None,
                    earliesteligiblepublicationdate=foiproactiverequest.get("earliesteligiblepublicationdate", current_proactive.get("earliesteligiblepublicationdate")) if foiproactiverequest.get("earliesteligiblepublicationdate", current_proactive.get("earliesteligiblepublicationdate")) != "" else None,
                    isactive=True,
                    created_at=createddate,
                    createdby=userid,
                    oipublicationstatus_id=foiproactiverequest.get("oipublicationstatus_id", current_proactive.get("oipublicationstatus_id")),
                    processingstatus=foiproactiverequest.get("processingstatus", current_proactive.get("processingstatus")),
                    processingmessage=foiproactiverequest.get("processingmessage", current_proactive.get("processingmessage")),
                    sitemap_pages=foiproactiverequest.get("sitemap_pages", current_proactive.get("sitemap_pages"))
                )
                db.session.add(new_proactive)
                db.session.commit()
                return DefaultMethodResult(True, "FOI Proactive Disclosure request version updated", new_proactive.proactivedisclosureid)
            else:
                new_proactive = FOIProactiveDisclosureRequests(
                    version=1,
                    foiministryrequest_id=foiproactiverequest["foiministryrequest_id"],
                    foiministryrequestversion_id=foiproactiverequest["foiministryrequestversion_id"],
                    proactivedisclosurecategoryid=foiproactiverequest.get("proactivedisclosurecategoryid"),
                    reportperiod=foiproactiverequest.get("reportperiod"),
                    publicationdate=foiproactiverequest.get("publicationdate") if foiproactiverequest.get("publicationdate") != "" else None,
                    earliesteligiblepublicationdate=foiproactiverequest.get("earliesteligiblepublicationdate") if foiproactiverequest.get("earliesteligiblepublicationdate") != "" else None,
                    isactive=True,
                    created_at=createddate,
                    createdby=userid,
                    oipublicationstatus_id=foiproactiverequest.get("oipublicationstatus_id", 1),
                    processingstatus=foiproactiverequest.get("processingstatus"),
                    processingmessage=foiproactiverequest.get("processingmessage"),
                    sitemap_pages=foiproactiverequest.get("sitemap_pages")
                )
                db.session.add(new_proactive)
                db.session.commit()
                return DefaultMethodResult(True, "FOI Proactive Disclosure request created", new_proactive.proactivedisclosureid)
        except Exception as exception:
            logging.error(f"Error: {exception}")
            return DefaultMethodResult(False, "FOI Proactive Disclosure request version unable to be updated")

    @classmethod
    def deActivateOldVersion(cls, ministryid, userid)->DefaultMethodResult:
        try:
            sql = """update "FOIProactiveDisclosureRequests" set isactive = false, updatedby = :userid, updated_at = now()  
                        where foiministryrequest_id = :ministryid and isactive = true 
                        and version != (select version from "FOIProactiveDisclosureRequests" where foiministryrequest_id = :ministryid order by "version" desc limit 1)"""
            db.session.execute(text(sql), {'ministryid': ministryid, 'userid':userid})
            db.session.commit()
            return DefaultMethodResult(True,'Request Updated',ministryid)
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
                
class FOIProactiveDisclosureRequestSchema(ma.Schema):
    class Meta:
        fields = (
            'proactivedisclosureid', 'foiministryrequest_id', 'foiministryrequestversion_id',
            'proactivedisclosurecategory.proactivedisclosurecategoryid','proactivedisclosurecategory.name','reportperiod',
            'publicationdate', 'created_at', 'updated_at', 'createdby', 'updatedby', 'version', 'isactive', 'oipublicationstatus_id',
            'processingstatus', 'processingmessage', 'sitemap_pages','earliesteligiblepublicationdate'
        )