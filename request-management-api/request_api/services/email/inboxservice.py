
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
            return {"success" : False, "message": "Unable to send", "content": pdf_content, "reason": message["reason"]}
        return {"success" : True, "message": "Sent successfully", "content": None, "reason": None}
    
    def get_failure_deliverystatus_as_eml(self, subject, email):    
        message = self._get_deliverystatus_by_text(MAIL_DELIVERY_FAILURE_TXT, subject, email)
        if message is not None:
            return {"success" : False, "message": "Unable to send", "content": message["content"].obj.__bytes__(), "reason": message["reason"]}
        return {"success" : True, "message": "Sent successfully", "content": None,  "reason": None}
    
    def _get_deliverystatus_by_text(self, subject, msgkey, text):
        try:
            mailbox = MailBox(MAIL_SERVER_IMAP)
            mailbox.login(MAIL_SRV_USERID, MAIL_SRV_PASSWORD)
            messages = mailbox.fetch(criteria=AND(subject=subject, text=text), reverse = True) 
            for message in messages:
                email_message = email.message_from_bytes(message.obj.__bytes__()).as_string()
                if text in email_message and msgkey in email_message:
                    _reasoncode = 500
                    for code in self.__getmanagederrorcodes():
                        if code in message.text:
                            _reasoncode = code   
                    return {"code": _reasoncode, "reason": self.__getreason(_reasoncode),  "content": message}
            return None
        except Exception as ex:
            logging.exception(ex)
        logging.debug('Read email for '+text)
                

    def __getmanagederrorcodes(self):
        return ["541", "550", "550 5.1.1", "551", "552"]
    
    def __getreason(self, code):
        if code == "541":
            return "Message rejected by the recipient address"
        elif code == "550 5.1.1":
            return "The email account that you tried to reach does not exist. Please try double-checking the recipient's email address for typos or unnecessary spaces"
        elif code == "550":
            return "Requested command failed because the user’s mailbox was unavailable, or the receiving server rejected the message because it was likely spam"
        elif code == "551":    
            return "Intended recipient mailbox isn't available on the receiving server"
        elif code == "552":
            return "Message wasn't sent because the recipient mailbox doesn't have enough storage"
        else:
            return "Server could not complete the action"