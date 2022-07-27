
from os import stat
import imaplib
import os
from imap_tools import MailBox, AND
import weasyprint
import logging
import email

MAIL_SERVER_IMAP = os.getenv('EMAIL_SERVER_IMAP')
MAIL_SRV_USERID = os.getenv('EMAIL_SRUSERID')
MAIL_SRV_PASSWORD = os.getenv('EMAIL_SRPWD')
MAIL_DELIVERY_FAILURE_TXT = "Delivery Status Notification"
class inboxservice:
    
    """ FOI Email Inbox Service
    
    This service wraps up inbox operations.

    """

    def get_failure_deliverystatus_as_pdf(self, subject, email):
        message = self._get_deliverystatus_by_text(MAIL_DELIVERY_FAILURE_TXT,subject, email)
        if message is not None:
            pdf_content = weasyprint.HTML(string=message.html).write_pdf()
            return {"success" : False, "message": "Unable to send", "content": pdf_content}
        return {"success" : True, "message": "Sent successfully", "content": None}
    
    def get_failure_deliverystatus_as_eml(self, subject, email):    
        message = self._get_deliverystatus_by_text(MAIL_DELIVERY_FAILURE_TXT, subject, email)
        if message is not None:
            return {"success" : False, "message": "Unable to send", "content": message.obj.__bytes__()}
        return {"success" : True, "message": "Sent successfully", "content": None}
    
    def _get_deliverystatus_by_text(self, subject, msgkey, text):
        try:
            mailbox = MailBox(MAIL_SERVER_IMAP)
            mailbox.login(MAIL_SRV_USERID, MAIL_SRV_PASSWORD)
            messages = mailbox.fetch(criteria=AND(subject=subject, text=text), reverse = True) 
            for message in messages:
                email_message = email.message_from_bytes(message.obj.__bytes__()).as_string()
                if text in email_message and msgkey in email_message:
                    return message
            return None
        except Exception as ex:
            logging.exception(ex)
        logging.debug('Read email for '+text)
                
