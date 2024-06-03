
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
import logging

class communicationservice:
    """ FOI Communication Service
    """

    

    def send(self, correspondencelog, userid):
        try:
            messagepart = self.__getbody(correspondencelog)
            to = self.__getsenders(correspondencelog)
            subject = 'Dummy'
            #messageattachmentlist = self.__get_attachments(ministryrequestid, emailschema, servicename)
            return senderservice().send_email(subject,messagepart, None, to)
        except Exception as ex:
            logging.exception(ex)

    
    def __getbody(self,correspondencelog):
        data = json.loads(correspondencelog)
        return data['emailhtml']
        
    def __getsenders(self,correspondencelog):
        return correspondencelog['emails']
        


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


    
    
 