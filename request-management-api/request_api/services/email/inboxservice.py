
from os import stat
import imaplib
import os
from imap_tools import MailBox, AND
import weasyprint
import logging

class inboxservice:
    """ FOI Email Inbox Service
    
    This service wraps up inbox operations.

    """

    def get_failure_deliverystatus_as_pdf(self, text):
        message = self._get_deliverystatus_by_text(text)
        if message is not None:
            pdf_content = weasyprint.HTML(string=message.html).write_pdf()
            return pdf_content
        return None
    
    def get_failure_deliverystatus_as_eml(self, text):    
        message = self._get_deliverystatus_by_text(text)
        if message is not None:
            return message.obj.__bytes__()
        return None
    
    def _get_deliverystatus_by_text(self, text):
        try:
            mailbox = MailBox(os.getenv('EMAIL_SERVER_IMAP'))
            mailbox.login(os.getenv('EMAIL_SRUSERID'), os.getenv('EMAIL_SRPWD'))
            messages = mailbox.fetch(criteria=AND(subject='Delivery Status Notification')) 
            for message in messages:
                if text in message.text:
                    return message
            return None     
        except Exception as ex:
            logging.error(ex)
        logging.debug('Read email for '+text)
                
