from flask.app import Flask
from sqlalchemy.sql.schema import ForeignKey, ForeignKeyConstraint
from .db import  db, ma
from datetime import datetime, timedelta
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
                    oipublicationstatus_id=foiproactiverequest.get("oipublicationstatus_id", 2),
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
    def mark_ready_for_crawling(cls, foiministryrequestid, sitemap_page)->DefaultMethodResult:
        try:
            current = (
                db.session.query(cls)
                .filter(cls.foiministryrequest_id == foiministryrequestid)
                .order_by(cls.version.desc())
                .first()
            )
            if current is None:
                return DefaultMethodResult(
                    False,
                    "FOI Proactive Disclosure request not found",
                    foiministryrequestid,
                )

            updated_at = datetime2.now().isoformat()

            active_rows = (
                db.session.query(cls)
                .filter(cls.foiministryrequest_id == foiministryrequestid)
                .filter(or_(cls.isactive == True, cls.isactive.is_(None)))
                .all()
            )
            for row in active_rows:
                row.isactive = False
                row.updated_at = updated_at
                row.updatedby = "publishingservice"

            latest = (
                db.session.query(cls)
                .filter(cls.foiministryrequest_id == foiministryrequestid)
                .order_by(cls.version.desc())
                .first()
            )

            new_proactive = FOIProactiveDisclosureRequests(
                proactivedisclosureid=latest.proactivedisclosureid,
                version=latest.version + 1,
                foiministryrequest_id=latest.foiministryrequest_id,
                foiministryrequestversion_id=latest.foiministryrequestversion_id,
                proactivedisclosurecategoryid=latest.proactivedisclosurecategoryid,
                reportperiod=latest.reportperiod,
                publicationdate=latest.publicationdate,
                earliesteligiblepublicationdate=latest.earliesteligiblepublicationdate,
                isactive=True,
                created_at=updated_at,
                createdby="publishingservice",
                oipublicationstatus_id=latest.oipublicationstatus_id,
                processingstatus="ready for crawling",
                processingmessage="Published", 
                sitemap_pages=sitemap_page
            )
            db.session.add(new_proactive)
            logging.info(
                "FOIProactiveDisclsoure row updated for ministry request %s with sitemap page %s",
                foiministryrequestid,
                sitemap_page,
            )
            db.session.commit()
            return DefaultMethodResult(True, "Proactive Disclosure publication status updated", foiministryrequestid)
        except Exception as exception:
            logging.error(f"Error updating Proactive Disclosure publication status: {exception}")
            db.session.rollback()
            return DefaultMethodResult(False, "Proactive Disclosure publication status unable to be updated", foiministryrequestid)
        finally:
            db.session.close()

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

    @classmethod
    def create_published_version_from_proactive_id(cls, proactivedisclosureid, message, sitemap, publicationdate)->DefaultMethodResult:
        try:
            current = (
                db.session.query(cls)
                .filter(cls.proactivedisclosureid == proactivedisclosureid)
                .order_by(cls.version.desc())
                .first()
            )
            if current is None:
                return DefaultMethodResult(
                    False,
                    "FOI Proactive Disclosure request not found",
                    proactivedisclosureid,
                )

            updated_at = datetime2.now().isoformat()
            ministry_request_id = current.foiministryrequest_id

            active_rows = (
                db.session.query(cls)
                .filter(cls.foiministryrequest_id == ministry_request_id)
                .filter(or_(cls.isactive == True, cls.isactive.is_(None)))
                .all()
            )
            for row in active_rows:
                row.isactive = False
                row.updated_at = updated_at
                row.updatedby = "publishingservice"

            latest = (
                db.session.query(cls)
                .filter(cls.foiministryrequest_id == ministry_request_id)
                .order_by(cls.version.desc())
                .first()
            )

            new_proactive = FOIProactiveDisclosureRequests(
                proactivedisclosureid=latest.proactivedisclosureid,
                version=latest.version + 1,
                foiministryrequest_id=latest.foiministryrequest_id,
                foiministryrequestversion_id=latest.foiministryrequestversion_id,
                proactivedisclosurecategoryid=latest.proactivedisclosurecategoryid,
                reportperiod=latest.reportperiod,
                publicationdate=publicationdate if publicationdate is not None else latest.publicationdate,
                earliesteligiblepublicationdate=latest.earliesteligiblepublicationdate,
                isactive=True,
                created_at=updated_at,
                createdby="publishingservice",
                oipublicationstatus_id=latest.oipublicationstatus_id,
                processingstatus="ready for crawling",
                processingmessage=message, 
                sitemap_pages=sitemap
            )
            db.session.add(new_proactive)
            db.session.commit()
            return DefaultMethodResult(
                True,
                "Proactive Disclosure publication status updated",
                new_proactive.proactivedisclosureid,
            )
        except Exception as exception:
            db.session.rollback()
            logging.error(f"Error updating Proactive Disclosure publication status: {exception}")
            return DefaultMethodResult(False, str(exception), proactivedisclosureid)
        finally:
            db.session.close()

    @classmethod
    def getpdrecordsforprepublishing(cls, now=None):
        try:
            publication_cutoff = ((now or datetime2.now()) + timedelta(days=1)).strftime('%Y-%m-%d')
            sql = """
                SELECT
                    pd.proactivedisclosureid,
                    pd.created_at,
                    mr.foiministryrequestid,
                    r.foirequestid,
                    mr.axisrequestid,
                    mr.description,
                    to_char(pd.publicationdate, 'YYYY-MM-DD') AS published_date,
                    pa.name as contributor,
                    ac.name as applicant_type,
                    COALESCE((fee.feedata->>'amountpaid')::Numeric, 0) as fees,
                    LOWER(pa.bcgovcode) AS bcgovcode,
                    COALESCE(pd.sitemap_pages, '') as sitemap_pages,
                    'publish' as type,
                    COALESCE(pdc.name, '') as proactivedisclosurecategory,
                    COALESCE(pd.reportperiod, '') as reportperiod,
                    COALESCE(
                        json_agg(
                            json_build_object(
                                'additionalfileid', oifiles.additionalfileid,
                                'filename', oifiles.filename,
                                's3uripath', oifiles.s3uripath,
                                'isactive', oifiles.isactive
                            )
                        ) FILTER (WHERE oifiles.additionalfileid IS NOT NULL), '[]'::json
                    ) AS additionalfiles
                FROM public."FOIMinistryRequests" mr
                INNER JOIN public."FOIRequests" r
                    ON mr.foirequest_id = r.foirequestid AND mr.foirequestversion_id = r.version
                INNER JOIN public."ProgramAreas" pa
                    ON mr.programareaid = pa.programareaid
                LEFT JOIN public."ApplicantCategories" ac
                    ON r.applicantcategoryid = ac.applicantcategoryid
                LEFT JOIN (
                    SELECT ministryrequestid, MAX(version) as max_version
                    FROM public."FOIRequestCFRFees"
                    GROUP BY ministryrequestid
                ) latest_payment
                    ON mr.foiministryrequestid = latest_payment.ministryrequestid
                LEFT JOIN public."FOIRequestCFRFees" fee
                    ON mr.foiministryrequestid = fee.ministryrequestid
                    AND latest_payment.max_version = fee.version
                    AND mr.version = fee.ministryrequestversion
                INNER JOIN public."FOIProactiveDisclosureRequests" pd
                    ON mr.foiministryrequestid = pd.foiministryrequest_id AND pd.isactive = TRUE
                LEFT JOIN public."ProactiveDisclosureCategories" pdc
                    ON pd.proactivedisclosurecategoryid = pdc.proactivedisclosurecategoryid
                INNER JOIN public."OpenInformationStatuses" oistatus
                    ON mr.oistatus_id = oistatus.oistatusid
                INNER JOIN public."OpenInfoPublicationStatuses" oirequesttype
                    ON pd.oipublicationstatus_id = oirequesttype.oipublicationstatusid
                LEFT JOIN public."FOIOpenInfoAdditionalFiles" oifiles
                    ON mr.foiministryrequestid = oifiles.ministryrequestid
                WHERE oistatus.name IN (:ready_status, :published_status)
                  AND oirequesttype.name = :publication_status
                  AND pd.publicationdate < :publication_cutoff
                  AND (pd.processingmessage != 'Published' OR pd.processingmessage is NULL) 
                  AND mr.isactive = TRUE
                GROUP BY
                    pd.proactivedisclosureid,
                    pd.created_at,
                    mr.foiministryrequestid,
                    r.foirequestid,
                    mr.axisrequestid,
                    mr.description,
                    pd.publicationdate,
                    pa.name,
                    ac.name,
                    COALESCE((fee.feedata->>'amountpaid')::Numeric, 0),
                    pa.bcgovcode,
                    pd.sitemap_pages,
                    pdc.name,
                    pd.reportperiod;
            """
            result = db.session.execute(
                text(sql),
                {
                    'ready_status': 'Ready to Publish',
                    'published_status': 'Published',
                    'publication_status': 'Publish',
                    'publication_cutoff': publication_cutoff,
                },
            )
            return [dict(row) for row in result]
        except Exception as exception:
            logging.error(f"Error fetching Proactive Disclosure pre-publishing records: {exception}")
            return []
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
