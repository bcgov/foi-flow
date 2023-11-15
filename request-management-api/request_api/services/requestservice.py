from re import T

from request_api.services.documentservice import documentservice
from request_api.services.workflowservice import workflowservice
from request_api.services.watcherservice import watcherservice
from request_api.services.commentservice import commentservice
from request_api.services.paymentservice import paymentservice
from request_api.services.foirequest.requestserviceconfigurator import (
    requestserviceconfigurator,
)
from request_api.services.foirequest.requestservicegetter import requestservicegetter
from request_api.services.foirequest.requestservicecreate import requestservicecreate
from request_api.services.foirequest.requestserviceupdate import requestserviceupdate
from request_api.services.applicantcorrespondence.applicantcorrespondencelog import (
    applicantcorrespondenceservice,
)
from request_api.services.subjectcodeservice import subjectcodeservice
from request_api.models.FOIRequestStatus import FOIRequestStatus
from request_api.models.FOIRawRequests import FOIRawRequest
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIMinistryRequestSubjectCodes import (
    FOIMinistryRequestSubjectCode,
)
from request_api.models.SubjectCodes import SubjectCode
from request_api.models.FOIRestrictedMinistryRequests import (
    FOIRestrictedMinistryRequest,
)
from request_api.utils.enums import StateName
from request_api.services.commons.duecalculator import duecalculator
from request_api.utils.commons.datetimehandler import datetimehandler
import os
import json


