
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


class emailservice:
    """ FOI Email Service
    """
  
    def send_payonline(self, servicekey, ministryrequestid, requestjson):
        try:
            _templatename = templateconfig().gettemplatename(servicekey)
            _messagepart = templateservice().generatetemplate(_templatename, requestjson)
            _messageattachmentlist = documentservice().getattachments(ministryrequestid, 'ministryrequest','feeassessed-onhold')
            return senderservice().send(servicekey, _messagepart, _messageattachmentlist, requestjson)
        except Exception as ex:
            logging.exception(ex)
        
        

    def acknowledge(self, servicekey, ministryrequestid, requestjson):
        try:
            self.__upload_sent_email(servicekey, ministryrequestid, requestjson)
            ackresponse = inboxservice().get_failure_deliverystatus_as_eml(templateconfig().getsubject(servicekey, requestjson), requestjson["email"])
            if ackresponse["success"] == False:
                self.__upload(templateconfig().getattachmentname("PAYONLINE-SEND-FAILURE")+".eml", ackresponse["content"], ministryrequestid, requestjson)   
                eventservice().posteventforemailfailure(ministryrequestid, "ministryrequest", templateconfig().getstage(servicekey), ackresponse["reason"], requestjson["assignedto"])
            return {"success" : True, "message": "Acknowledgement successful"}
        except Exception as ex:
            logging.exception(ex)
            return {"success" : False, "message": "Acknowledgement successful"}
    
 
    def __upload_sent_email(self, servicekey, ministryrequestid, requestjson):
        try:
            _originalmsg = senderservice().read_outbox_as_bytes(servicekey, requestjson)
            if _originalmsg is not None:
                return self.__upload(templateconfig().getattachmentname(servicekey)+".eml",_originalmsg, ministryrequestid, requestjson)
        except Exception as ex:
            logging.exception(ex)
        
    def __upload(self, filename, filebytes, ministryrequestid, requestjson):
        try:
            logging.info("Upload file for payload"+ json.dumps(requestjson))
            _response =  storageservice().uploadbytes(filename, filebytes, requestjson["bcgovcode"], requestjson["idNumber"])
            logging.info("Upload status for payload"+ json.dumps(_response))
            if _response["success"] == True:
                _documentschema = {"documents": [{"filename": _response["filename"], "documentpath": _response["documentpath"], "category": "feeassessed-onhold"}]}
                documentservice().createrequestdocument(ministryrequestid, _documentschema, "SYSTEM", "ministryrequest")
            return _response
        except Exception as ex:
            logging.exception(ex)
            
