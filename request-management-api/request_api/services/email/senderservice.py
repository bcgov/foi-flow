
from audioop import reverse
from os import stat
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from request_api.services.email.templates.templateconfig import templateconfig
import imaplib
from imap_tools import MailBox, AND
import logging
import email
import json
from request_api.services.external.storageservice import storageservice
from request_api.models.default_method_result import DefaultMethodResult


MAIL_SERVER_SMTP = os.getenv('EMAIL_SERVER_SMTP')
MAIL_SERVER_SMTP_PORT = os.getenv('EMAIL_SERVER_SMTP_PORT')
MAIL_SERVER_IMAP = os.getenv('EMAIL_SERVER_IMAP')
MAIL_SRV_USERID = os.getenv('EMAIL_SRUSERID')
MAIL_SRV_PASSWORD = os.getenv('EMAIL_SRPWD')
MAIL_FROM_ADDRESS = os.getenv('EMAIL_SENDER_ADDRESS')
MAIL_FOLDER_OUTBOX = os.getenv('EMAIL_FOLDER_OUTBOX')
MAIL_FOLDER_INBOX = os.getenv('EMAIL_FOLDER_INBOX')
class senderservice:
    """ Email Sender service

    This service wraps up send operations.

    """

    def send_by_request(self, subject, content, _messageattachmentlist, requestjson):
        return self.send(subject, content, _messageattachmentlist, requestjson["email"])

    def send(self, subject, content, _messageattachmentlist, emails):
        logging.debug("Begin: Send email for request ")
        
        msg = MIMEMultipart()
        msg['From'] = MAIL_FROM_ADDRESS
        msg['To'] = ",".join(emails)
        msg['Subject'] = subject
        part = MIMEText(content, "html")
        msg.attach(part)
        # Add Attachment and Set mail headers
        for attachment in _messageattachmentlist:
            file = storageservice().download(attachment['url'])
            part = MIMEBase("application", "octet-stream")
            part.set_payload(file.content)
            encoders.encode_base64(part)
            part.add_header(
            "Content-Disposition",
            "attachment", filename= attachment.get('filename')
            )
            msg.attach(part)
        try:
            with smtplib.SMTP(MAIL_SERVER_SMTP,  MAIL_SERVER_SMTP_PORT) as smtpobj:
                smtpobj.ehlo()
                smtpobj.starttls()
                smtpobj.ehlo()
                #smtpobj.login(MAIL_SRV_USERID, MAIL_SRV_PASSWORD)
                smtpobj.sendmail(msg['From'],  msg['To'], msg.as_string())
                smtpobj.quit()
                logging.debug("End: Send email for request")
                return DefaultMethodResult(True,'Sent successfully', -1)    
        except Exception as e:
            logging.exception(e)
        return DefaultMethodResult(False,'Unable to send', -1)    
    

    def read_outbox_as_bytes(self, servicekey, requestjson):
        logging.debug("Begin: Read sent item for request = "+json.dumps(requestjson))
        _subject = templateconfig().getsubject(servicekey, requestjson)
        try:
            mailbox = MailBox(MAIL_SERVER_IMAP)
            mailbox.login(MAIL_SRV_USERID, MAIL_SRV_PASSWORD)
            #Navigate to sent Items
            is_exists = mailbox.folder.exists(MAIL_FOLDER_OUTBOX)
            if is_exists == True:
                mailbox.folder.set(MAIL_FOLDER_OUTBOX)
            messages = mailbox.fetch(criteria=AND(subject=_subject), reverse = True) 
            for message in messages:
                logging.debug("End: Read sent item for request = "+json.dumps(requestjson))
                return message.obj.__bytes__()
        except Exception as ex:
            logging.exception(ex)
        logging.debug("End: Read sent item for request = "+json.dumps(requestjson))
        return None     
        
           