class requestservice:
    """FOI Request management service

    This service class manages all CRUD operations related to an FOI opened Request

    """

    def saverequest(
        self,
        foirequestschema,
        userid,
        foirequestid=None,
        ministryid=None,
        filenumber=None,
        version=None,
        rawrequestid=None,
        wfinstanceid=None,
    ):
        return requestservicecreate().saverequest(
            foirequestschema,
            userid,
            foirequestid,
            ministryid,
            filenumber,
            version,
            rawrequestid,
            wfinstanceid,
        )

    def saverequestversion(self, foirequestschema, foirequestid, ministryid, userid):
        nextstatename = FOIRequestStatus.getrequeststatusname(
            foirequestschema["requeststatusid"]
        )
        rev_foirequestschema = self.updateduedate(
            foirequestid,
            ministryid,
            datetimehandler().gettoday(),
            foirequestschema,
            nextstatename,
        )
        responseschema = requestservicecreate().saverequestversion(
            rev_foirequestschema, foirequestid, ministryid, userid
        )
        if "paymentExpiryDate" in foirequestschema and foirequestschema[
            "paymentExpiryDate"
        ] not in (None, ""):
            paymentservice().createpayment(
                foirequestid, ministryid, foirequestschema, userid
            )
        return responseschema

    def saveministryrequestversion(
        self, ministryrequestschema, foirequestid, ministryid, userid, usertype=None
    ):
        return requestservicecreate().saveministryrequestversion(
            ministryrequestschema, foirequestid, ministryid, userid, usertype
        )

    def updaterequest(self, foirequestschema, foirequestid, userid):
        return requestserviceupdate().updaterequest(
            foirequestschema, foirequestid, userid
        )

    def updateministryrequestduedate(self, ministryrequestid, duedate, userid):
        return requestserviceupdate().updateministryrequestduedate(
            ministryrequestid, duedate, userid
        )

    def postpaymentstatetransition(
        self, requestid, ministryrequestid, nextstatename, paymentdate
    ):
        _foirequest = self.getrequest(requestid, ministryrequestid)
        foirequest = self.updateduedate(
            requestid, ministryrequestid, paymentdate, _foirequest, nextstatename
        )
        status = FOIRequestStatus().getrequeststatusid(nextstatename)
        foirequest["requeststatusid"] = status["requeststatusid"]
        return requestservicecreate().saverequestversion(
            foirequest, requestid, ministryrequestid, "Online Payment"
        )

    def updateduedate(
        self, requestid, ministryrequestid, offholddate, foirequestschema, nextstatename
    ):
        foirequest = self.getrequest(requestid, ministryrequestid)
        currentstatus = (
            foirequest["stateTransition"][0]["status"]
            if "stateTransition" in foirequest
            and len(foirequest["stateTransition"]) > 1
            else None
        )
        # Check for Off Hold
        if (
            currentstatus not in (None, "")
            and currentstatus == StateName.onhold.value
            and nextstatename != StateName.response.value
        ):
            skipcalculation = self.__skipduedatecalculation(
                ministryrequestid, offholddate, currentstatus, nextstatename
            )
            # Skip multiple off hold in a day
            if skipcalculation == True:
                calc_duedate, calc_cfrduedate = (
                    foirequest["dueDate"],
                    foirequest["cfrDueDate"],
                )
            else:
                calc_duedate, calc_cfrduedate = self.calculateduedate(
                    ministryrequestid, foirequest, offholddate
                )
            foirequestschema["dueDate"] = calc_duedate
            foirequestschema["cfrDueDate"] = calc_cfrduedate
        return foirequestschema

    def getrequest(self, foirequestid, foiministryrequestid):
        return requestservicegetter().getrequest(foirequestid, foiministryrequestid)

    def getrequestdetailsforministry(
        self, foirequestid, foiministryrequestid, authmembershipgroups
    ):
        return requestservicegetter().getrequestdetailsforministry(
            foirequestid, foiministryrequestid, authmembershipgroups
        )

    def getrequestdetails(self, foirequestid, foiministryrequestid):
        return requestservicegetter().getrequestdetails(
            foirequestid, foiministryrequestid
        )

    def getrequestid(self, foiministryrequestid):
        return FOIMinistryRequest.getrequest(foiministryrequestid)["foirequest_id"]

    def copywatchers(self, rawrequestid, ministries, userid):
        watchers = watcherservice().getrawrequestwatchers(int(rawrequestid))
        for ministry in ministries:
            for watcher in watchers:
                watcherschema = {
                    "ministryrequestid": ministry["id"],
                    "watchedbygroup": watcher["watchedbygroup"],
                    "watchedby": watcher["watchedby"],
                    "isactive": True,
                }
                watcherservice().createministryrequestwatcher(
                    watcherschema, userid, None
                )

    def copycomments(self, rawrequestid, ministries, userid):
        comments = commentservice().getrawrequestcomments(int(rawrequestid))
        for ministry in ministries:
            commentservice().copyrequestcomment(ministry["id"], comments, userid)

    def copydocuments(self, rawrequestid, ministries, userid):
        attachments = documentservice().getrequestdocuments(
            int(rawrequestid), "rawrequest"
        )
        for ministry in ministries:
            documentservice().copyrequestdocuments(ministry["id"], attachments, userid)

    def copysubjectcode(self, subjectcode, ministries, userid):
        if subjectcode:
            for ministry in ministries:
                subjectcodeservice().savesubjectcode(
                    ministry["id"], subjectcode, userid
                )

    def postopeneventtoworkflow(self, id, requestschema, ministries):
        pid = workflowservice().syncwfinstance("rawrequest", requestschema["id"])
        workflowservice().postunopenedevent(id, pid, requestschema, "Open", ministries)

    def postfeeeventtoworkflow(
        self, requestid, ministryrequestid, paymentstatus, nextstatename=None
    ):
        foirequestschema = self.getrequestdetails(requestid, ministryrequestid)
        workflowservice().postfeeevent(
            requestid, ministryrequestid, foirequestschema, paymentstatus, nextstatename
        )

    def posteventtoworkflow(self, id, requestschema, data, usertype):
        requeststatusid = (
            requestschema.get("requeststatusid")
            if "requeststatusid" in requestschema
            else None
        )
        status = (
            requestserviceconfigurator().getstatusname(requeststatusid)
            if requeststatusid is not None
            else None
        )
        pid = workflowservice().syncwfinstance("ministryrequest", id)
        workflowservice().postopenedevent(
            id, pid, requestschema, data, status, usertype
        )

    def postcorrespondenceeventtoworkflow(
        self,
        requestid,
        ministryrequestid,
        applicantcorrespondenceid,
        attributes,
        templateid,
    ):
        foirequestschema = self.getrequestdetails(requestid, ministryrequestid)
        templatedetails = applicantcorrespondenceservice().gettemplatebyid(templateid)
        wfinstanceid = workflowservice().syncwfinstance(
            "ministryrequest", ministryrequestid, True
        )
        workflowservice().postcorrenspodenceevent(
            wfinstanceid,
            ministryrequestid,
            foirequestschema,
            applicantcorrespondenceid,
            templatedetails.name,
            attributes,
        )

    def calculateduedate(self, ministryrequestid, foirequest, paymentdate):
        duedate_includeoffhold, cfrduedate_includeoffhold = self.__isincludeoffhold()
        onhold_extend_days = duecalculator().getbusinessdaysbetween(
            foirequest["onholdTransitionDate"], paymentdate
        )
        isoffhold_businessday = duecalculator().isbusinessday(paymentdate)
        duedate_extend_days = (
            onhold_extend_days + 1
            if isoffhold_businessday == True and duedate_includeoffhold == True
            else onhold_extend_days
        )
        cfrduedate_extend_days = (
            onhold_extend_days + 1
            if isoffhold_businessday == True and cfrduedate_includeoffhold == True
            else onhold_extend_days
        )
        calc_duedate = duecalculator().addbusinessdays(
            foirequest["dueDate"], duedate_extend_days
        )
        calc_cfrduedate = duecalculator().addbusinessdays(
            foirequest["cfrDueDate"], cfrduedate_extend_days
        )
        return calc_duedate, calc_cfrduedate

    def __skipduedatecalculation(
        self, ministryrequestid, offholddate, currentstatus="", nextstatename=""
    ):
        print("currentstatus >>>>> ", currentstatus)
        print("nextstatename >>>>> ", nextstatename)
        previousoffholddate = FOIMinistryRequest.getlastoffholddate(ministryrequestid)
        if (
            currentstatus not in (None, "")
            and currentstatus == StateName.onhold.value
            and nextstatename not in (None, "")
            and currentstatus == nextstatename["name"]
        ):
            return True
        if previousoffholddate not in (None, ""):
            previouspaymentdate_pst = datetimehandler().convert_to_pst(
                previousoffholddate
            )
            if (
                datetimehandler().getdate(previouspaymentdate_pst).date()
                == datetimehandler().getdate(offholddate).date()
            ):
                return True
        return False

    def __isincludeoffhold(self):
        payment_config_str = os.getenv("PAYMENT_CONFIG", "")
        if payment_config_str in (None, ""):
            return True, True
        _paymentconfig = json.loads(payment_config_str)
        duedate_includeoffhold = (
            True if _paymentconfig["duedate"]["includeoffhold"] == "Y" else False
        )
        cfrduedate_includeoffhold = (
            True if _paymentconfig["cfrduedate"]["includeoffhold"] == "Y" else False
        )
        return duedate_includeoffhold, cfrduedate_includeoffhold

    # intake in progress to open: create a restricted request record for each selected ministries
    def createrestrictedrequests(self, ministries, type, isrestricted, userid):
        for ministry in ministries:
            version = FOIMinistryRequest.getversionforrequest(ministry["id"])
            FOIRestrictedMinistryRequest.disablerestrictedrequests(
                ministry["id"], type, userid
            )
            FOIRestrictedMinistryRequest.saverestrictedrequest(
                ministry["id"], type, isrestricted, version, userid
            )

    def saverestrictedrequest(self, ministryrequestid, type, isrestricted, userid):
        version = FOIMinistryRequest.getversionforrequest(ministryrequestid)
        FOIRestrictedMinistryRequest.disablerestrictedrequests(
            ministryrequestid, type, userid
        )
        return FOIRestrictedMinistryRequest.saverestrictedrequest(
            ministryrequestid, type, isrestricted, version, userid
        )
