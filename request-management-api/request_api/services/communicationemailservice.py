
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

class communicationemailservice:
    """ FOI Communication Service
    """
    
    def send(self, template, correspondencelog):
        try:
            messagepart = self.__getbody(correspondencelog)
            to = self.__getsenders(correspondencelog)
            ccemails = self.__getccemails(correspondencelog)
            attributes =  self.__getattributes(correspondencelog)
            subject = correspondencelog['emailsubject']
            messageattachmentlist = self.__getattachments(correspondencelog)
            _messagepart = templateservice().decorate_template(template, messagepart, attributes, correspondencelog)
            return senderservice().send(subject, _messagepart, messageattachmentlist, to, ccemails, correspondencelog.get('from_email', None))
        except Exception as ex:
            logging.exception(ex)

    def send_preview_email(self, template, correspondencelog):
        try:
            messagepart = self.__getbody(correspondencelog)
            to = self.__getsenders(correspondencelog)
            ccemails = self.__getccemails(correspondencelog)
            attributes =  self.__getattributes(correspondencelog)
            subject = correspondencelog['emailsubject']
            messageattachmentlist = self.__getattachments(correspondencelog)
            _messagepart = templateservice().decorate_template(template, messagepart, attributes, correspondencelog)
            return senderservice().send(subject, _messagepart, messageattachmentlist, to, ccemails, correspondencelog.get('from_email', None))
        except Exception as ex:
            logging.exception(ex)

    def __getbody(self,correspondencelog):
        data = json.loads(correspondencelog['correspondencemessagejson'])
        return data['emailhtml']
        
    def __getsenders(self,correspondencelog):
        return correspondencelog['emails']

    def __getccemails(self,correspondencelog):
        if 'ccemails' in correspondencelog:
            return correspondencelog['ccemails']
        else:
            return None
        
    def __getattachments(self, correspondencelog):
        return correspondencelog['attachments']
    
    def __getattributes(self, correspondencelog):
        return correspondencelog["attributes"][0]


    
    
 