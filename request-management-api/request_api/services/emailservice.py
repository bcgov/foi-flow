
import os
from re import VERBOSE
import json
import email
import smtplib
import imaplib
from imap_tools import MailBox, AND
import logging
from request_api.services.documentservice import documentservice
from request_api.services.external.storageservice import storageservice
from request_api.services.email.templates.templateservice import templateservice
from request_api.services.email.templates.templateconfig import templateconfig
from request_api.services.email.senderservice import senderservice
from request_api.services.email.inboxservice import inboxservice
from request_api.services.eventservice import eventservice
from request_api.services.requestservice import requestservice
from request_api.services.applicantcorrespondence.applicantcorrespondencelog  import applicantcorrespondenceservice
from request_api.utils.enums import ServiceName
from request_api.auth import AuthHelper
import logging

class emailservice:
    """ FOI Email Service
    """
  
    def send(self, servicename, requestid, ministryrequestid, emailschema):
        subject = None
        savedcorrespondence = None
        try:
            print("============send function================")
            requestjson = requestservice().getrequestdetails(requestid,ministryrequestid)
            _templatename = self.__getvaluefromschema(emailschema, "templatename")
            servicename = _templatename  if servicename == ServiceName.correspondence.value.upper() else servicename            
            _applicantcorrespondenceid = self.__getvaluefromschema(emailschema, "applicantcorrespondenceid")
            print("_applicantcorrespondenceid : ", _applicantcorrespondenceid)
            _messagepart, content = templateservice().generate_by_servicename_and_schema(servicename, requestjson, ministryrequestid, _applicantcorrespondenceid)
            if (_applicantcorrespondenceid and templateconfig().isnotreceipt(servicename)):
                servicename = _templatename.upper() if _templatename else ""
            _messageattachmentlist = self.__get_attachments(ministryrequestid, emailschema, servicename)
            savedcorrespondence = self.__pre_send_correspondence_audit(requestid, ministryrequestid,emailschema, content, templateconfig().isnotreceipt(servicename), _messageattachmentlist, recipient_email=requestjson.get("email"))
            print("savedcorrespondence : ",savedcorrespondence)
            if savedcorrespondence and _applicantcorrespondenceid:
                print("Debug 1")
                subject = getattr(applicantcorrespondenceservice().fetch_applicant_correspondence_log_by_id(_applicantcorrespondenceid), "emailsubject", subject)
                print("Debug subject : ",subject)                
            if subject is None:
                subject = templateconfig().getsubject(servicename, requestjson)
            print("inside send func subject : ",subject)
            emailresult = senderservice().send(subject, _messagepart, _messageattachmentlist, requestjson.get("email"))
            return {"success": emailresult["success"], "message": emailresult["message"], "identifier": savedcorrespondence.identifier, "subject": subject}
        except Exception as ex:
            logging.exception(ex)
            return {"success": False, "message": "Failed to send email", "identifier": savedcorrespondence.identifier if savedcorrespondence else -1, "subject": subject}

    def acknowledge(self, servicename, requestid, ministryrequestid):
        try:
            requestjson = requestservice().getrequestdetails(requestid,ministryrequestid)
            self.__upload_sent_email(servicename, ministryrequestid, requestjson)
            ackresponse = inboxservice().get_failure_deliverystatus_as_eml(templateconfig().getsubject(servicename, requestjson), requestjson["email"])
            if ackresponse["success"] == False:
                self.__upload(templateconfig().getattachmentname(servicename+"-SEND-FAILURE")+".eml", ackresponse["content"], ministryrequestid, requestjson, templateconfig().getattachmentcategory(servicename+"-FAILED"))   
                eventservice().posteventforemailfailure(ministryrequestid, "ministryrequest", templateconfig().getstage(servicename), ackresponse["reason"], requestjson["assignedTo"])

            return {"success" : True, "message": "Acknowledgement successful"}
        except Exception as ex:
            logging.exception(ex)
            return {"success" : False, "message": "Acknowledgement successful"}

    def __get_attachments(self, ministryrequestid, emailschema, servicename):
        _messageattachmentlist = []
        _applicantcorrespondenceid = self.__getvaluefromschema(emailschema, "applicantcorrespondenceid")
        if (_applicantcorrespondenceid and templateconfig().isnotreceipt(servicename)):
            _messageattachmentlist = documentservice().getapplicantcorrespondenceattachmentsbyapplicantcorrespondenceid(_applicantcorrespondenceid)
        elif templateconfig().isnotreceipt(servicename) is not True:
            _messageattachmentlist = documentservice().getreceiptattachments(ministryrequestid, templateconfig().getattachmentcategory(servicename).lower())
        else:
            _messageattachmentlist = documentservice().getattachments(ministryrequestid, 'ministryrequest', templateconfig().getattachmentcategory(servicename).lower())
        return _messageattachmentlist   


    def __pre_send_correspondence_audit(self, requestid, ministryrequestid, emailschema, content, isnotreceipt, attachmentlist=None, recipient_email=None):
        print("============__pre_send_correspondence_audit================")
        _applicantcorrespondenceid = self.__getvaluefromschema(emailschema, "applicantcorrespondenceid")
        print(" _applicantcorrespondenceid :",_applicantcorrespondenceid)
        if _applicantcorrespondenceid and isnotreceipt:
            print("_applicantcorrespondenceid and isnotreceipt")
            # _applicantcorrespondence = applicantcorrespondenceservice().getapplicantcorrespondencelogbyid(_applicantcorrespondenceid)
            # print("fetch from _applicantcorrespondence : ",_applicantcorrespondence)
            # content_to_update = {"message" : content }
            # content_to_update.update(self._get_subjects_if_exist(_applicantcorrespondence))
            # print("content_to_update : ",content_to_update)
            return applicantcorrespondenceservice().updateapplicantcorrespondencelog(_applicantcorrespondenceid, {"message" : content })
        else:
            data = {
                "templateid": None,
                "correspondencemessagejson": {"message": content},
                "attachments": attachmentlist,
                "emails": [recipient_email] if recipient_email else []
            }
            print("check data : ",data)
            return applicantcorrespondenceservice().saveapplicantcorrespondencelog(requestid, ministryrequestid, data, 'system')
        

    def __upload_sent_email(self, servicekey, ministryrequestid, requestjson):
        try:
            _originalmsg = senderservice().read_outbox_as_bytes(servicekey, requestjson)
            if _originalmsg is not None:
                return self.__upload(templateconfig().getattachmentname(servicekey)+".eml",_originalmsg, ministryrequestid, requestjson, templateconfig().getattachmentcategory(servicekey+"-SUCCESSFUL"))
        except Exception as ex:
            logging.exception(ex)
        
    def __upload(self, filename, filebytes, ministryrequestid, requestjson, category):
        try:
            logging.info("Upload file for payload"+ json.dumps(requestjson))
            _response =  storageservice().uploadbytes(filename, filebytes, requestjson["bcgovcode"], requestjson["idNumber"])
            logging.info("Upload status for payload"+ json.dumps(_response))
            if _response["success"] == True:
                _documentschema = {"documents": [{"filename": _response["filename"], "documentpath": _response["documentpath"], "category": category}]}
                documentservice().createrequestdocument(ministryrequestid, _documentschema, "SYSTEM", "ministryrequest")
            return _response
        except Exception as ex:
            logging.exception(ex)
    
    def __getvaluefromschema(self, emailschema, property):
        return emailschema.get(property) if property in emailschema  else None
    
    def _get_subjects_if_exist(self, correspondence):
        result = {}
        if correspondence:
            if getattr(correspondence, "emailsubject", ''):
                result["emailsubject"] = correspondence.emailsubject
            if getattr(correspondence, "correspondencesubject", ''):
                result["correspondencesubject"] = correspondence.correspondencesubject
            if getattr(correspondence, "sentby", ''):
                result["sentby"] = correspondence.sentby
        return result
