
from os import stat
from request_api.auth import AuthHelper
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIRequests import FOIRequest
from datetime import datetime
import dateutil.parser
import maya
from enum import Enum
from request_api.services.applicantcorrespondence.applicantcorrespondencelog import applicantcorrespondenceservice 
from request_api.services.requestservice import requestservice
from request_api.services.cfrfeeservice import cfrfeeservice
from request_api.services.paymentservice import paymentservice
from request_api.models.default_method_result import DefaultMethodResult
from request_api.services.communicationemailservice import communicationemailservice

class communicationwrapperservice:
    """ FOI communication wrapper service

    """
    
    def send_email(self,requestid, ministryrequestid, applicantcorrespondencelog):
        result = applicantcorrespondenceservice().saveapplicantcorrespondencelog(requestid, ministryrequestid, applicantcorrespondencelog, AuthHelper.getuserid())
        if result.success == True:
            if self.__is_fee_processing(applicantcorrespondencelog["templateid"]) == True:
                return self.__handle_fee_email(requestid, ministryrequestid, applicantcorrespondencelog)
            else:
                if "emails" in applicantcorrespondencelog and len(applicantcorrespondencelog["emails"]) > 0:
                    template = applicantcorrespondenceservice().gettemplatebyid(applicantcorrespondencelog["templateid"])
                    return communicationemailservice().send(template, applicantcorrespondencelog)
                return result
                




    def __handle_fee_email(self,requestid, ministryrequestid, applicantcorrespondencelog):
        if cfrfeeservice().getactivepayment(requestid, ministryrequestid) != None:
            requestservice().postfeeeventtoworkflow(requestid, ministryrequestid, "CANCELLED")
            _attributes = applicantcorrespondencelog["attributes"][0] if "attributes" in applicantcorrespondencelog else None
            _paymentexpirydate =  _attributes["paymentExpiryDate"] if _attributes is not None and "paymentExpiryDate" in _attributes else None
            if _paymentexpirydate not in (None, ""):
                paymentservice().createpayment(requestid, ministryrequestid, _attributes, AuthHelper.getuserid())
        return requestservice().postcorrespondenceeventtoworkflow(requestid, ministryrequestid, result.identifier, applicantcorrespondencelog['attributes'], applicantcorrespondencelog['templateid'])

    def __is_fee_processing(self, templateid):
        if applicantcorrespondenceservice().gettemplatebyid(templateid) in ['PAYONLINE','PAYOUTSTANDING']:
            return True
        return False

class CommuniationType(Enum):
    """Communication types."""
    FEE_PROCESSING = 'FEE_PROCESSING'
    GENERAL = 'GENERAL'        