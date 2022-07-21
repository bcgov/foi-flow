
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
from request_api.services.requestservice import requestservice
from request_api.services.email.templates.templateservice import templateservice
from request_api.services.email.templates.templateconfig import templateconfig
from request_api.services.email.senderservice import senderservice
import weasyprint

class emailservice:
    """ FOI Email Service
    """
  
    def send_payonline(self, requestid, ministryrequestid, requestjson):
        #Get FOI Request
        if requestjson is not None:
            _templatename = templateconfig().gettemplatename("PAYONLINE")
            _messagepart = templateservice().generatetemplate(_templatename, requestjson)
            _messageattachmentlist = documentservice().getattachments(ministryrequestid, 'ministryrequest','feeassessed-onhold')
            senderservice().send(_messagepart, _messageattachmentlist, requestjson)
        #template
        #senderservice.send(metadata, template, attachments)
        

        
    def acknowledge(self, requestid):
        try:
            print("test")
            #inboxservice._get_failure
            #storageservice().uploadbytes("email2.pdf",pdf_content)
            
            #storageservice().uploadbytes("email3.eml",message.obj.__bytes__())

        except Exception as ex:
            logging.error(ex)
        logging.debug('Read email for '+requestid)
        