
from os import stat
from request_api.auth import AuthHelper
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIRequests import FOIRequest
from datetime import datetime
import dateutil.parser
import maya
import json
import logging
from enum import Enum
from urllib.parse import unquote, urlsplit
from request_api.services.applicantcorrespondence.applicantcorrespondencelog import applicantcorrespondenceservice 
from request_api.services.requestservice import requestservice
from request_api.services.cfrfeeservice import cfrfeeservice
from request_api.services.paymentservice import paymentservice
from request_api.models.default_method_result import DefaultMethodResult
from request_api.services.communicationemailservice import communicationemailservice
from request_api.services.email.templates.templateconfig import templateconfig
from request_api.services.emailservice import emailservice
from request_api.schemas.foiemail import  FOIEmailSchema

logger = logging.getLogger(__name__)

class communicationwrapperservice:
    """ FOI communication wrapper service
    """

    def _resolve_ownership_coords(self, ministryrequestid):
        """Resolve (ministrycode, requestnumbers) for attachment ownership validation.

        - ``ministrycode`` is the ``bcgovcode`` of the ministry that owns this
          request (matches S3 key segment 1). Read from the schema dump under
          the dotted key ``'programarea.bcgovcode'``; falls back to a direct
          SQL lookup if absent.
        - ``requestnumbers`` is the set of every value that may legally appear
          as the request-number segment of an S3 key for this request
          (FOIMOD-4270). S3 keys are stamped at upload time and are never
          rewritten, so the set includes:

            * the current ``filenumber`` (covers AXIS-era rows where the S3
              key equals the filenumber),
            * the current ``axisrequestid`` (covers modern rows where the S3
              key equals the current axisrequestid), and
            * every historical ``axisrequestid`` ever recorded on any version
              of this request (covers requests that were renumbered mid-life,
              whose older S3 keys still reference an old axisrequestid value
              no longer present on the current row).

        Returns ``(None, set())`` when resolution fails so callers can fail
        closed.
        """
        from request_api.models.db import db
        from sqlalchemy import text

        ministry = FOIMinistryRequest.getrequest(ministryrequestid) or {}
        # FOIMinistryRequestSchema dumps bcgovcode under the dotted key
        # 'programarea.bcgovcode'. Keep the bare 'bcgovcode' as a defensive
        # alias for tests and any future schema flattening.
        ministrycode = ministry.get('programarea.bcgovcode') or ministry.get('bcgovcode')

        requestnumbers = set()
        for key in ('filenumber', 'axisrequestid'):
            v = ministry.get(key)
            if v:
                requestnumbers.add(v)

        # Historical axisrequestids: renumbers overwrite the current row's
        # value, but earlier row versions retain the older value that some
        # S3 keys still reference. Cheap indexed lookup, runs only when
        # there are attachments to check.
        try:
            rows = db.session.execute(
                text(
                    'SELECT DISTINCT axisrequestid FROM "FOIMinistryRequests" '
                    'WHERE foiministryrequestid = :mid AND axisrequestid IS NOT NULL'
                ),
                {"mid": ministryrequestid},
            ).fetchall()
            for row in rows or []:
                val = row[0]
                if val:
                    requestnumbers.add(val)
        except Exception:
            logger.exception(
                "Historical axisrequestid lookup failed for ministryrequestid=%s; "
                "continuing with current-row values only.",
                ministryrequestid,
            )

        if not ministrycode:
            try:
                row = db.session.execute(
                    text(
                        'SELECT lower(pa.bcgovcode) AS bcgovcode '
                        'FROM "FOIMinistryRequests" mr '
                        'JOIN "ProgramAreas" pa ON pa.programareaid = mr.programareaid '
                        'WHERE mr.foiministryrequestid = :mid '
                        'ORDER BY mr.version DESC LIMIT 1'
                    ),
                    {"mid": ministryrequestid},
                ).fetchone()
                if row and row[0]:
                    ministrycode = row[0]
            except Exception:
                logger.exception(
                    "bcgovcode fallback lookup failed for ministryrequestid=%s",
                    ministryrequestid,
                )

        return ministrycode, requestnumbers

    def _validate_attachment_ownership(self, attachments, ministrycode, requestnumbers):
        """Filter out attachments whose S3 URL does not belong to this request.

        Expected S3 path convention: ``.../{ministrycode}/{requestnumber}/...``
        where ``requestnumber`` is any value that has been the request's
        ``filenumber`` or ``axisrequestid`` over its lifetime — S3 keys are
        stamped at upload time and are not rewritten when a request is
        renumbered (FOIMOD-4270). ``requestnumbers`` may therefore be a set
        (or any iterable) of multiple accepted values; a bare string is also
        accepted for backwards compatibility.

        The match is case-insensitive, path-segment bounded (leading and
        trailing '/'), and evaluated against the URL path only — the
        querystring and fragment are stripped so signed-URL parameters
        (e.g. ?X-Amz-...) cannot cause false positives, and raw S3 keys
        without a scheme are still accepted. Any attachment whose URL does
        not contain any accepted prefix is dropped and logged as a WARNING.
        """
        if not attachments:
            return attachments or []
        if isinstance(requestnumbers, str):
            candidates = [requestnumbers]
        else:
            candidates = [rn for rn in (requestnumbers or []) if rn]
        expected_segments = {
            f"/{ministrycode}/{rn}/".lower()
            for rn in candidates
            if rn
        }
        if not expected_segments:
            logger.warning(
                "Attachment ownership check invoked with no accepted "
                "requestnumbers (ministrycode=%s); rejecting %d attachment(s).",
                ministrycode, len(attachments),
            )
            return []
        valid, rejected = [], []
        for att in attachments:
            raw = att.get('url') or att.get('documenturipath') or ''
            if not raw:
                rejected.append(att)
                continue
            # Extract just the path portion; for scheme-less raw keys
            # urlsplit puts the whole string in .path.
            path = urlsplit(raw).path or raw
            # Normalize percent-encoding and ensure a leading slash so the
            # first path segment is bounded on both sides for the match.
            normalized = unquote(path).lower()
            if not normalized.startswith('/'):
                normalized = '/' + normalized
            if any(seg in normalized for seg in expected_segments):
                valid.append(att)
            else:
                rejected.append(att)
        if rejected:
            logger.warning(
                "Attachment ownership violation blocked: requestnumbers=%s ministrycode=%s "
                "rejected_count=%d rejected_filenames=%s",
                sorted(candidates), ministrycode, len(rejected),
                [a.get('filename') for a in rejected]
            )
        return valid

    def send_email(self, requestid, rawrequestid, ministryrequestid, applicantcorrespondencelog):
        # Get the correct email subject
        data = json.loads(applicantcorrespondencelog['correspondencemessagejson'])
        attributes = applicantcorrespondencelog["attributes"][0]
        emailsubject = ""
        customizedsubject = applicantcorrespondencelog['correspondencesubject'] if 'correspondencesubject' in applicantcorrespondencelog else ""
        if applicantcorrespondencelog["templatename"] is None:
            template = applicantcorrespondenceservice().gettemplatebyid(applicantcorrespondencelog["templateid"])
        else:
            template = None
        if customizedsubject and len(customizedsubject) > 0:
            emailsubject = customizedsubject
        elif template is None:
            if 'templatename' in applicantcorrespondencelog and applicantcorrespondencelog['templatename'] is not None:
                emailsubject = templateconfig().getsubject(applicantcorrespondencelog['templatename'], attributes)
            else:
                emailsubject = templateconfig().getsubject("", attributes)
        else:
            emailsubject = templateconfig().getsubject(template.name, attributes)
        applicantcorrespondencelog['emailsubject'] = emailsubject
        # FOIMOD-4270 — reject attachments that do not belong to this request.
        # Skip the DB lookup entirely when there are no attachments to check.
        if ministryrequestid not in ('None', None) and applicantcorrespondencelog.get('attachments'):
            ministrycode, requestnumbers = self._resolve_ownership_coords(ministryrequestid)
            if ministrycode and requestnumbers:
                applicantcorrespondencelog['attachments'] = self._validate_attachment_ownership(
                    applicantcorrespondencelog.get('attachments', []),
                    ministrycode,
                    requestnumbers,
                )
            else:
                # Fail closed: if we cannot resolve the request's ownership
                # coordinates we cannot verify any attachment belongs to it.
                # Drop them all rather than leak a foreign attachment. Log at
                # ERROR so this is alertable — it should never happen for a
                # valid ministryrequestid.
                original_count = len(applicantcorrespondencelog.get('attachments') or [])
                logger.error(
                    "Attachment ownership check could not resolve requestnumber/ministrycode "
                    "for ministryrequestid=%s (requestnumbers=%r ministrycode=%r); "
                    "dropping %d attachment(s) to fail closed.",
                    ministryrequestid, sorted(requestnumbers), ministrycode, original_count,
                )
                applicantcorrespondencelog['attachments'] = []
        # Save correspondence log based on request type
        if ministryrequestid == 'None' or ministryrequestid is None or ("israwrequest" in applicantcorrespondencelog and applicantcorrespondencelog["israwrequest"]) is True:
            result = applicantcorrespondenceservice().saveapplicantcorrespondencelogforrawrequest(rawrequestid, applicantcorrespondencelog, AuthHelper.getuserid())
        else:
            result = applicantcorrespondenceservice().saveapplicantcorrespondencelog(requestid, ministryrequestid, applicantcorrespondencelog, AuthHelper.getuserid())

        sendemailresult = {"success" : False, "message": "Email has not been sent", "identifier": -1}
        if result.success == True:
            # raw requests should never be fee emails so they would only get handled by else statement
            # Handle fee processing templates
            templatename = ""
            if applicantcorrespondencelog["templateid"] is not None:
                templatename = applicantcorrespondenceservice().gettemplatebyid(applicantcorrespondencelog["templateid"]).name
            else:
                templatename = applicantcorrespondencelog["templatename"]

            if self.__is_fee_processing(templatename):
                return self.__handle_fee_email(requestid, ministryrequestid, result, applicantcorrespondencelog)
            # Handle non-fee templates - Send email for non-fee templates with email recipients
            else:
                if ("emails" in applicantcorrespondencelog and len(applicantcorrespondencelog["emails"]) > 0) or ("ccemails" in applicantcorrespondencelog and len(applicantcorrespondencelog["ccemails"]) > 0):
                        # template["name"] = applicantcorrespondencelog["templatename"]
                        # template["description"] = applicantcorrespondencelog["templatename"]
                    sendemailresult = communicationemailservice().send(template, applicantcorrespondencelog)
                    # Update the sent status in the correspondence log after sending the email
                    is_sent_succesfully = sendemailresult["success"]
                    from_email = sendemailresult["from_email"] if "from_email" in sendemailresult else None
                    if ministryrequestid == 'None' or ministryrequestid is None or ("israwrequest" in applicantcorrespondencelog and applicantcorrespondencelog["israwrequest"]) is True:
                        applicantcorrespondenceservice().updateappcorrespondenceaftersendforrawrequest(rawrequestid, result.identifier, is_sent_succesfully, from_email)
                    else:
                        applicantcorrespondenceservice().updateappcorrespondenceaftersendforministryrequest(ministryrequestid, result.identifier, is_sent_succesfully, from_email)
                    return sendemailresult
                else:
                    return {"success" : False, "message": "No Email", "identifier": -1}
        elif result.success == False:
            sendemailresult = {"success" : False, "message": result.message, "identifier": -1}
        return sendemailresult

    def send_preview_email(self, requestid, rawrequestid, ministryrequestid, applicantcorrespondencelog, correspondencemessagejson):
        data = json.loads(applicantcorrespondencelog['correspondencemessagejson'])
        attributes = applicantcorrespondencelog["attributes"][0]
        emailsubject = ""
        customizedsubject = applicantcorrespondencelog['correspondencesubject'] if 'correspondencesubject' in applicantcorrespondencelog else ""
        if applicantcorrespondencelog["templatename"] is None:
            template = applicantcorrespondenceservice().gettemplatebyid(applicantcorrespondencelog["templateid"])
        else:
            template = None
        if customizedsubject and len(customizedsubject) > 0:
            emailsubject = customizedsubject
        elif template is None:
            if 'templatename' in applicantcorrespondencelog and applicantcorrespondencelog['templatename'] is not None:
                emailsubject = templateconfig().getsubject(applicantcorrespondencelog['templatename'], attributes)
            else:
                emailsubject = templateconfig().getsubject("", attributes)
        else:
            emailsubject = templateconfig().getsubject(template.name, attributes)
        applicantcorrespondencelog['emailsubject'] = emailsubject

        sendemailresult = {"success" : False, "message": "Email has not been sent", "identifier": -1}
        templatename = ""
        if applicantcorrespondencelog["templateid"] is not None:
            templatename = applicantcorrespondenceservice().gettemplatebyid(applicantcorrespondencelog["templateid"]).name
        else:
            templatename = applicantcorrespondencelog["templatename"]

        if self.__is_fee_processing(templatename):
            emailschema = { "templatename": templatename }
            result = emailservice().send_preview_email(templatename.upper(), requestid, ministryrequestid, emailschema, emailsubject, applicantcorrespondencelog['emails'], correspondencemessagejson)
            return result
        else:
            sendemailresult = communicationemailservice().send(template, applicantcorrespondencelog)
            return sendemailresult

    def __handle_fee_email(self, requestid, ministryrequestid, result, applicantcorrespondencelog):
        if cfrfeeservice().getactivepayment(requestid, ministryrequestid) is not None:
            requestservice().postfeeeventtoworkflow(requestid, ministryrequestid, "CANCELLED")
        _attributes = applicantcorrespondencelog["attributes"][0] if "attributes" in applicantcorrespondencelog else None
        _paymentexpirydate =  _attributes["paymentExpiryDate"] if _attributes is not None and "paymentExpiryDate" in _attributes else None
        if _paymentexpirydate not in (None, ""):
            paymentservice().createpayment(requestid, ministryrequestid, _attributes, AuthHelper.getuserid())            
        requestservice().postcorrespondenceeventtoworkflow(requestid, ministryrequestid, result.identifier, applicantcorrespondencelog)
        return {"success" : True, "message": "Sent successfully", "identifier": -1}  


    def __is_fee_processing(self, templatename):
        if templatename in ['PAYONLINE','PAYOUTSTANDING']:
            return True
        return False

class CommuniationType(Enum):
    """Communication types."""
    FEE_PROCESSING = 'FEE_PROCESSING'
    GENERAL = 'GENERAL'   